"""
Claude Code Hooks System for IDFWU

This module implements a comprehensive hook system for message ingestion,
sentiment analysis, vectorization, and RAG capabilities.
"""

from .core import HookSystem, HookRegistry, HookContext, HookType, MessageScope, get_hook_system
from .prehook import PrehookProcessor, SentimentAnalysis, AccuracyMetrics, ProcessedMessage
from .posthook import PosthookProcessor, ExecutionStatus, ExecutionMetrics, ExecutionReport
from .link_catalog import LinkCatalogHook, LinkType, CataloguedLink
from .vector_rag import VectorRAGSystem, SemanticChunk, VectorEmbedding
from .security import SecurityFramework, SecurityLevel, PIIDetectionResult
from .integrations import HookIntegrationManager
from .config import ConfigurationManager, HooksSystemConfig, get_config, get_config_manager

__all__ = [
    # Core components
    'HookSystem',
    'HookRegistry',
    'HookContext',
    'HookType',
    'MessageScope',
    'get_hook_system',
    
    # Prehook system
    'PrehookProcessor',
    'SentimentAnalysis',
    'AccuracyMetrics', 
    'ProcessedMessage',
    
    # Posthook system
    'PosthookProcessor',
    'ExecutionStatus',
    'ExecutionMetrics',
    'ExecutionReport',
    
    # Link cataloging
    'LinkCatalogHook',
    'LinkType',
    'CataloguedLink',
    
    # Vector RAG
    'VectorRAGSystem',
    'SemanticChunk',
    'VectorEmbedding',
    
    # Security
    'SecurityFramework',
    'SecurityLevel',
    'PIIDetectionResult',
    
    # Integrations
    'HookIntegrationManager',
    
    # Configuration
    'ConfigurationManager',
    'HooksSystemConfig',
    'get_config',
    'get_config_manager',
    
    # Main initialization
    'initialize_hooks_system',
    'get_initialized_system'
]

# Global system instance
_initialized_system = None

def initialize_hooks_system(config_path=None, auto_setup_integrations=True):
    """Initialize the complete hooks system with all components."""
    global _initialized_system
    
    if _initialized_system is not None:
        return _initialized_system
    
    # Load configuration
    config_manager = ConfigurationManager(config_path)
    config = config_manager.get_config()
    
    # Initialize core hook system
    hook_system = get_hook_system()
    
    # Initialize all components based on configuration
    components = {}
    
    if config.prehook.enabled:
        components['prehook'] = PrehookProcessor()
        
        # Register prehook processor
        hook_system.registry.register(
            HookType.PREHOOK,
            components['prehook'].process_message,
            priority=100,
            name='main_prehook_processor'
        )
    
    if config.posthook.enabled:
        components['posthook'] = PosthookProcessor()
    
    if config.link_catalog.enabled:
        components['link_catalog'] = LinkCatalogHook()
        
        # Register link catalog hook
        hook_system.registry.register(
            HookType.POST_TOOL_USE,
            components['link_catalog'].process_tool_use,
            priority=90,
            name='link_catalog_processor'
        )
    
    if config.vector_rag.enabled:
        components['vector_rag'] = VectorRAGSystem()
    
    if config.security.enabled:
        components['security'] = SecurityFramework()
        
        # Register security processor for all hook types
        async def security_processor(context):
            return await components['security'].process_security_check(
                context.message, context, SecurityLevel.INTERNAL
            )
        
        hook_system.registry.register(
            HookType.PREHOOK,
            security_processor,
            priority=200,  # High priority for security
            name='security_processor'
        )
    
    # Initialize integrations
    if auto_setup_integrations:
        components['integrations'] = HookIntegrationManager(hook_system)
    
    _initialized_system = {
        'hook_system': hook_system,
        'config_manager': config_manager,
        'config': config,
        'components': components
    }
    
    return _initialized_system

def get_initialized_system():
    """Get the initialized hooks system."""
    global _initialized_system
    
    if _initialized_system is None:
        return initialize_hooks_system()
    
    return _initialized_system