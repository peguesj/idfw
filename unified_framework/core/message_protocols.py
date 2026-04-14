"""
Message Protocols for IDFWU Unified Framework
Linear Project: 4d649a6501f7

Defines standardized message protocols for inter-agent communication including:
- Message routing and delivery
- Event-driven notifications
- Callback mechanisms
- Result streaming
- Error handling and recovery
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Awaitable, Union
from uuid import uuid4

import redis
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Standard message types for agent communication"""
    
    # Agent lifecycle
    AGENT_REGISTER = "agent_register"
    AGENT_HEARTBEAT = "agent_heartbeat"
    AGENT_SHUTDOWN = "agent_shutdown"
    
    # Task management
    TASK_REQUEST = "task_request"
    TASK_ASSIGNMENT = "task_assignment"
    TASK_UPDATE = "task_update"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    TASK_CANCELLED = "task_cancelled"
    
    # Communication
    DIRECT_MESSAGE = "direct_message"
    BROADCAST = "broadcast"
    REQUEST = "request"
    RESPONSE = "response"
    
    # Monitoring and alerts
    STATUS_UPDATE = "status_update"
    HEALTH_CHECK = "health_check"
    RESOURCE_ALERT = "resource_alert"
    ERROR_REPORT = "error_report"
    
    # Coordination
    SYNC_REQUEST = "sync_request"
    DEPENDENCY_RESOLVED = "dependency_resolved"
    COORDINATION_EVENT = "coordination_event"


class DeliveryMode(str, Enum):
    """Message delivery modes"""
    FIRE_AND_FORGET = "fire_and_forget"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"
    REQUEST_REPLY = "request_reply"


class ProtocolMessage(BaseModel):
    """Standard protocol message structure"""
    
    # Message identification
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: MessageType
    
    # Routing
    sender_id: str
    receiver_id: Optional[str] = None  # None for broadcast
    channel: Optional[str] = None
    
    # Content
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Protocol control
    delivery_mode: DeliveryMode = DeliveryMode.FIRE_AND_FORGET
    ttl: Optional[int] = None  # Time to live in seconds
    priority: int = Field(default=5, ge=0, le=10)  # 0=highest, 10=lowest
    
    # Correlation
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    # Delivery tracking
    delivery_count: int = Field(default=0)
    max_retries: int = Field(default=3)


class MessageHandler(ABC):
    """Abstract base class for message handlers"""
    
    @abstractmethod
    async def handle(self, message: ProtocolMessage) -> Optional[ProtocolMessage]:
        """Handle a message and optionally return a response"""
        pass
    
    @abstractmethod
    def can_handle(self, message_type: MessageType) -> bool:
        """Check if this handler can process the message type"""
        pass


class MessageRouter:
    """Routes messages between agents and handles delivery"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.handlers: Dict[MessageType, List[MessageHandler]] = {}
        self.middleware: List[Callable] = []
        self.delivery_callbacks: Dict[str, Callable] = {}
        
    def register_handler(self, message_type: MessageType, handler: MessageHandler):
        """Register a message handler"""
        if message_type not in self.handlers:
            self.handlers[message_type] = []
        self.handlers[message_type].append(handler)
        logger.debug(f"Registered handler for {message_type}")
    
    def add_middleware(self, middleware: Callable):
        """Add middleware for message processing"""
        self.middleware.append(middleware)
    
    async def send_message(self, message: ProtocolMessage) -> bool:
        """Send a message through the routing system"""
        try:
            # Apply middleware
            for middleware in self.middleware:
                message = await middleware(message)
                if not message:
                    return False
            
            # Set expiration if TTL is specified
            if message.ttl:
                message.expires_at = datetime.utcnow().replace(
                    second=0, microsecond=0
                ) + timedelta(seconds=message.ttl)
            
            # Route message
            if message.receiver_id:
                # Direct message
                await self._route_direct(message)
            else:
                # Broadcast message
                await self._route_broadcast(message)
            
            # Handle delivery confirmation
            if message.delivery_mode in [DeliveryMode.AT_LEAST_ONCE, DeliveryMode.EXACTLY_ONCE]:
                await self._track_delivery(message)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message {message.id}: {e}")
            return False
    
    async def _route_direct(self, message: ProtocolMessage):
        """Route message to specific agent"""
        channel = f"idfwu:agent:{message.receiver_id}"
        message_json = message.json()
        
        await self.redis.lpush(channel, message_json)
        logger.debug(f"Routed message {message.id} to {message.receiver_id}")
    
    async def _route_broadcast(self, message: ProtocolMessage):
        """Broadcast message to all agents"""
        channel = f"idfwu:broadcast:{message.type.value}"
        message_json = message.json()
        
        await self.redis.publish(channel, message_json)
        logger.debug(f"Broadcast message {message.id} of type {message.type}")
    
    async def _track_delivery(self, message: ProtocolMessage):
        """Track message delivery for reliable delivery modes"""
        tracking_key = f"idfwu:delivery:{message.id}"
        tracking_data = {
            "message_id": message.id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "delivery_mode": message.delivery_mode.value,
            "created_at": message.created_at.isoformat(),
            "status": "sent"
        }
        
        # Store with TTL
        ttl = message.ttl or 3600  # Default 1 hour
        await self.redis.setex(tracking_key, ttl, json.dumps(tracking_data))
    
    async def process_message(self, message: ProtocolMessage) -> Optional[ProtocolMessage]:
        """Process an incoming message through registered handlers"""
        try:
            # Check expiration
            if message.expires_at and datetime.utcnow() > message.expires_at:
                logger.warning(f"Message {message.id} expired, discarding")
                return None
            
            # Find handlers
            handlers = self.handlers.get(message.type, [])
            
            if not handlers:
                logger.warning(f"No handlers found for message type {message.type}")
                return None
            
            # Process through handlers
            response = None
            for handler in handlers:
                if handler.can_handle(message.type):
                    try:
                        handler_response = await handler.handle(message)
                        if handler_response and not response:
                            response = handler_response
                    except Exception as e:
                        logger.error(f"Handler error for message {message.id}: {e}")
            
            # Send delivery confirmation if required
            if message.delivery_mode != DeliveryMode.FIRE_AND_FORGET:
                await self._confirm_delivery(message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message {message.id}: {e}")
            return None
    
    async def _confirm_delivery(self, message: ProtocolMessage):
        """Send delivery confirmation"""
        confirmation = ProtocolMessage(
            type=MessageType.STATUS_UPDATE,
            sender_id="message_router",
            receiver_id=message.sender_id,
            payload={
                "status": "delivered",
                "original_message_id": message.id,
                "delivered_at": datetime.utcnow().isoformat()
            }
        )
        
        await self.send_message(confirmation)


class EventBus:
    """Event-driven notification system"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Dict[str, Any]] = []
        self.max_history = 1000
    
    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to event type: {event_type}")
    
    async def publish_event(self, event_type: str, event_data: Dict[str, Any]):
        """Publish an event"""
        event = {
            "id": str(uuid4()),
            "type": event_type,
            "data": event_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Notify local subscribers
        subscribers = self.subscribers.get(event_type, [])
        for callback in subscribers:
            try:
                await callback(event_data)
            except Exception as e:
                logger.error(f"Error in event callback for {event_type}: {e}")
        
        # Publish to Redis for distributed subscribers
        channel = f"idfwu:events:{event_type}"
        await self.redis.publish(channel, json.dumps(event))
        
        logger.debug(f"Published event {event['id']} of type {event_type}")
    
    async def listen_for_events(self, event_types: List[str]):
        """Listen for distributed events"""
        pubsub = self.redis.pubsub()
        
        # Subscribe to channels
        for event_type in event_types:
            channel = f"idfwu:events:{event_type}"
            await pubsub.subscribe(channel)
        
        # Process messages
        async for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    event = json.loads(message['data'])
                    event_type = event['type']
                    event_data = event['data']
                    
                    # Notify local subscribers
                    subscribers = self.subscribers.get(event_type, [])
                    for callback in subscribers:
                        try:
                            await callback(event_data)
                        except Exception as e:
                            logger.error(f"Error processing distributed event {event_type}: {e}")
                            
                except Exception as e:
                    logger.error(f"Error parsing event message: {e}")


class CallbackManager:
    """Manages callback mechanisms for asynchronous operations"""
    
    def __init__(self):
        self.pending_callbacks: Dict[str, Callable] = {}
        self.callback_timeouts: Dict[str, float] = {}
        self.default_timeout = 300  # 5 minutes
    
    def register_callback(self, correlation_id: str, callback: Callable, timeout: Optional[int] = None):
        """Register a callback for a correlation ID"""
        self.pending_callbacks[correlation_id] = callback
        self.callback_timeouts[correlation_id] = time.time() + (timeout or self.default_timeout)
        logger.debug(f"Registered callback for correlation ID: {correlation_id}")
    
    async def trigger_callback(self, correlation_id: str, data: Any) -> bool:
        """Trigger a callback with response data"""
        if correlation_id in self.pending_callbacks:
            callback = self.pending_callbacks.pop(correlation_id)
            self.callback_timeouts.pop(correlation_id, None)
            
            try:
                await callback(data)
                logger.debug(f"Triggered callback for correlation ID: {correlation_id}")
                return True
            except Exception as e:
                logger.error(f"Error in callback for {correlation_id}: {e}")
                return False
        else:
            logger.warning(f"No callback found for correlation ID: {correlation_id}")
            return False
    
    async def cleanup_expired_callbacks(self):
        """Clean up expired callbacks"""
        current_time = time.time()
        expired_ids = []
        
        for correlation_id, timeout in self.callback_timeouts.items():
            if current_time > timeout:
                expired_ids.append(correlation_id)
        
        for correlation_id in expired_ids:
            self.pending_callbacks.pop(correlation_id, None)
            self.callback_timeouts.pop(correlation_id, None)
            logger.warning(f"Callback expired for correlation ID: {correlation_id}")


class ResultStreamer:
    """Streams results from long-running operations"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.streams: Dict[str, Dict[str, Any]] = {}
    
    async def create_stream(self, stream_id: str, metadata: Dict[str, Any] = None) -> str:
        """Create a new result stream"""
        stream_key = f"idfwu:stream:{stream_id}"
        
        stream_info = {
            "id": stream_id,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "status": "active"
        }
        
        await self.redis.hset(f"{stream_key}:info", mapping=stream_info)
        self.streams[stream_id] = stream_info
        
        logger.debug(f"Created result stream: {stream_id}")
        return stream_id
    
    async def add_result(self, stream_id: str, result: Dict[str, Any]):
        """Add a result to the stream"""
        stream_key = f"idfwu:stream:{stream_id}"
        
        result_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "data": json.dumps(result)
        }
        
        await self.redis.xadd(stream_key, result_entry)
        logger.debug(f"Added result to stream {stream_id}")
    
    async def read_results(self, stream_id: str, start: str = "0", count: Optional[int] = None) -> List[Dict[str, Any]]:
        """Read results from a stream"""
        stream_key = f"idfwu:stream:{stream_id}"
        
        try:
            # Read from Redis stream
            args = [stream_key, start]
            if count:
                args.extend(["COUNT", count])
            
            entries = await self.redis.xread({stream_key: start}, count=count)
            
            results = []
            for stream, messages in entries:
                for message_id, fields in messages:
                    result = {
                        "id": message_id,
                        "timestamp": fields.get("timestamp"),
                        "data": json.loads(fields.get("data", "{}"))
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error reading from stream {stream_id}: {e}")
            return []
    
    async def close_stream(self, stream_id: str):
        """Close a result stream"""
        if stream_id in self.streams:
            self.streams[stream_id]["status"] = "closed"
            self.streams[stream_id]["closed_at"] = datetime.utcnow().isoformat()
            
            # Update Redis
            stream_key = f"idfwu:stream:{stream_id}"
            await self.redis.hset(f"{stream_key}:info", "status", "closed")
            await self.redis.hset(f"{stream_key}:info", "closed_at", self.streams[stream_id]["closed_at"])
            
            logger.debug(f"Closed result stream: {stream_id}")


class CommunicationProtocol:
    """Main communication protocol coordinator"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.router = MessageRouter(redis_client)
        self.event_bus = EventBus(redis_client)
        self.callback_manager = CallbackManager()
        self.result_streamer = ResultStreamer(redis_client)
        
        # Start background tasks
        asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            try:
                await self.callback_manager.cleanup_expired_callbacks()
                await asyncio.sleep(60)  # Run every minute
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(10)
    
    async def send_request_reply(self, message: ProtocolMessage, timeout: int = 30) -> Optional[ProtocolMessage]:
        """Send a request and wait for reply"""
        correlation_id = str(uuid4())
        message.correlation_id = correlation_id
        message.delivery_mode = DeliveryMode.REQUEST_REPLY
        
        # Set up callback
        response_future = asyncio.Future()
        
        async def response_callback(response_data):
            if not response_future.done():
                response_future.set_result(response_data)
        
        self.callback_manager.register_callback(correlation_id, response_callback, timeout)
        
        # Send message
        success = await self.router.send_message(message)
        if not success:
            return None
        
        # Wait for response
        try:
            response_data = await asyncio.wait_for(response_future, timeout=timeout)
            return ProtocolMessage(**response_data)
        except asyncio.TimeoutError:
            logger.warning(f"Request {message.id} timed out after {timeout}s")
            return None
    
    def register_message_handler(self, message_type: MessageType, handler: MessageHandler):
        """Register a message handler"""
        self.router.register_handler(message_type, handler)
    
    def subscribe_to_event(self, event_type: str, callback: Callable):
        """Subscribe to an event"""
        self.event_bus.subscribe(event_type, callback)
    
    async def publish_event(self, event_type: str, event_data: Dict[str, Any]):
        """Publish an event"""
        await self.event_bus.publish_event(event_type, event_data)
    
    async def create_result_stream(self, stream_id: str, metadata: Dict[str, Any] = None) -> str:
        """Create a result stream"""
        return await self.result_streamer.create_stream(stream_id, metadata)
    
    async def stream_result(self, stream_id: str, result: Dict[str, Any]):
        """Add result to stream"""
        await self.result_streamer.add_result(stream_id, result)