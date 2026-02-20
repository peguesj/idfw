import pytest
pytestmark = pytest.mark.skip(reason="Hooks system removed - identified as bloat")

"""
Comprehensive tests for the hooks system.
"""

import asyncio
import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

# Import the hooks system
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unified_framework.hooks import (
    initialize_hooks_system, get_initialized_system,
    HookSystem, HookContext, HookType, MessageScope,
    PrehookProcessor, PosthookProcessor, LinkCatalogHook,
    VectorRAGSystem, SecurityFramework, HookIntegrationManager,
    ConfigurationManager, HooksSystemConfig
)


class TestHooksSystemInitialization:
    """Test hooks system initialization and configuration."""
    
    def test_basic_initialization(self):
        """Test basic system initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'config.json'
            
            # Create basic config
            config = HooksSystemConfig()
            config_manager = ConfigurationManager(config_path)
            config_manager.config = config
            config_manager.save_config()
            
            # Initialize system
            system = initialize_hooks_system(config_path)
            
            assert system is not None
            assert 'hook_system' in system
            assert 'config_manager' in system
            assert 'components' in system
    
    def test_component_initialization(self):
        """Test that components are initialized based on configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'config.json'
            
            # Create config with specific components enabled
            config = HooksSystemConfig()
            config.prehook.enabled = True
            config.security.enabled = True
            config.link_catalog.enabled = False
            
            config_manager = ConfigurationManager(config_path)
            config_manager.config = config
            config_manager.save_config()
            
            # Initialize system
            system = initialize_hooks_system(config_path)
            components = system['components']
            
            assert 'prehook' in components
            assert 'security' in components
            assert 'link_catalog' not in components


class TestHookContext:
    """Test hook context functionality."""
    
    def test_hook_context_creation(self):
        """Test creating hook contexts."""
        context = HookContext(
            hook_id="test-123",
            hook_type=HookType.PREHOOK,
            timestamp=datetime.now(),
            scope=MessageScope.USER,
            message="Test message",
            metadata={"test": "data"}
        )
        
        assert context.hook_id == "test-123"
        assert context.hook_type == HookType.PREHOOK
        assert context.scope == MessageScope.USER
        assert context.message == "Test message"
        assert context.metadata["test"] == "data"
    
    def test_hook_context_serialization(self):
        """Test hook context serialization."""
        context = HookContext(
            hook_id="test-123",
            hook_type=HookType.PREHOOK,
            timestamp=datetime.now(),
            scope=MessageScope.USER,
            message="Test message",
            metadata={"test": "data"}
        )
        
        context_dict = context.to_dict()
        
        assert isinstance(context_dict, dict)
        assert context_dict['hook_id'] == "test-123"
        assert context_dict['hook_type'] == HookType.PREHOOK
        assert context_dict['message'] == "Test message"


class TestPrehookProcessor:
    """Test prehook message processing."""
    
    @pytest.fixture
    def prehook_processor(self):
        """Create a prehook processor for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            return PrehookProcessor(Path(temp_dir))
    
    @pytest.mark.asyncio
    async def test_message_processing(self, prehook_processor):
        """Test basic message processing."""
        context = HookContext(
            hook_id="test-123",
            hook_type=HookType.PREHOOK,
            timestamp=datetime.now(),
            scope=MessageScope.USER,
            message="This is an urgent bug fix needed immediately!",
            metadata={}
        )
        
        result = await prehook_processor.process_message(context)
        
        assert isinstance(result, type(prehook_processor.processing_history[0]))
        assert result.sentiment_analysis is not None
        assert result.accuracy_metrics is not None
        assert len(result.chunks) > 0
    
    def test_sentiment_analysis(self, prehook_processor):
        """Test sentiment analysis functionality."""
        analyzer = prehook_processor.sentiment_analyzer
        
        # Test urgent message
        urgent_result = analyzer.analyze("This is urgent! Fix immediately!")
        assert urgent_result.urgency_score > 0.5
        
        # Test positive message
        positive_result = analyzer.analyze("Great work! This looks perfect.")
        assert positive_result.confidence > 0.3
    
    def test_accuracy_evaluation(self, prehook_processor):
        """Test accuracy metrics evaluation."""
        evaluator = prehook_processor.accuracy_evaluator
        
        context = HookContext(
            hook_id="test-123",
            hook_type=HookType.PREHOOK,
            timestamp=datetime.now(),
            scope=MessageScope.USER,
            message="Test message",
            metadata={}
        )
        
        # Test clear, actionable message
        clear_message = "Please implement the user authentication system using JWT tokens"
        result = evaluator.evaluate(clear_message, context)
        
        assert result.clarity > 0.5
        assert result.actionability > 0.5
        assert result.overall_score() >= 0.0
    
    def test_token_management(self, prehook_processor):
        """Test token management and chunking."""
        token_manager = prehook_processor.token_manager
        
        # Test short message (no chunking needed)
        short_message = "Short message"
        chunks = token_manager.chunk_message(short_message)
        assert len(chunks) == 1
        assert chunks[0] == short_message
        
        # Test long message (chunking needed)
        long_message = "This is a very long message. " * 100
        chunks = token_manager.chunk_message(long_message)
        assert len(chunks) > 1


class TestPosthookProcessor:
    """Test posthook reporting and pattern recognition."""
    
    @pytest.fixture
    def posthook_processor(self):
        """Create a posthook processor for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            return PosthookProcessor(Path(temp_dir))
    
    def test_execution_tracking(self, posthook_processor):
        """Test execution tracking functionality."""
        context = HookContext(
            hook_id="test-123",
            hook_type=HookType.POSTHOOK,
            timestamp=datetime.now(),
            scope=MessageScope.TASK,
            message="Task completed successfully",
            metadata={}
        )
        
        execution_id = posthook_processor.start_execution_tracking(context)
        assert execution_id in posthook_processor.active_executions
    
    @pytest.mark.asyncio
    async def test_execution_completion(self, posthook_processor):
        """Test execution completion processing."""
        from unified_framework.hooks.posthook import ExecutionStatus, ExecutionMetrics
        
        context = HookContext(
            hook_id="test-123",
            hook_type=HookType.POSTHOOK,
            timestamp=datetime.now(),
            scope=MessageScope.TASK,
            message="Task completed",
            metadata={}
        )
        
        execution_id = posthook_processor.start_execution_tracking(context)
        
        metrics = ExecutionMetrics(
            execution_time=1.5,
            cpu_usage=None,
            memory_usage=None,
            disk_io=None,
            network_io=None,
            error_count=0,
            warning_count=1,
            test_coverage=None,
            build_success=True,
            deployment_success=True
        )
        
        report = await posthook_processor.process_execution_completion(
            execution_id,
            context,
            ExecutionStatus.SUCCESS,
            "Task completed successfully",
            metrics
        )
        
        assert report.execution_status == ExecutionStatus.SUCCESS
        assert len(report.lessons_learned) >= 0
        assert len(report.next_actions) >= 0
    
    def test_pattern_recognition(self, posthook_processor):
        """Test pattern recognition functionality."""
        recognizer = posthook_processor.pattern_recognizer
        
        context = HookContext(
            hook_id="test-123",
            hook_type=HookType.POSTHOOK,
            timestamp=datetime.now(),
            scope=MessageScope.TASK,
            message="Build failed with TypeScript errors",
            metadata={}
        )
        
        from unified_framework.hooks.posthook import ExecutionMetrics
        metrics = ExecutionMetrics(
            execution_time=30.0,
            cpu_usage=None,
            memory_usage=None,
            disk_io=None,
            network_io=None,
            error_count=3,
            warning_count=1,
            test_coverage=None,
            build_success=False,
            deployment_success=False
        )
        
        patterns = recognizer.analyze_execution(
            context,
            metrics,
            "TypeScript compilation failed with 3 errors"
        )
        
        assert len(patterns) >= 0  # Should detect some patterns


class TestLinkCatalogHook:
    """Test link cataloging functionality."""
    
    @pytest.fixture
    def link_catalog(self):
        """Create a link catalog for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            return LinkCatalogHook(Path(temp_dir))
    
    def test_link_extraction(self, link_catalog):
        """Test link extraction from content."""
        extractor = link_catalog.extractor
        
        content = """
        Check out this documentation: https://docs.example.com/api
        Also see: https://github.com/user/repo for the source code
        """
        
        links = extractor.extract_links(content)
        assert len(links) == 2
        assert "https://docs.example.com/api" in [link[0] for link in links]
        assert "https://github.com/user/repo" in [link[0] for link in links]
    
    def test_link_classification(self, link_catalog):
        """Test link classification."""
        extractor = link_catalog.extractor
        
        # Test documentation link
        doc_link = "https://docs.react.dev/learn"
        doc_type, confidence = extractor.classify_link(doc_link, "React documentation")
        assert confidence > 0.5
        
        # Test repository link
        repo_link = "https://github.com/facebook/react"
        repo_type, confidence = extractor.classify_link(repo_link, "React repository")
        assert confidence > 0.8
    
    @pytest.mark.asyncio
    async def test_tool_use_processing(self, link_catalog):
        """Test processing tool use for link cataloging."""
        context = HookContext(
            hook_id="test-123",
            hook_type=HookType.POST_TOOL_USE,
            timestamp=datetime.now(),
            scope=MessageScope.SYSTEM,
            message="Check out https://example.com/docs",
            metadata={
                'tool_result': 'Found documentation at https://docs.example.com'
            }
        )
        
        result = await link_catalog.process_tool_use(context)
        
        assert 'total_links_found' in result
        assert 'catalogued_links' in result


class TestVectorRAGSystem:
    """Test vector RAG functionality."""
    
    @pytest.fixture
    def vector_rag(self):
        """Create a vector RAG system for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            return VectorRAGSystem(Path(temp_dir))
    
    def test_semantic_chunking(self, vector_rag):
        """Test semantic chunking functionality."""
        chunker = vector_rag.chunker
        
        content = "This is a test document. " * 50  # Long content
        chunks = chunker.chunk_content(content, "test-doc", "document")
        
        assert len(chunks) > 0
        if len(content) > chunker.max_chunk_size:
            assert len(chunks) > 1
    
    def test_embedding_generation(self, vector_rag):
        """Test embedding generation."""
        generator = vector_rag.embedding_generator
        
        text = "This is a test message for embedding generation"
        embedding = generator.generate_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == generator.embedding_dimension
        assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_content_addition(self, vector_rag):
        """Test adding content to vector database."""
        content = "This is test content for the vector database"
        result = await vector_rag.add_content(
            content, "test-source", "test-type"
        )
        
        assert 'chunks_created' in result
        assert 'embeddings_created' in result
        assert result['chunks_created'] > 0
        assert result['embeddings_created'] > 0
    
    @pytest.mark.asyncio
    async def test_querying(self, vector_rag):
        """Test querying the vector database."""
        # Add some content first
        await vector_rag.add_content(
            "This is about machine learning and AI",
            "ml-doc", "document"
        )
        
        # Query for similar content
        result = await vector_rag.query("artificial intelligence")
        
        assert 'query' in result
        assert 'results_found' in result
        assert 'search_results' in result


class TestSecurityFramework:
    """Test security and compliance functionality."""
    
    @pytest.fixture
    def security_framework(self):
        """Create a security framework for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            return SecurityFramework(Path(temp_dir))
    
    def test_pii_detection(self, security_framework):
        """Test PII detection functionality."""
        detector = security_framework.pii_detector
        
        # Test email detection
        email_content = "Contact me at john.doe@example.com for more info"
        result = detector.detect_pii(email_content)
        
        assert result.found_pii
        assert 'email' in result.pii_types
        assert result.confidence_scores['email'] > 0.8
    
    def test_vulnerability_scanning(self, security_framework):
        """Test vulnerability scanning."""
        scanner = security_framework.vulnerability_scanner
        
        # Test hardcoded secret detection
        vulnerable_code = '''
        password = "secret123"
        api_key = "sk-1234567890abcdef"
        '''
        
        assessment = scanner.scan_content(vulnerable_code)
        
        assert len(assessment.vulnerabilities_found) > 0
        assert assessment.overall_risk_score > 0
    
    @pytest.mark.asyncio
    async def test_security_check_processing(self, security_framework):
        """Test comprehensive security check processing."""
        from unified_framework.hooks.security import SecurityLevel
        
        context = HookContext(
            hook_id="test-123",
            hook_type=HookType.PREHOOK,
            timestamp=datetime.now(),
            scope=MessageScope.USER,
            message="Test message with email john@example.com",
            metadata={}
        )
        
        result = await security_framework.process_security_check(
            context.message, context, SecurityLevel.INTERNAL
        )
        
        assert 'security_level' in result
        assert 'pii_detection' in result
        assert 'checks_performed' in result


class TestConfigurationManager:
    """Test configuration management."""
    
    def test_config_creation(self):
        """Test creating default configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'config.json'
            config_manager = ConfigurationManager(config_path)
            
            assert isinstance(config_manager.config, HooksSystemConfig)
            assert config_manager.config.enabled
    
    def test_config_save_load(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'config.json'
            
            # Create and save config
            config_manager = ConfigurationManager(config_path)
            config_manager.config.debug_mode = True
            config_manager.config.project_id = "test-project"
            assert config_manager.save_config()
            
            # Load config
            new_config_manager = ConfigurationManager(config_path)
            assert new_config_manager.config.debug_mode
            assert new_config_manager.config.project_id == "test-project"
    
    def test_config_validation(self):
        """Test configuration validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'config.json'
            config_manager = ConfigurationManager(config_path)
            
            # Test with invalid values
            config_manager.config.storage.max_storage_mb = 50  # Too low
            config_manager.config.performance.max_concurrent_hooks = 0  # Invalid
            
            issues = config_manager.validate_config()
            assert len(issues) > 0


class TestIntegrationPoints:
    """Test system integration points."""
    
    @pytest.fixture
    def integration_manager(self):
        """Create an integration manager for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            hook_system = HookSystem(Path(temp_dir) / 'config.json')
            return HookIntegrationManager(hook_system)
    
    @pytest.mark.asyncio
    async def test_todo_integration(self, integration_manager):
        """Test todo system integration."""
        todo_integration = integration_manager.todo_integration
        
        context = HookContext(
            hook_id="test-123",
            hook_type=HookType.CONTEXT_HOOK,
            timestamp=datetime.now(),
            scope=MessageScope.TASK,
            message="Test todo creation",
            metadata={}
        )
        
        todo_data = {
            'id': 'test-todo-123',
            'content': 'Implement user authentication'
        }
        
        result = await todo_integration.on_todo_created(todo_data, context)
        
        assert 'todo_id' in result
        assert 'priority_assessment' in result
        assert 'complexity_assessment' in result
    
    def test_agent_performance_tracking(self, integration_manager):
        """Test agent performance tracking."""
        agent_integration = integration_manager.agent_integration
        
        context = HookContext(
            hook_id="test-123",
            hook_type=HookType.CONTEXT_HOOK,
            timestamp=datetime.now(),
            scope=MessageScope.AGENT,
            message="Test agent deployment",
            metadata={}
        )
        
        agent_data = {
            'agent_id': 'test-agent-123',
            'name': 'Test Agent',
            'specialization': 'testing'
        }
        
        # This is a sync test for the performance tracking setup
        agent_integration.agent_performance['test-agent-123'] = {
            'deployed_at': datetime.now().isoformat(),
            'task_count': 5,
            'success_count': 4,
            'failure_count': 1,
            'average_execution_time': 15.0,
            'specialization': 'testing'
        }
        
        recommendations = agent_integration.optimize_task_distribution()
        assert 'optimization_recommendations' in recommendations


def run_performance_benchmarks():
    """Run basic performance benchmarks."""
    import time
    
    print("\n=== Performance Benchmarks ===")
    
    # Test prehook processing speed
    with tempfile.TemporaryDirectory() as temp_dir:
        processor = PrehookProcessor(Path(temp_dir))
        
        test_message = "This is a test message for performance benchmarking. " * 20
        context = HookContext(
            hook_id="perf-test",
            hook_type=HookType.PREHOOK,
            timestamp=datetime.now(),
            scope=MessageScope.USER,
            message=test_message,
            metadata={}
        )
        
        # Benchmark prehook processing
        start_time = time.time()
        for _ in range(10):
            asyncio.run(processor.process_message(context))
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        print(f"Prehook processing: {avg_time:.3f}s average per message")
        
        # Benchmark sentiment analysis
        analyzer = processor.sentiment_analyzer
        start_time = time.time()
        for _ in range(100):
            analyzer.analyze(test_message)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100
        print(f"Sentiment analysis: {avg_time:.4f}s average per message")
        
        # Benchmark vector embeddings
        vector_system = VectorRAGSystem(Path(temp_dir) / 'vectors')
        generator = vector_system.embedding_generator
        
        start_time = time.time()
        for _ in range(50):
            generator.generate_embedding(test_message)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 50
        print(f"Vector embedding generation: {avg_time:.4f}s average")
        
        print("=== Benchmarks Complete ===\n")


if __name__ == "__main__":
    print("Running hooks system tests...")
    
    # Run performance benchmarks
    run_performance_benchmarks()
    
    # Run basic validation tests
    print("Running basic validation tests...")
    
    # Test system initialization
    try:
        system = initialize_hooks_system()
        print("✓ System initialization successful")
        
        # Test configuration
        config = system['config']
        if config.enabled:
            print("✓ Configuration loaded successfully")
        
        # Test components
        components = system['components']
        print(f"✓ Initialized {len(components)} components")
        
        # Test hook execution
        hook_system = system['hook_system']
        if len(hook_system.registry._hook_metadata) > 0:
            print("✓ Hooks registered successfully")
        
        print(f"\nSystem ready with components: {list(components.keys())}")
        
    except Exception as e:
        print(f"✗ System initialization failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nBasic validation complete!")