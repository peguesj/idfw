"""
Basic validation tests for the hooks system.
"""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path

# Import the hooks system
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unified_framework.hooks import (
    initialize_hooks_system, get_initialized_system,
    HookContext, HookType, MessageScope,
    ConfigurationManager, HooksSystemConfig
)


def test_basic_functionality():
    """Test basic hooks system functionality."""
    print("Testing basic hooks system functionality...")
    
    try:
        # Test 1: System initialization
        print("1. Testing system initialization...")
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'config.json'
            
            # Create basic config
            config_manager = ConfigurationManager(config_path)
            config = config_manager.get_config()
            
            # Ensure storage paths use temp directory
            config.storage.storage_root = str(Path(temp_dir) / 'hooks')
            config_manager.save_config()
            
            # Initialize system
            system = initialize_hooks_system(config_path, auto_setup_integrations=False)
            
            assert system is not None
            assert 'hook_system' in system
            assert 'config' in system
            assert 'components' in system
            print("   ✓ System initialization successful")
        
        # Test 2: Hook context creation
        print("2. Testing hook context creation...")
        context = HookContext(
            hook_id="test-123",
            hook_type=HookType.PREHOOK,
            timestamp=datetime.now(),
            scope=MessageScope.USER,
            message="Test message for hooks system",
            metadata={"test": "data"}
        )
        
        assert context.hook_id == "test-123"
        assert context.message == "Test message for hooks system"
        print("   ✓ Hook context creation successful")
        
        # Test 3: Configuration management
        print("3. Testing configuration management...")
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'config.json'
            config_manager = ConfigurationManager(config_path)
            
            # Test config validation
            issues = config_manager.validate_config()
            print(f"   ✓ Configuration validation completed ({len(issues)} issues found)")
            
            # Test config save/load
            config_manager.config.project_id = "test-project-123"
            save_result = config_manager.save_config()
            assert save_result, "Config save failed"
            
            # Load config
            new_manager = ConfigurationManager(config_path)
            assert new_manager.config.project_id == "test-project-123"
            print("   ✓ Configuration save/load successful")
        
        # Test 4: Component availability
        print("4. Testing component availability...")
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'config.json'
            
            # Create config with all components enabled
            config_manager = ConfigurationManager(config_path)
            config = config_manager.get_config()
            config.storage.storage_root = str(Path(temp_dir) / 'hooks')
            
            # Save and initialize
            config_manager.save_config()
            system = initialize_hooks_system(config_path, auto_setup_integrations=False)
            
            components = system['components']
            expected_components = ['prehook', 'posthook', 'link_catalog', 'vector_rag', 'security']
            
            for component in expected_components:
                if component in components:
                    print(f"   ✓ {component} component initialized")
                else:
                    print(f"   - {component} component not initialized")
        
        # Test 5: Basic message processing (without async storage)
        print("5. Testing basic message processing...")
        with tempfile.TemporaryDirectory() as temp_dir:
            from unified_framework.hooks.prehook import SentimentAnalyzer, AccuracyEvaluator
            
            analyzer = SentimentAnalyzer()
            evaluator = AccuracyEvaluator()
            
            # Test sentiment analysis
            test_message = "This is an urgent task that needs immediate attention!"
            sentiment_result = analyzer.analyze(test_message)
            assert sentiment_result.urgency_score > 0.3
            print("   ✓ Sentiment analysis working")
            
            # Test accuracy evaluation
            context = HookContext(
                hook_id="test-123",
                hook_type=HookType.PREHOOK,
                timestamp=datetime.now(),
                scope=MessageScope.USER,
                message=test_message,
                metadata={}
            )
            
            accuracy_result = evaluator.evaluate(test_message, context)
            assert accuracy_result.overall_score() >= 0.0
            print("   ✓ Accuracy evaluation working")
        
        # Test 6: Security checks
        print("6. Testing security functionality...")
        with tempfile.TemporaryDirectory() as temp_dir:
            from unified_framework.hooks.security import PIIDetector, VulnerabilityScanner
            
            pii_detector = PIIDetector()
            vuln_scanner = VulnerabilityScanner()
            
            # Test PII detection
            pii_content = "Contact me at test@example.com for more details"
            pii_result = pii_detector.detect_pii(pii_content)
            assert pii_result.found_pii
            print("   ✓ PII detection working")
            
            # Test vulnerability scanning
            vuln_content = 'password = "hardcoded123"'
            vuln_result = vuln_scanner.scan_content(vuln_content)
            assert len(vuln_result.vulnerabilities_found) > 0
            print("   ✓ Vulnerability scanning working")
        
        # Test 7: Link cataloging
        print("7. Testing link cataloging...")
        with tempfile.TemporaryDirectory() as temp_dir:
            from unified_framework.hooks.link_catalog import LinkExtractor
            
            extractor = LinkExtractor()
            
            # Test link extraction
            content_with_links = """
            Check out the documentation at https://docs.example.com
            And the repository at https://github.com/user/repo
            """
            
            links = extractor.extract_links(content_with_links)
            assert len(links) >= 2
            print("   ✓ Link extraction working")
        
        # Test 8: Vector operations
        print("8. Testing vector operations...")
        with tempfile.TemporaryDirectory() as temp_dir:
            from unified_framework.hooks.vector_rag import EmbeddingGenerator, SemanticChunker
            
            generator = EmbeddingGenerator()
            chunker = SemanticChunker()
            
            # Test embedding generation
            test_text = "This is a test for vector embedding generation"
            embedding = generator.generate_embedding(test_text)
            assert isinstance(embedding, list)
            assert len(embedding) == generator.embedding_dimension
            print("   ✓ Vector embedding generation working")
            
            # Test semantic chunking
            long_text = "This is a test document. " * 30
            chunks = chunker.chunk_content(long_text, "test-doc", "document")
            assert len(chunks) > 0
            print("   ✓ Semantic chunking working")
        
        print("\n=== All Basic Tests Passed! ===")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test system integration."""
    print("\nTesting system integration...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'config.json'
            
            # Setup configuration
            config_manager = ConfigurationManager(config_path)
            config = config_manager.get_config()
            config.storage.storage_root = str(Path(temp_dir) / 'hooks')
            config.debug_mode = True
            config_manager.save_config()
            
            # Initialize complete system
            system = initialize_hooks_system(config_path, auto_setup_integrations=True)
            
            hook_system = system['hook_system']
            components = system['components']
            
            print(f"✓ Initialized system with {len(components)} components")
            print(f"✓ Registered {len(hook_system.registry._hook_metadata)} hooks")
            
            # Test hook registry
            if 'integrations' in components:
                integration_manager = components['integrations']
                stats = integration_manager.get_integration_statistics()
                print(f"✓ Integration statistics available: {len(stats)} categories")
            
            # Test configuration access
            config = system['config']
            print(f"✓ Configuration loaded: {config.version}")
            
            return True
            
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_performance_check():
    """Run basic performance check."""
    print("\nRunning performance check...")
    
    import time
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            from unified_framework.hooks.prehook import SentimentAnalyzer
            from unified_framework.hooks.vector_rag import EmbeddingGenerator
            
            # Test sentiment analysis performance
            analyzer = SentimentAnalyzer()
            test_messages = [
                "This is a test message",
                "Urgent: Fix this bug immediately!",
                "Great work on the new feature",
                "Can you help me understand this code?",
                "The system is running slowly today"
            ]
            
            start_time = time.time()
            for message in test_messages * 10:  # 50 total
                analyzer.analyze(message)
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 50
            print(f"✓ Sentiment analysis: {avg_time:.4f}s average per message")
            
            # Test embedding generation performance
            generator = EmbeddingGenerator()
            
            start_time = time.time()
            for message in test_messages * 5:  # 25 total
                generator.generate_embedding(message)
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 25
            print(f"✓ Embedding generation: {avg_time:.4f}s average per message")
            
            return True
            
    except Exception as e:
        print(f"✗ Performance check failed: {e}")
        return False


if __name__ == "__main__":
    print("Claude Code Hooks System - Basic Validation")
    print("=" * 50)
    
    success = True
    
    # Run basic functionality tests
    if not test_basic_functionality():
        success = False
    
    # Run integration tests
    if not test_integration():
        success = False
    
    # Run performance check
    if not run_performance_check():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Hooks system is ready for use.")
        print("\nNext steps:")
        print("1. Initialize the system in your project:")
        print("   from unified_framework.hooks import initialize_hooks_system")
        print("   system = initialize_hooks_system()")
        print("2. Configure components as needed")
        print("3. Start processing messages through the hooks")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("=" * 50)