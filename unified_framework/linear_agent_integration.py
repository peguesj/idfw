#!/usr/bin/env python3
"""
Linear Agent Integration Framework for IDFWU

Provides comprehensive integration with Linear's AI Agent platform using OAuth2 authentication,
GraphQL API access, and automated agent lifecycle management.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from urllib.parse import urlparse, parse_qs
import httpx
import jwt
from pydantic import BaseModel, Field, validator


# Configuration Models
class LinearOAuthConfig(BaseModel):
    """OAuth2 configuration for Linear API access"""
    client_id: str
    client_secret: Optional[str] = None
    redirect_uri: Optional[str] = None
    scopes: List[str] = Field(default_factory=lambda: ["read", "write"])
    actor_mode: str = Field(default="app", pattern="^(user|app)$")


class LinearGraphQLConfig(BaseModel):
    """GraphQL API configuration"""
    endpoint: str = "https://api.linear.app/graphql"
    requests_per_hour: int = Field(default=500, ge=1, le=1500)
    complexity_points_per_hour: int = Field(default=200000, ge=1000, le=250000)
    max_complexity: int = Field(default=1000, ge=1, le=10000)
    timeout_ms: int = Field(default=30000, ge=1000, le=300000)


class LinearSessionConfig(BaseModel):
    """Session management configuration"""
    token_refresh: bool = True
    session_timeout: int = Field(default=86400, ge=3600, le=86400)
    max_retries: int = Field(default=3, ge=0, le=10)
    backoff_factor: float = Field(default=2.0, ge=1.0, le=5.0)
    initial_delay: int = Field(default=1000, ge=100, le=10000)


class LinearAgentCapabilities(BaseModel):
    """Agent capabilities configuration"""
    issue_management: bool = True
    comment_management: bool = True
    project_management: bool = False
    team_management: bool = False
    webhook_handling: bool = True
    real_time_sync: bool = True


class LinearAgentConfig(BaseModel):
    """Complete Linear agent configuration"""
    agent_id: str = Field(pattern="^linear-agent-[a-z0-9-]+$")
    oauth_config: LinearOAuthConfig
    graphql_config: LinearGraphQLConfig = LinearGraphQLConfig()
    session_config: LinearSessionConfig = LinearSessionConfig()
    capabilities: LinearAgentCapabilities = LinearAgentCapabilities()
    workspace_id: Optional[str] = None
    team_filters: List[str] = Field(default_factory=list)
    project_filters: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Status and State Models
class AgentStatus(str, Enum):
    """Agent status enumeration"""
    INITIALIZING = "initializing"
    AUTHENTICATING = "authenticating"
    READY = "ready"
    ACTIVE = "active"
    ERROR = "error"
    STOPPED = "stopped"


class SessionStatus(str, Enum):
    """Session status enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    EXPIRED = "expired"
    ERROR = "error"


@dataclass
class RateLimit:
    """Rate limiting state"""
    requests_remaining: int
    complexity_remaining: int
    reset_time: datetime
    current_window_start: datetime


@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    requests_made: int = 0
    complexity_used: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    average_response_time: float = 0.0
    last_activity: Optional[datetime] = None
    uptime_seconds: float = 0.0
    error_rate: float = 0.0


# Exception Classes
class LinearAgentError(Exception):
    """Base exception for Linear agent operations"""
    pass


class AuthenticationError(LinearAgentError):
    """Authentication-related errors"""
    pass


class RateLimitError(LinearAgentError):
    """Rate limiting errors"""
    pass


class APIError(LinearAgentError):
    """Linear API errors"""
    pass


class ConfigurationError(LinearAgentError):
    """Configuration errors"""
    pass


# Core Linear Agent Implementation
class LinearAgent:
    """
    Linear AI Agent with full OAuth2 authentication, GraphQL API access,
    and automated lifecycle management.
    """
    
    def __init__(self, config: LinearAgentConfig):
        self.config = config
        self.status = AgentStatus.INITIALIZING
        self.session_status = SessionStatus.DISCONNECTED
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.rate_limit = RateLimit(
            requests_remaining=config.graphql_config.requests_per_hour,
            complexity_remaining=config.graphql_config.complexity_points_per_hour,
            reset_time=datetime.now() + timedelta(hours=1),
            current_window_start=datetime.now()
        )
        self.metrics = AgentMetrics()
        self.logger = logging.getLogger(f"linear_agent.{config.agent_id}")
        self.client: Optional[httpx.AsyncClient] = None
        self.webhook_handlers: Dict[str, Callable] = {}
        self.start_time = datetime.now()
        
    async def initialize(self) -> bool:
        """Initialize the Linear agent"""
        try:
            self.logger.info(f"Initializing Linear agent {self.config.agent_id}")
            self.status = AgentStatus.INITIALIZING
            
            # Create HTTP client
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.graphql_config.timeout_ms / 1000),
                headers={
                    "User-Agent": f"IDFWU-LinearAgent/{self.config.agent_id}",
                    "Content-Type": "application/json"
                }
            )
            
            # Authenticate
            if not await self._authenticate():
                raise AuthenticationError("Failed to authenticate with Linear API")
            
            # Validate configuration
            if not await self._validate_configuration():
                raise ConfigurationError("Invalid agent configuration")
            
            self.status = AgentStatus.READY
            self.logger.info(f"Linear agent {self.config.agent_id} initialized successfully")
            return True
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"Failed to initialize agent: {e}")
            return False
    
    async def _authenticate(self) -> bool:
        """Handle OAuth2 authentication flow"""
        try:
            self.session_status = SessionStatus.CONNECTING
            
            if self.config.oauth_config.client_secret:
                # Use client credentials flow for server-to-server
                success = await self._client_credentials_flow()
            else:
                # Use authorization code flow (requires user interaction)
                success = await self._authorization_code_flow()
            
            if success:
                self.session_status = SessionStatus.AUTHENTICATED
                self.logger.info("Successfully authenticated with Linear API")
                return True
            else:
                self.session_status = SessionStatus.ERROR
                return False
                
        except Exception as e:
            self.session_status = SessionStatus.ERROR
            self.logger.error(f"Authentication failed: {e}")
            return False
    
    async def _client_credentials_flow(self) -> bool:
        """OAuth2 client credentials flow for app tokens"""
        try:
            response = await self.client.post(
                "https://api.linear.app/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.config.oauth_config.client_id,
                    "client_secret": self.config.oauth_config.client_secret,
                    "scope": " ".join(self.config.oauth_config.scopes)
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                # Client credentials tokens are valid for 30 days
                self.token_expires_at = datetime.now() + timedelta(days=30)
                return True
            else:
                self.logger.error(f"Token request failed: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Client credentials flow failed: {e}")
            return False
    
    async def _authorization_code_flow(self) -> bool:
        """OAuth2 authorization code flow (requires user interaction)"""
        # This would require a web server to handle the redirect
        # For now, we'll assume the token is provided externally
        self.logger.warning("Authorization code flow requires external token provision")
        return False
    
    async def _validate_configuration(self) -> bool:
        """Validate agent configuration against Linear API"""
        try:
            # Test API access with a simple query
            query = """
            query {
                viewer {
                    id
                    name
                    email
                }
            }
            """
            
            result = await self._execute_graphql_query(query)
            if result and "data" in result and "viewer" in result["data"]:
                self.logger.info(f"Configuration validated for user: {result['data']['viewer']['name']}")
                return True
            else:
                self.logger.error("Failed to validate configuration")
                return False
                
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    async def _execute_graphql_query(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict]:
        """Execute GraphQL query with rate limiting and error handling"""
        try:
            # Check rate limits
            if not self._check_rate_limits():
                raise RateLimitError("Rate limit exceeded")
            
            # Prepare request
            payload = {"query": query}
            if variables:
                payload["variables"] = variables
            
            # Execute request
            start_time = time.time()
            response = await self.client.post(
                self.config.graphql_config.endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response_time = time.time() - start_time
            
            # Update metrics
            self._update_metrics(response_time, response.status_code == 200)
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    self.logger.warning(f"GraphQL errors: {result['errors']}")
                return result
            elif response.status_code == 429:
                # Rate limited
                self._handle_rate_limit(response)
                raise RateLimitError("Rate limit exceeded")
            else:
                self.logger.error(f"GraphQL request failed: {response.status_code} {response.text}")
                raise APIError(f"API request failed: {response.status_code}")
                
        except Exception as e:
            self._update_metrics(0, False)
            raise e
    
    def _check_rate_limits(self) -> bool:
        """Check if request can be made within rate limits"""
        now = datetime.now()
        
        # Reset rate limit window if expired
        if now >= self.rate_limit.reset_time:
            self.rate_limit.requests_remaining = self.config.graphql_config.requests_per_hour
            self.rate_limit.complexity_remaining = self.config.graphql_config.complexity_points_per_hour
            self.rate_limit.reset_time = now + timedelta(hours=1)
            self.rate_limit.current_window_start = now
        
        return self.rate_limit.requests_remaining > 0
    
    def _handle_rate_limit(self, response: httpx.Response):
        """Handle rate limit response from API"""
        # Parse rate limit headers if available
        reset_header = response.headers.get("X-RateLimit-Reset")
        if reset_header:
            self.rate_limit.reset_time = datetime.fromtimestamp(int(reset_header))
        
        remaining_header = response.headers.get("X-RateLimit-Remaining")
        if remaining_header:
            self.rate_limit.requests_remaining = int(remaining_header)
    
    def _update_metrics(self, response_time: float, success: bool):
        """Update agent performance metrics"""
        self.metrics.requests_made += 1
        self.metrics.last_activity = datetime.now()
        self.metrics.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
        
        if success:
            self.metrics.successful_operations += 1
        else:
            self.metrics.failed_operations += 1
        
        # Update average response time
        total_ops = self.metrics.successful_operations + self.metrics.failed_operations
        self.metrics.average_response_time = (
            (self.metrics.average_response_time * (total_ops - 1) + response_time) / total_ops
        )
        
        # Update error rate
        if total_ops > 0:
            self.metrics.error_rate = self.metrics.failed_operations / total_ops
        
        # Update rate limit counters
        self.rate_limit.requests_remaining -= 1
    
    # Agent Operations
    async def create_issue(self, title: str, description: str, team_id: str, **kwargs) -> Optional[Dict]:
        """Create a new Linear issue"""
        if not self.config.capabilities.issue_management:
            raise ConfigurationError("Issue management capability not enabled")
        
        mutation = """
        mutation CreateIssue($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    description
                    url
                }
            }
        }
        """
        
        variables = {
            "input": {
                "title": title,
                "description": description,
                "teamId": team_id,
                **kwargs
            }
        }
        
        try:
            result = await self._execute_graphql_query(mutation, variables)
            if result and "data" in result and result["data"]["issueCreate"]["success"]:
                issue = result["data"]["issueCreate"]["issue"]
                self.logger.info(f"Created issue {issue['identifier']}: {issue['title']}")
                return issue
            else:
                self.logger.error(f"Failed to create issue: {result}")
                return None
        except Exception as e:
            self.logger.error(f"Error creating issue: {e}")
            return None
    
    async def update_issue(self, issue_id: str, **updates) -> Optional[Dict]:
        """Update an existing Linear issue"""
        if not self.config.capabilities.issue_management:
            raise ConfigurationError("Issue management capability not enabled")
        
        mutation = """
        mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
            issueUpdate(id: $id, input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    description
                    state {
                        name
                    }
                }
            }
        }
        """
        
        variables = {
            "id": issue_id,
            "input": updates
        }
        
        try:
            result = await self._execute_graphql_query(mutation, variables)
            if result and "data" in result and result["data"]["issueUpdate"]["success"]:
                issue = result["data"]["issueUpdate"]["issue"]
                self.logger.info(f"Updated issue {issue['identifier']}")
                return issue
            else:
                self.logger.error(f"Failed to update issue: {result}")
                return None
        except Exception as e:
            self.logger.error(f"Error updating issue: {e}")
            return None
    
    async def add_comment(self, issue_id: str, body: str) -> Optional[Dict]:
        """Add a comment to a Linear issue"""
        if not self.config.capabilities.comment_management:
            raise ConfigurationError("Comment management capability not enabled")
        
        mutation = """
        mutation CreateComment($input: CommentCreateInput!) {
            commentCreate(input: $input) {
                success
                comment {
                    id
                    body
                    createdAt
                }
            }
        }
        """
        
        variables = {
            "input": {
                "issueId": issue_id,
                "body": body
            }
        }
        
        try:
            result = await self._execute_graphql_query(mutation, variables)
            if result and "data" in result and result["data"]["commentCreate"]["success"]:
                comment = result["data"]["commentCreate"]["comment"]
                self.logger.info(f"Added comment to issue")
                return comment
            else:
                self.logger.error(f"Failed to add comment: {result}")
                return None
        except Exception as e:
            self.logger.error(f"Error adding comment: {e}")
            return None
    
    async def get_issues(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get issues with optional filters"""
        query = """
        query GetIssues($filter: IssueFilter) {
            issues(filter: $filter) {
                nodes {
                    id
                    identifier
                    title
                    description
                    state {
                        name
                    }
                    priority
                    createdAt
                    updatedAt
                    assignee {
                        name
                        email
                    }
                    team {
                        id
                        name
                    }
                }
            }
        }
        """
        
        variables = {}
        if filters:
            variables["filter"] = filters
        
        try:
            result = await self._execute_graphql_query(query, variables)
            if result and "data" in result:
                issues = result["data"]["issues"]["nodes"]
                self.logger.info(f"Retrieved {len(issues)} issues")
                return issues
            else:
                self.logger.error(f"Failed to get issues: {result}")
                return []
        except Exception as e:
            self.logger.error(f"Error getting issues: {e}")
            return []
    
    async def get_teams(self) -> List[Dict]:
        """Get available teams"""
        query = """
        query GetTeams {
            teams {
                nodes {
                    id
                    name
                    key
                    description
                }
            }
        }
        """
        
        try:
            result = await self._execute_graphql_query(query)
            if result and "data" in result:
                teams = result["data"]["teams"]["nodes"]
                self.logger.info(f"Retrieved {len(teams)} teams")
                return teams
            else:
                self.logger.error(f"Failed to get teams: {result}")
                return []
        except Exception as e:
            self.logger.error(f"Error getting teams: {e}")
            return []
    
    def register_webhook_handler(self, event_type: str, handler: Callable):
        """Register a webhook event handler"""
        if not self.config.capabilities.webhook_handling:
            raise ConfigurationError("Webhook handling capability not enabled")
        
        self.webhook_handlers[event_type] = handler
        self.logger.info(f"Registered webhook handler for {event_type}")
    
    async def handle_webhook(self, event_type: str, payload: Dict):
        """Handle incoming webhook event"""
        if event_type in self.webhook_handlers:
            try:
                await self.webhook_handlers[event_type](payload)
                self.logger.info(f"Handled webhook event: {event_type}")
            except Exception as e:
                self.logger.error(f"Error handling webhook {event_type}: {e}")
        else:
            self.logger.warning(f"No handler registered for webhook event: {event_type}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            "agent_id": self.config.agent_id,
            "status": self.status.value,
            "session_status": self.session_status.value,
            "metrics": {
                "requests_made": self.metrics.requests_made,
                "successful_operations": self.metrics.successful_operations,
                "failed_operations": self.metrics.failed_operations,
                "error_rate": self.metrics.error_rate,
                "average_response_time": self.metrics.average_response_time,
                "uptime_seconds": self.metrics.uptime_seconds,
                "last_activity": self.metrics.last_activity.isoformat() if self.metrics.last_activity else None
            },
            "rate_limit": {
                "requests_remaining": self.rate_limit.requests_remaining,
                "complexity_remaining": self.rate_limit.complexity_remaining,
                "reset_time": self.rate_limit.reset_time.isoformat()
            },
            "capabilities": self.config.capabilities.dict(),
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None
        }
    
    async def shutdown(self):
        """Shutdown the agent gracefully"""
        self.logger.info(f"Shutting down Linear agent {self.config.agent_id}")
        self.status = AgentStatus.STOPPED
        if self.client:
            await self.client.aclose()


# Agent Factory and Management
class LinearAgentFactory:
    """Factory for creating and managing Linear agents"""
    
    @staticmethod
    def create_agent(config: Dict[str, Any]) -> LinearAgent:
        """Create a Linear agent from configuration"""
        agent_config = LinearAgentConfig(**config)
        return LinearAgent(agent_config)
    
    @staticmethod
    def create_agent_from_file(config_path: str) -> LinearAgent:
        """Create a Linear agent from configuration file"""
        with open(config_path, 'r') as f:
            config = json.load(f)
        return LinearAgentFactory.create_agent(config)


class LinearAgentManager:
    """Manager for multiple Linear agents"""
    
    def __init__(self):
        self.agents: Dict[str, LinearAgent] = {}
        self.logger = logging.getLogger("linear_agent_manager")
    
    async def add_agent(self, agent: LinearAgent) -> bool:
        """Add and initialize an agent"""
        try:
            if await agent.initialize():
                self.agents[agent.config.agent_id] = agent
                self.logger.info(f"Added agent {agent.config.agent_id}")
                return True
            else:
                self.logger.error(f"Failed to initialize agent {agent.config.agent_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error adding agent: {e}")
            return False
    
    def get_agent(self, agent_id: str) -> Optional[LinearAgent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """List all agent IDs"""
        return list(self.agents.keys())
    
    def get_agents_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all agents"""
        return {
            agent_id: agent.get_status()
            for agent_id, agent in self.agents.items()
        }
    
    async def shutdown_all(self):
        """Shutdown all agents"""
        for agent in self.agents.values():
            await agent.shutdown()
        self.agents.clear()
        self.logger.info("All agents shut down")


# Utility Functions
def create_linear_agent_config(
    agent_id: str,
    client_id: str,
    scopes: List[str] = None,
    **kwargs
) -> LinearAgentConfig:
    """Helper function to create Linear agent configuration"""
    if scopes is None:
        scopes = ["read", "write", "issues:create"]
    
    oauth_config = LinearOAuthConfig(
        client_id=client_id,
        scopes=scopes,
        **{k: v for k, v in kwargs.items() if k in LinearOAuthConfig.__fields__}
    )
    
    return LinearAgentConfig(
        agent_id=agent_id,
        oauth_config=oauth_config,
        **{k: v for k, v in kwargs.items() if k in LinearAgentConfig.__fields__}
    )


# Main entry point for testing
async def main():
    """Main function for testing Linear agent integration"""
    logging.basicConfig(level=logging.INFO)
    
    # Example configuration (requires actual Linear OAuth app)
    config = create_linear_agent_config(
        agent_id="linear-agent-test",
        client_id="your-client-id",
        scopes=["read", "write", "issues:create"]
    )
    
    agent = LinearAgent(config)
    
    try:
        if await agent.initialize():
            print("Agent initialized successfully!")
            print(f"Status: {agent.get_status()}")
            
            # Example operations
            teams = await agent.get_teams()
            print(f"Available teams: {len(teams)}")
            
            issues = await agent.get_issues()
            print(f"Issues found: {len(issues)}")
            
        else:
            print("Failed to initialize agent")
    
    finally:
        await agent.shutdown()


if __name__ == "__main__":
    asyncio.run(main())