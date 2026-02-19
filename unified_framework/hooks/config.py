"""
Configuration system for the hooks framework.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PrehookConfig:
    """Configuration for prehook processing."""
    enabled: bool = True
    sentiment_analysis_enabled: bool = True
    accuracy_metrics_enabled: bool = True
    token_management_enabled: bool = True
    max_message_length: int = 10000
    min_confidence_threshold: float = 0.5
    custom_sentiment_patterns: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.custom_sentiment_patterns is None:
            self.custom_sentiment_patterns = {}


@dataclass
class PosthookConfig:
    """Configuration for posthook processing."""
    enabled: bool = True
    pattern_recognition_enabled: bool = True
    dependency_detection_enabled: bool = True
    next_action_generation_enabled: bool = True
    reinforcement_learning_enabled: bool = True
    max_execution_history: int = 1000
    pattern_confidence_threshold: float = 0.6
    auto_optimization_enabled: bool = True


@dataclass
class LinkCatalogConfig:
    """Configuration for link cataloging."""
    enabled: bool = True
    auto_categorization_enabled: bool = True
    metadata_extraction_enabled: bool = True
    dependency_analysis_enabled: bool = True
    dead_link_detection_enabled: bool = True
    max_links_per_session: int = 100
    verification_interval_hours: int = 24
    confidence_threshold: float = 0.5


@dataclass
class VectorRAGConfig:
    """Configuration for vector RAG system."""
    enabled: bool = True
    auto_indexing_enabled: bool = True
    semantic_chunking_enabled: bool = True
    max_chunk_size: int = 1000
    overlap_size: int = 100
    embedding_dimension: int = 512
    similarity_threshold: float = 0.1
    max_results: int = 20
    context_window_size: int = 4000
    index_optimization_enabled: bool = True


@dataclass
class SecurityConfig:
    """Configuration for security framework."""
    enabled: bool = True
    pii_detection_enabled: bool = True
    auto_encryption_enabled: bool = True
    auto_redaction_enabled: bool = True
    vulnerability_scanning_enabled: bool = True
    compliance_validation_enabled: bool = True
    audit_logging_enabled: bool = True
    alert_on_critical_enabled: bool = True
    encryption_algorithm: str = "AES-256-GCM"
    compliance_frameworks: List[str] = None
    
    def __post_init__(self):
        if self.compliance_frameworks is None:
            self.compliance_frameworks = ["gdpr", "soc2"]


@dataclass
class IntegrationConfig:
    """Configuration for system integrations."""
    todo_integration_enabled: bool = True
    agent_integration_enabled: bool = True
    ide_integration_enabled: bool = True
    linear_integration_enabled: bool = True
    mcp_integration_enabled: bool = True
    auto_issue_creation_enabled: bool = True
    performance_tracking_enabled: bool = True
    quality_monitoring_enabled: bool = True


@dataclass
class PerformanceConfig:
    """Configuration for performance settings."""
    parallel_execution_enabled: bool = True
    max_concurrent_hooks: int = 10
    hook_timeout_seconds: int = 30
    rate_limit_enabled: bool = True
    max_requests_per_second: int = 10
    cache_enabled: bool = True
    cache_max_size_mb: int = 100
    background_processing_enabled: bool = True


@dataclass
class StorageConfig:
    """Configuration for storage settings."""
    storage_root: str = ""
    max_storage_mb: int = 1000
    retention_days: int = 30
    auto_cleanup_enabled: bool = True
    compression_enabled: bool = True
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    encryption_at_rest_enabled: bool = True
    
    def __post_init__(self):
        if not self.storage_root:
            self.storage_root = str(Path.home() / '.claude' / 'hooks')


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    enabled: bool = True
    log_level: LogLevel = LogLevel.INFO
    log_to_file: bool = True
    log_to_console: bool = False
    log_file_path: str = ""
    max_log_size_mb: int = 10
    max_log_files: int = 5
    structured_logging: bool = True
    
    def __post_init__(self):
        if not self.log_file_path:
            self.log_file_path = str(Path.home() / '.claude' / 'hooks' / 'hooks.log')


@dataclass
class HooksSystemConfig:
    """Complete hooks system configuration."""
    # Core settings
    enabled: bool = True
    debug_mode: bool = False
    version: str = "1.0.0"
    
    # Component configurations
    prehook: PrehookConfig = None
    posthook: PosthookConfig = None
    link_catalog: LinkCatalogConfig = None
    vector_rag: VectorRAGConfig = None
    security: SecurityConfig = None
    integrations: IntegrationConfig = None
    performance: PerformanceConfig = None
    storage: StorageConfig = None
    logging: LoggingConfig = None
    
    # Project-specific settings
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    
    # Custom settings
    custom_settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.prehook is None:
            self.prehook = PrehookConfig()
        if self.posthook is None:
            self.posthook = PosthookConfig()
        if self.link_catalog is None:
            self.link_catalog = LinkCatalogConfig()
        if self.vector_rag is None:
            self.vector_rag = VectorRAGConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.integrations is None:
            self.integrations = IntegrationConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.storage is None:
            self.storage = StorageConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
        if self.custom_settings is None:
            self.custom_settings = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)


class ConfigurationManager:
    """Manages hooks system configuration."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / '.claude' / 'hooks' / 'config.json'
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Default configuration
        self.config = HooksSystemConfig()
        
        # Load existing configuration
        self.load_config()
        
        # Environment variable overrides
        self._apply_env_overrides()
    
    def load_config(self) -> HooksSystemConfig:
        """Load configuration from file."""
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_dict = json.load(f)
                
                # Reconstruct configuration objects
                self.config = self._dict_to_config(config_dict)
                
            except Exception as e:
                print(f"Warning: Could not load hooks configuration: {e}")
                print("Using default configuration")
        
        return self.config
    
    def save_config(self) -> bool:
        """Save configuration to file."""
        
        try:
            config_dict = self.config.to_dict()
            
            with open(self.config_path, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"Error: Could not save hooks configuration: {e}")
            return False
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values."""
        
        try:
            # Apply updates to current config
            self._apply_updates(self.config, updates)
            
            # Save updated configuration
            return self.save_config()
            
        except Exception as e:
            print(f"Error: Could not update hooks configuration: {e}")
            return False
    
    def get_config(self) -> HooksSystemConfig:
        """Get current configuration."""
        return self.config
    
    def get_component_config(self, component: str) -> Any:
        """Get configuration for a specific component."""
        
        component_configs = {
            'prehook': self.config.prehook,
            'posthook': self.config.posthook,
            'link_catalog': self.config.link_catalog,
            'vector_rag': self.config.vector_rag,
            'security': self.config.security,
            'integrations': self.config.integrations,
            'performance': self.config.performance,
            'storage': self.config.storage,
            'logging': self.config.logging
        }
        
        return component_configs.get(component)
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return any issues."""
        
        issues = []
        
        # Validate storage settings
        if self.config.storage.max_storage_mb < 100:
            issues.append("Storage limit too low (minimum 100MB recommended)")
        
        if self.config.storage.retention_days < 1:
            issues.append("Retention period too short (minimum 1 day)")
        
        # Validate performance settings
        if self.config.performance.max_concurrent_hooks < 1:
            issues.append("Max concurrent hooks must be at least 1")
        
        if self.config.performance.hook_timeout_seconds < 5:
            issues.append("Hook timeout too short (minimum 5 seconds)")
        
        # Validate vector RAG settings
        if self.config.vector_rag.max_chunk_size < 100:
            issues.append("Max chunk size too small (minimum 100 characters)")
        
        if self.config.vector_rag.embedding_dimension < 50:
            issues.append("Embedding dimension too small (minimum 50)")
        
        # Validate security settings
        if self.config.security.enabled and not self.config.security.audit_logging_enabled:
            issues.append("Security enabled but audit logging disabled (security risk)")
        
        # Validate paths exist
        storage_path = Path(self.config.storage.storage_root)
        if not storage_path.exists():
            try:
                storage_path.mkdir(parents=True, exist_ok=True)
            except Exception:
                issues.append(f"Cannot create storage directory: {storage_path}")
        
        return issues
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults."""
        
        try:
            self.config = HooksSystemConfig()
            return self.save_config()
            
        except Exception as e:
            print(f"Error: Could not reset hooks configuration: {e}")
            return False
    
    def export_config(self, export_path: Path) -> bool:
        """Export configuration to specified path."""
        
        try:
            config_dict = self.config.to_dict()
            
            with open(export_path, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"Error: Could not export hooks configuration: {e}")
            return False
    
    def import_config(self, import_path: Path) -> bool:
        """Import configuration from specified path."""
        
        try:
            with open(import_path, 'r') as f:
                config_dict = json.load(f)
            
            self.config = self._dict_to_config(config_dict)
            return self.save_config()
            
        except Exception as e:
            print(f"Error: Could not import hooks configuration: {e}")
            return False
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> HooksSystemConfig:
        """Convert dictionary to configuration object."""
        
        # Handle nested configurations
        if 'prehook' in config_dict:
            config_dict['prehook'] = PrehookConfig(**config_dict['prehook'])
        
        if 'posthook' in config_dict:
            config_dict['posthook'] = PosthookConfig(**config_dict['posthook'])
        
        if 'link_catalog' in config_dict:
            config_dict['link_catalog'] = LinkCatalogConfig(**config_dict['link_catalog'])
        
        if 'vector_rag' in config_dict:
            config_dict['vector_rag'] = VectorRAGConfig(**config_dict['vector_rag'])
        
        if 'security' in config_dict:
            config_dict['security'] = SecurityConfig(**config_dict['security'])
        
        if 'integrations' in config_dict:
            config_dict['integrations'] = IntegrationConfig(**config_dict['integrations'])
        
        if 'performance' in config_dict:
            config_dict['performance'] = PerformanceConfig(**config_dict['performance'])
        
        if 'storage' in config_dict:
            config_dict['storage'] = StorageConfig(**config_dict['storage'])
        
        if 'logging' in config_dict and isinstance(config_dict['logging'], dict):
            if 'log_level' in config_dict['logging']:
                if isinstance(config_dict['logging']['log_level'], str):
                    config_dict['logging']['log_level'] = LogLevel(config_dict['logging']['log_level'])
            config_dict['logging'] = LoggingConfig(**config_dict['logging'])
        
        return HooksSystemConfig(**config_dict)
    
    def _apply_updates(self, config_obj: Any, updates: Dict[str, Any]):
        """Apply updates to configuration object."""
        
        for key, value in updates.items():
            if hasattr(config_obj, key):
                current_value = getattr(config_obj, key)
                
                if isinstance(current_value, dict) and isinstance(value, dict):
                    # Merge dictionaries
                    current_value.update(value)
                elif hasattr(current_value, '__dict__') and isinstance(value, dict):
                    # Recursively update nested objects
                    self._apply_updates(current_value, value)
                else:
                    # Direct assignment
                    setattr(config_obj, key, value)
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        
        # Check for environment variable overrides
        env_overrides = {
            'CLAUDE_HOOKS_ENABLED': ('enabled', bool),
            'CLAUDE_HOOKS_DEBUG': ('debug_mode', bool),
            'CLAUDE_HOOKS_STORAGE_ROOT': ('storage.storage_root', str),
            'CLAUDE_HOOKS_MAX_STORAGE_MB': ('storage.max_storage_mb', int),
            'CLAUDE_HOOKS_PROJECT_ID': ('project_id', str),
            'CLAUDE_HOOKS_USER_ID': ('user_id', str),
            'CLAUDE_HOOKS_SECURITY_ENABLED': ('security.enabled', bool),
            'CLAUDE_HOOKS_PII_DETECTION': ('security.pii_detection_enabled', bool),
            'CLAUDE_HOOKS_VECTOR_RAG_ENABLED': ('vector_rag.enabled', bool),
        }
        
        for env_var, (config_path, value_type) in env_overrides.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    # Convert value to appropriate type
                    if value_type == bool:
                        parsed_value = env_value.lower() in ('true', '1', 'yes', 'on')
                    elif value_type == int:
                        parsed_value = int(env_value)
                    else:
                        parsed_value = env_value
                    
                    # Apply to config using dot notation
                    self._set_nested_value(self.config, config_path, parsed_value)
                    
                except (ValueError, AttributeError) as e:
                    print(f"Warning: Invalid environment variable {env_var}: {e}")
    
    def _set_nested_value(self, obj: Any, path: str, value: Any):
        """Set value using dot notation path."""
        
        parts = path.split('.')
        current = obj
        
        for part in parts[:-1]:
            current = getattr(current, part)
        
        setattr(current, parts[-1], value)


# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def get_config() -> HooksSystemConfig:
    """Get the current hooks system configuration."""
    return get_config_manager().get_config()


def update_config(updates: Dict[str, Any]) -> bool:
    """Update the hooks system configuration."""
    return get_config_manager().update_config(updates)


def reload_config() -> HooksSystemConfig:
    """Reload configuration from file."""
    return get_config_manager().load_config()


# Configuration validation utilities
def validate_storage_path(path: str) -> bool:
    """Validate storage path is accessible."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def validate_file_permissions(file_path: str, required_perms: str = 'rw') -> bool:
    """Validate file permissions."""
    try:
        path = Path(file_path)
        if not path.exists():
            return True  # File doesn't exist yet
        
        can_read = 'r' not in required_perms or os.access(path, os.R_OK)
        can_write = 'w' not in required_perms or os.access(path, os.W_OK)
        
        return can_read and can_write
    except Exception:
        return False


def estimate_storage_usage(config: HooksSystemConfig) -> Dict[str, Any]:
    """Estimate storage usage based on configuration."""
    
    storage_root = Path(config.storage.storage_root)
    
    if not storage_root.exists():
        return {
            'current_usage_mb': 0,
            'estimated_daily_mb': 10,  # Base estimate
            'days_until_full': config.storage.max_storage_mb / 10
        }
    
    # Calculate current usage
    current_usage = 0
    try:
        for file_path in storage_root.rglob('*'):
            if file_path.is_file():
                current_usage += file_path.stat().st_size
    except Exception:
        pass
    
    current_usage_mb = current_usage / (1024 * 1024)
    
    # Estimate daily usage based on configuration
    estimated_daily_mb = 5  # Base estimate
    
    if config.prehook.enabled:
        estimated_daily_mb += 2
    if config.posthook.enabled:
        estimated_daily_mb += 3
    if config.link_catalog.enabled:
        estimated_daily_mb += 1
    if config.vector_rag.enabled:
        estimated_daily_mb += 5
    if config.security.audit_logging_enabled:
        estimated_daily_mb += 2
    
    # Adjust for retention and compression
    if config.storage.compression_enabled:
        estimated_daily_mb *= 0.6  # 40% compression estimate
    
    days_until_full = (config.storage.max_storage_mb - current_usage_mb) / estimated_daily_mb
    
    return {
        'current_usage_mb': round(current_usage_mb, 2),
        'estimated_daily_mb': round(estimated_daily_mb, 2),
        'days_until_full': max(0, round(days_until_full, 1)),
        'cleanup_recommended': days_until_full < 7
    }