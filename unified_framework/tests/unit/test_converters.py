"""
Unit tests for IDFW-FORCE Converters
Linear Issues: PEG-884 (SB-003), PEG-885 (SB-004)
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from unified_framework.core.converters import (
    IDFWToFORCEConverter,
    FORCEToIDFWConverter,
    BidirectionalConverter
)
from unified_framework.core.force_parser import (
    FORCETool,
    FORCECategory,
    FORCEParameter,
    FORCEReturn,
    FORCEDependency
)


class TestIDFWToFORCEConverter:
    """Test suite for IDFW to FORCE converter"""
    
    @pytest.fixture
    def converter(self):
        """Create converter instance"""
        return IDFWToFORCEConverter()
    
    @pytest.fixture
    def sample_idfw_doc(self):
        """Sample IDFW documentation"""
        return {
            "docId": "IDDA-001",
            "title": "API Documentation",
            "version": "2.0.0",
            "revision": "_b2",
            "description": "REST API documentation for user service",
            "variables": {
                "api_version": "v2",
                "base_url": "https://api.example.com",
                "timeout": 30,
                "retry_count": 3
            },
            "tasks": [
                {
                    "taskId": "auth-task",
                    "name": "Authenticate User",
                    "params": {
                        "method": "POST",
                        "endpoint": "/auth"
                    }
                },
                {
                    "taskId": "fetch-task",
                    "name": "Fetch User Data",
                    "params": {
                        "method": "GET",
                        "endpoint": "/users/{id}"
                    }
                }
            ],
            "references": ["IDDA-002", "IDDG-001"],
            "metadata": {
                "author": "John Doe",
                "tags": ["api", "rest", "documentation"],
                "created_at": "2025-09-29T10:00:00Z"
            }
        }
    
    @pytest.fixture
    def sample_idfw_diagram(self):
        """Sample IDFW diagram"""
        return {
            "diagId": "IDDG-001",
            "title": "System Architecture",
            "version": "1.0.0",
            "diagramType": "architecture",
            "typeTool": "mermaid",
            "generatorLibId": "gen-mermaid-flow",
            "description": "High-level system architecture diagram"
        }
    
    @pytest.fixture
    def sample_idfw_project(self):
        """Sample IDFW project"""
        return {
            "docId": "IDPJ-001",
            "title": "IDFWU Project",
            "version": "2.1.1",
            "projectName": "IDFWU",
            "description": "Unified framework project",
            "tasks": [
                {"taskId": "T1", "name": "Initialize"},
                {"taskId": "T2", "name": "Build"}
            ],
            "metadata": {
                "status": "active"
            }
        }
    
    def test_converter_initialization(self):
        """Test converter initializes correctly"""
        converter = IDFWToFORCEConverter()
        assert converter.strict_mode is True
        assert converter.stats["documents_converted"] == 0
        assert converter.stats["conversion_errors"] == 0
    
    def test_convert_basic_document(self, converter, sample_idfw_doc):
        """Test converting basic IDFW document to FORCE tool"""
        force_tool = converter.convert_document(sample_idfw_doc)
        
        assert isinstance(force_tool, FORCETool)
        assert force_tool.tool_id == "IDDA-001"
        assert force_tool.name == "API Documentation"
        assert force_tool.version == "2.0.0"
        assert force_tool.description == "REST API documentation for user service"
        assert force_tool.category == FORCECategory.TOOL
    
    def test_convert_variables_to_parameters(self, converter, sample_idfw_doc):
        """Test converting IDFW variables to FORCE parameters"""
        force_tool = converter.convert_document(sample_idfw_doc)
        
        assert len(force_tool.parameters) == 4
        
        # Check immutable parameters (version/url)
        api_version_param = next(p for p in force_tool.parameters if p.name == "api_version")
        assert api_version_param.type == "string"
        assert api_version_param.default == "v2"
        assert api_version_param.required is False
        
        # Check mutable parameters
        timeout_param = next(p for p in force_tool.parameters if p.name == "timeout")
        assert timeout_param.type == "integer"
        assert timeout_param.default == 30
    
    def test_convert_tasks_to_workflow(self, converter, sample_idfw_doc):
        """Test converting IDFW tasks to FORCE workflow steps"""
        force_tool = converter.convert_document(sample_idfw_doc)
        
        assert "workflow_steps" in force_tool.metadata
        assert len(force_tool.metadata["workflow_steps"]) == 2
        
        auth_step = force_tool.metadata["workflow_steps"][0]
        assert auth_step["id"] == "auth-task"
        assert auth_step["name"] == "Authenticate User"
        assert auth_step["params"]["method"] == "POST"
    
    def test_convert_references_to_dependencies(self, converter, sample_idfw_doc):
        """Test converting IDFW references to FORCE dependencies"""
        force_tool = converter.convert_document(sample_idfw_doc)
        
        assert len(force_tool.dependencies) == 2
        assert force_tool.dependencies[0].tool_id == "IDDA-002"
        assert force_tool.dependencies[1].tool_id == "IDDG-001"
    
    def test_convert_metadata_preservation(self, converter, sample_idfw_doc):
        """Test metadata is preserved during conversion"""
        force_tool = converter.convert_document(sample_idfw_doc)
        
        assert force_tool.metadata["author"] == "John Doe"
        assert "api" in force_tool.metadata["tags"]
        assert force_tool.metadata["created_at"] == "2025-09-29T10:00:00Z"
        assert force_tool.metadata["revision"] == "_b2"
    
    def test_convert_diagram_category(self, converter, sample_idfw_diagram):
        """Test diagram converts to pattern category"""
        force_tool = converter.convert_document(sample_idfw_diagram)
        
        assert force_tool.category == FORCECategory.PATTERN
        assert force_tool.metadata["pattern_type"] == "architecture"
        assert force_tool.metadata["typeTool"] == "mermaid"
    
    def test_convert_project_category(self, converter, sample_idfw_project):
        """Test project converts to workflow category"""
        force_tool = converter.convert_document(sample_idfw_project)
        
        assert force_tool.category == FORCECategory.WORKFLOW
        assert force_tool.metadata["projectName"] == "IDFWU"
        assert len(force_tool.metadata["workflow_steps"]) == 2
    
    def test_convert_with_missing_optional_fields(self, converter):
        """Test conversion with minimal IDFW document"""
        minimal_doc = {
            "title": "Minimal Doc",
            "version": "1.0.0"
        }
        
        force_tool = converter.convert_document(minimal_doc)
        
        assert force_tool.tool_id.startswith("idfw_")
        assert force_tool.name == "Minimal Doc"
        assert force_tool.parameters == []
        assert force_tool.dependencies == []
    
    def test_convert_invalid_document_strict_mode(self, converter):
        """Test strict mode raises error for invalid document"""
        invalid_doc = {"invalid": "document"}
        
        with pytest.raises(ValueError, match="Missing required fields"):
            converter.convert_document(invalid_doc)
    
    def test_convert_invalid_document_lenient_mode(self):
        """Test lenient mode handles invalid document gracefully"""
        converter = IDFWToFORCEConverter(strict_mode=False)
        invalid_doc = {"invalid": "document"}
        
        force_tool = converter.convert_document(invalid_doc)
        
        assert force_tool.name == "Untitled"
        assert force_tool.version == "1.0.0"
        assert converter.stats["conversion_errors"] == 0
    
    def test_conversion_statistics(self, converter, sample_idfw_doc):
        """Test conversion statistics tracking"""
        converter.convert_document(sample_idfw_doc)
        
        assert converter.stats["documents_converted"] == 1
        assert converter.stats["parameters_created"] == 4
        assert converter.stats["dependencies_created"] == 2
        
        # Convert another document
        converter.convert_document(sample_idfw_doc)
        assert converter.stats["documents_converted"] == 2
    
    def test_detect_parameter_type(self, converter):
        """Test parameter type detection"""
        assert converter._detect_parameter_type("123") == "integer"
        assert converter._detect_parameter_type(123) == "integer"
        assert converter._detect_parameter_type(123.45) == "number"
        assert converter._detect_parameter_type(True) == "boolean"
        assert converter._detect_parameter_type("hello") == "string"
        assert converter._detect_parameter_type([1, 2, 3]) == "array"
        assert converter._detect_parameter_type({"key": "value"}) == "object"
    
    def test_map_idfw_to_force_category(self, converter):
        """Test category mapping"""
        assert converter._map_idfw_to_force_category("documentation") == FORCECategory.TOOL
        assert converter._map_idfw_to_force_category("diagram") == FORCECategory.PATTERN
        assert converter._map_idfw_to_force_category("project") == FORCECategory.WORKFLOW
        assert converter._map_idfw_to_force_category("generator") == FORCECategory.TRANSFORMATION
        assert converter._map_idfw_to_force_category("config") == FORCECategory.CONSTRAINT
        assert converter._map_idfw_to_force_category("variable") == FORCECategory.VALIDATION


class TestFORCEToIDFWConverter:
    """Test suite for FORCE to IDFW converter"""
    
    @pytest.fixture
    def converter(self):
        """Create converter instance"""
        return FORCEToIDFWConverter()
    
    @pytest.fixture
    def sample_force_tool(self):
        """Sample FORCE tool"""
        return FORCETool(
            tool_id="force_tool_001",
            name="Data Transformer",
            category=FORCECategory.TOOL,
            version="1.5.0",
            description="Transform data between formats",
            command="$transform",
            parameters=[
                FORCEParameter(
                    name="input_format",
                    type="string",
                    required=True,
                    description="Input data format"
                ),
                FORCEParameter(
                    name="output_format",
                    type="string",
                    required=True,
                    default="json",
                    description="Output data format"
                ),
                FORCEParameter(
                    name="validate",
                    type="boolean",
                    required=False,
                    default=True
                )
            ],
            returns=FORCEReturn(
                type="object",
                description="Transformed data"
            ),
            dependencies=[
                FORCEDependency(tool_id="force_parser_001", version="1.0.0"),
                FORCEDependency(tool_id="force_validator_001")
            ],
            metadata={
                "author": "Jane Smith",
                "tags": ["transform", "data"],
                "created_at": "2025-09-29T12:00:00Z"
            }
        )
    
    @pytest.fixture
    def sample_force_pattern(self):
        """Sample FORCE pattern"""
        return FORCETool(
            tool_id="force_pattern_001",
            name="Singleton Pattern",
            category=FORCECategory.PATTERN,
            version="1.0.0",
            description="Singleton design pattern",
            metadata={
                "pattern_type": "creational",
                "template": "singleton.tpl"
            }
        )
    
    def test_converter_initialization(self):
        """Test converter initializes correctly"""
        converter = FORCEToIDFWConverter()
        assert converter.strict_mode is True
        assert converter.stats["tools_converted"] == 0
        assert converter.stats["conversion_errors"] == 0
    
    def test_convert_basic_tool(self, converter, sample_force_tool):
        """Test converting basic FORCE tool to IDFW document"""
        idfw_doc = converter.convert_tool(sample_force_tool)
        
        assert idfw_doc["docId"] == "force_tool_001"
        assert idfw_doc["title"] == "Data Transformer"
        assert idfw_doc["version"] == "1.5.0"
        assert idfw_doc["description"] == "Transform data between formats"
    
    def test_convert_parameters_to_variables(self, converter, sample_force_tool):
        """Test converting FORCE parameters to IDFW variables"""
        idfw_doc = converter.convert_tool(sample_force_tool)
        
        assert "variables" in idfw_doc
        variables = idfw_doc["variables"]
        
        # Check immutable variables (required params)
        assert "immutable" in variables
        assert variables["immutable"]["input_format"]["value"] is None
        assert variables["immutable"]["input_format"]["description"] == "Input data format"
        
        # Check mutable variables (optional params)
        assert "mutable" in variables
        assert variables["mutable"]["output_format"]["value"] == "json"
        assert variables["mutable"]["validate"]["value"] is True
    
    def test_convert_dependencies_to_references(self, converter, sample_force_tool):
        """Test converting FORCE dependencies to IDFW references"""
        idfw_doc = converter.convert_tool(sample_force_tool)
        
        assert "references" in idfw_doc
        assert len(idfw_doc["references"]) == 2
        assert "force_parser_001" in idfw_doc["references"]
        assert "force_validator_001" in idfw_doc["references"]
    
    def test_convert_metadata_preservation(self, converter, sample_force_tool):
        """Test metadata is preserved during conversion"""
        idfw_doc = converter.convert_tool(sample_force_tool)
        
        assert idfw_doc["metadata"]["author"] == "Jane Smith"
        assert "transform" in idfw_doc["metadata"]["tags"]
        assert idfw_doc["metadata"]["created_at"] == "2025-09-29T12:00:00Z"
        assert idfw_doc["metadata"]["command"] == "$transform"
    
    def test_convert_pattern_to_diagram(self, converter, sample_force_pattern):
        """Test pattern converts to diagram document type"""
        idfw_doc = converter.convert_tool(sample_force_pattern)
        
        assert idfw_doc["docId"] == "force_pattern_001"
        assert idfw_doc["diagramType"] == "creational"
        assert idfw_doc["metadata"]["template"] == "singleton.tpl"
    
    def test_convert_workflow_to_project(self, converter):
        """Test workflow converts to project document type"""
        workflow = FORCETool(
            tool_id="workflow_001",
            name="Build Pipeline",
            category=FORCECategory.WORKFLOW,
            version="1.0.0",
            metadata={
                "workflow_steps": [
                    {"id": "step1", "name": "Compile"},
                    {"id": "step2", "name": "Test"}
                ]
            }
        )
        
        idfw_doc = converter.convert_tool(workflow)
        
        assert idfw_doc["projectName"] == "Build Pipeline"
        assert len(idfw_doc["tasks"]) == 2
        assert idfw_doc["tasks"][0]["taskId"] == "step1"
    
    def test_convert_with_missing_optional_fields(self, converter):
        """Test conversion with minimal FORCE tool"""
        minimal_tool = FORCETool(
            tool_id="minimal_001",
            name="Minimal Tool",
            category=FORCECategory.TOOL
        )
        
        idfw_doc = converter.convert_tool(minimal_tool)
        
        assert idfw_doc["docId"] == "minimal_001"
        assert idfw_doc["title"] == "Minimal Tool"
        assert idfw_doc["version"] == "1.0.0"
        assert idfw_doc.get("variables") == {}
    
    def test_convert_from_dict(self, converter):
        """Test converting from dictionary instead of FORCETool object"""
        tool_dict = {
            "tool_id": "dict_tool",
            "name": "Dictionary Tool",
            "category": "tool",
            "version": "2.0.0"
        }
        
        idfw_doc = converter.convert_tool(tool_dict)
        
        assert idfw_doc["docId"] == "dict_tool"
        assert idfw_doc["title"] == "Dictionary Tool"
        assert idfw_doc["version"] == "2.0.0"
    
    def test_convert_invalid_tool_strict_mode(self, converter):
        """Test strict mode raises error for invalid tool"""
        with pytest.raises(ValueError, match="Invalid FORCE tool"):
            converter.convert_tool({"invalid": "tool"})
    
    def test_convert_invalid_tool_lenient_mode(self):
        """Test lenient mode handles invalid tool gracefully"""
        converter = FORCEToIDFWConverter(strict_mode=False)
        
        idfw_doc = converter.convert_tool({"invalid": "tool"})
        
        assert idfw_doc["docId"].startswith("force_")
        assert idfw_doc["title"] == "Untitled"
        assert converter.stats["conversion_errors"] == 0
    
    def test_conversion_statistics(self, converter, sample_force_tool):
        """Test conversion statistics tracking"""
        converter.convert_tool(sample_force_tool)
        
        assert converter.stats["tools_converted"] == 1
        assert converter.stats["variables_created"] == 3
        assert converter.stats["references_created"] == 2
    
    def test_generate_idfw_doc_id(self, converter):
        """Test IDFW document ID generation"""
        # Test with explicit ID
        assert converter._generate_idfw_doc_id("test_id", "documentation") == "test_id"
        
        # Test ID generation by category
        assert converter._generate_idfw_doc_id(None, "documentation").startswith("IDDA-")
        assert converter._generate_idfw_doc_id(None, "diagram").startswith("IDDG-")
        assert converter._generate_idfw_doc_id(None, "project").startswith("IDPJ-")
    
    def test_map_force_to_idfw_type(self, converter):
        """Test category to document type mapping"""
        assert converter._map_force_to_idfw_type(FORCECategory.TOOL) == "documentation"
        assert converter._map_force_to_idfw_type(FORCECategory.PATTERN) == "diagram"
        assert converter._map_force_to_idfw_type(FORCECategory.WORKFLOW) == "project"
        assert converter._map_force_to_idfw_type(FORCECategory.TRANSFORMATION) == "generator"
        assert converter._map_force_to_idfw_type(FORCECategory.CONSTRAINT) == "config"
        assert converter._map_force_to_idfw_type(FORCECategory.VALIDATION) == "variable"


class TestBidirectionalConverter:
    """Test suite for bidirectional converter"""
    
    @pytest.fixture
    def converter(self):
        """Create bidirectional converter instance"""
        return BidirectionalConverter()
    
    @pytest.fixture
    def sample_idfw_doc(self):
        """Sample IDFW document"""
        return {
            "docId": "IDDA-100",
            "title": "Test Document",
            "version": "1.0.0",
            "description": "Test description",
            "variables": {
                "var1": "value1",
                "var2": 42
            },
            "references": ["IDDA-101"],
            "metadata": {
                "author": "Test Author"
            }
        }
    
    @pytest.fixture
    def sample_force_tool(self):
        """Sample FORCE tool"""
        return {
            "tool_id": "force_100",
            "name": "Test Tool",
            "category": "tool",
            "version": "1.0.0",
            "description": "Test description",
            "parameters": [
                {
                    "name": "param1",
                    "type": "string",
                    "required": True
                }
            ],
            "dependencies": [
                {"tool_id": "force_101"}
            ],
            "metadata": {
                "author": "Test Author"
            }
        }
    
    def test_converter_initialization(self):
        """Test bidirectional converter initializes correctly"""
        converter = BidirectionalConverter()
        assert converter.idfw_to_force is not None
        assert converter.force_to_idfw is not None
        assert converter.round_trip_stats["successful"] == 0
        assert converter.round_trip_stats["failed"] == 0
    
    def test_convert_idfw_to_force(self, converter, sample_idfw_doc):
        """Test IDFW to FORCE conversion through bidirectional converter"""
        result = converter.convert(sample_idfw_doc, "idfw", "force")
        
        assert isinstance(result, FORCETool)
        assert result.tool_id == "IDDA-100"
        assert result.name == "Test Document"
    
    def test_convert_force_to_idfw(self, converter, sample_force_tool):
        """Test FORCE to IDFW conversion through bidirectional converter"""
        result = converter.convert(sample_force_tool, "force", "idfw")
        
        assert isinstance(result, dict)
        assert result["docId"] == "force_100"
        assert result["title"] == "Test Tool"
    
    def test_convert_invalid_source_format(self, converter, sample_idfw_doc):
        """Test invalid source format raises error"""
        with pytest.raises(ValueError, match="Invalid source format"):
            converter.convert(sample_idfw_doc, "invalid", "force")
    
    def test_convert_invalid_target_format(self, converter, sample_idfw_doc):
        """Test invalid target format raises error"""
        with pytest.raises(ValueError, match="Invalid target format"):
            converter.convert(sample_idfw_doc, "idfw", "invalid")
    
    def test_convert_same_format(self, converter, sample_idfw_doc):
        """Test converting to same format returns original"""
        result = converter.convert(sample_idfw_doc, "idfw", "idfw")
        assert result == sample_idfw_doc
    
    def test_round_trip_idfw_to_idfw(self, converter, sample_idfw_doc):
        """Test round-trip conversion from IDFW"""
        is_valid, message = converter.validate_round_trip(sample_idfw_doc, "idfw")
        
        assert is_valid is True
        assert message is None
        assert converter.round_trip_stats["successful"] == 1
    
    def test_round_trip_force_to_force(self, converter, sample_force_tool):
        """Test round-trip conversion from FORCE"""
        is_valid, message = converter.validate_round_trip(sample_force_tool, "force")
        
        assert is_valid is True
        assert message is None
        assert converter.round_trip_stats["successful"] == 1
    
    def test_round_trip_with_data_loss(self, converter):
        """Test round-trip validation detects data loss"""
        # Create a document with fields that won't survive round-trip
        doc_with_loss = {
            "docId": "IDDA-200",
            "title": "Test",
            "version": "1.0.0",
            "custom_field": "This will be lost"  # Non-standard field
        }
        
        is_valid, message = converter.validate_round_trip(doc_with_loss, "idfw")
        
        # Should still be valid but with warnings
        assert is_valid is True
        assert converter.round_trip_stats["successful"] == 1
    
    def test_round_trip_with_complex_structure(self, converter):
        """Test round-trip with complex nested structures"""
        complex_doc = {
            "docId": "IDDA-300",
            "title": "Complex Document",
            "version": "2.0.0",
            "variables": {
                "immutable": {
                    "api_key": "secret",
                    "version": "1.0"
                },
                "mutable": {
                    "counter": 0,
                    "flags": {"debug": True, "verbose": False}
                }
            },
            "tasks": [
                {"taskId": "t1", "name": "Task 1", "params": {"p": "v"}},
                {"taskId": "t2", "name": "Task 2"}
            ],
            "references": ["IDDA-301", "IDDG-302", "IDPJ-303"],
            "metadata": {
                "nested": {
                    "deeply": {
                        "value": "preserved"
                    }
                }
            }
        }
        
        is_valid, message = converter.validate_round_trip(complex_doc, "idfw")
        assert is_valid is True
    
    def test_batch_conversion(self, converter):
        """Test batch conversion of multiple documents"""
        documents = [
            {"docId": f"IDDA-{i}", "title": f"Doc {i}", "version": "1.0.0"}
            for i in range(5)
        ]
        
        results = converter.convert_batch(documents, "idfw", "force")
        
        assert len(results) == 5
        for i, result in enumerate(results):
            assert isinstance(result, FORCETool)
            assert result.tool_id == f"IDDA-{i}"
    
    def test_conversion_with_lenient_mode(self):
        """Test lenient mode in bidirectional converter"""
        converter = BidirectionalConverter(strict_mode=False)
        
        # Invalid document that would fail in strict mode
        invalid_doc = {"title": "Missing version"}
        
        # Should not raise error in lenient mode
        result = converter.convert(invalid_doc, "idfw", "force")
        assert isinstance(result, FORCETool)
        assert result.version == "1.0.0"  # Default version
    
    def test_get_conversion_report(self, converter, sample_idfw_doc, sample_force_tool):
        """Test conversion statistics report"""
        # Perform some conversions
        converter.convert(sample_idfw_doc, "idfw", "force")
        converter.convert(sample_force_tool, "force", "idfw")
        converter.validate_round_trip(sample_idfw_doc, "idfw")
        
        report = converter.get_conversion_report()
        
        assert "IDFW to FORCE Statistics" in report
        assert "FORCE to IDFW Statistics" in report
        assert "Round-Trip Validation" in report
        assert "documents_converted: 1" in report
        assert "tools_converted: 1" in report
        assert "Successful: 1" in report


class TestIntegrationScenarios:
    """Integration tests for real-world conversion scenarios"""
    
    @pytest.fixture
    def bidirectional(self):
        """Create bidirectional converter"""
        return BidirectionalConverter()
    
    def test_full_project_conversion(self, bidirectional):
        """Test converting a full IDFWU project structure"""
        project = {
            "docId": "IDPJ-IDFWU",
            "title": "IDFWU Framework",
            "version": "2.1.1",
            "projectName": "IDFWU",
            "description": "Unified framework for IDFW and FORCE integration",
            "tasks": [
                {"taskId": "init", "name": "Initialize Project"},
                {"taskId": "parse", "name": "Parse Documents"},
                {"taskId": "convert", "name": "Convert Schemas"},
                {"taskId": "validate", "name": "Validate Output"}
            ],
            "variables": {
                "framework_version": "2.1.1",
                "supported_formats": ["idfw", "force"],
                "max_file_size": 10485760
            },
            "references": [
                "IDDA-001", "IDDA-002", "IDDG-001",
                "force_tool_001", "force_pattern_001"
            ],
            "metadata": {
                "created_at": "2025-09-29T00:00:00Z",
                "maintainers": ["John Doe", "Jane Smith"],
                "repository": "https://github.com/peguesj/idfwu",
                "linear_project": "4d649a6501f7"
            }
        }
        
        # Convert to FORCE
        force_tool = bidirectional.convert(project, "idfw", "force")
        
        assert force_tool.category == FORCECategory.WORKFLOW
        assert len(force_tool.metadata["workflow_steps"]) == 4
        assert len(force_tool.parameters) == 3
        assert len(force_tool.dependencies) == 5
        
        # Convert back to IDFW
        idfw_back = bidirectional.convert(force_tool, "force", "idfw")
        
        assert idfw_back["projectName"] == "IDFWU Framework"
        assert len(idfw_back["tasks"]) == 4
        
        # Validate round-trip
        is_valid, _ = bidirectional.validate_round_trip(project, "idfw")
        assert is_valid is True
    
    def test_dev_sentinel_command_preservation(self, bidirectional):
        """Test YUNG command preservation through conversion"""
        force_tool = {
            "tool_id": "sentinel_cmd_001",
            "name": "Build Command",
            "category": "tool",
            "version": "1.0.0",
            "command": "$build",
            "parameters": [
                {"name": "target", "type": "string", "required": True},
                {"name": "env", "type": "string", "default": "production"}
            ],
            "metadata": {
                "yung_prefix": "$",
                "sentinel_category": "build"
            }
        }
        
        # Convert to IDFW
        idfw_doc = bidirectional.convert(force_tool, "force", "idfw")
        assert idfw_doc["metadata"]["command"] == "$build"
        
        # Convert back to FORCE
        force_back = bidirectional.convert(idfw_doc, "idfw", "force")
        assert force_back.command == "$build"
    
    def test_complex_dependency_chain(self, bidirectional):
        """Test complex dependency chains are preserved"""
        tool_with_deps = {
            "tool_id": "complex_tool",
            "name": "Complex Tool",
            "category": "tool",
            "version": "3.0.0",
            "dependencies": [
                {"tool_id": "dep1", "version": "1.0.0", "required": True},
                {"tool_id": "dep2", "version": "2.0.0", "required": False},
                {"tool_id": "dep3", "version": "1.5.0"},
                {"tool_id": "dep4"}
            ]
        }
        
        # Round-trip conversion
        idfw = bidirectional.convert(tool_with_deps, "force", "idfw")
        force_back = bidirectional.convert(idfw, "idfw", "force")
        
        # Check all dependencies preserved
        assert len(force_back.dependencies) == 4
        dep_ids = [d.tool_id for d in force_back.dependencies]
        assert "dep1" in dep_ids
        assert "dep2" in dep_ids
        assert "dep3" in dep_ids
        assert "dep4" in dep_ids
    
    def test_error_handling_and_recovery(self, bidirectional):
        """Test error handling in conversion pipeline"""
        # Malformed document
        malformed = {
            "docId": None,  # Invalid ID
            "title": "",    # Empty title
            "version": "invalid",  # Invalid version format
        }
        
        # Should handle gracefully in lenient mode
        lenient_converter = BidirectionalConverter(strict_mode=False)
        result = lenient_converter.convert(malformed, "idfw", "force")
        
        assert result.tool_id.startswith("idfw_")  # Generated ID
        assert result.name == "Untitled"  # Default name
        assert result.version == "1.0.0"  # Default version
    
    @pytest.mark.parametrize("doc_type,expected_category", [
        ("documentation", FORCECategory.TOOL),
        ("diagram", FORCECategory.PATTERN),
        ("project", FORCECategory.WORKFLOW),
        ("generator", FORCECategory.TRANSFORMATION),
        ("config", FORCECategory.CONSTRAINT),
        ("variable", FORCECategory.VALIDATION)
    ])
    def test_all_document_type_mappings(self, bidirectional, doc_type, expected_category):
        """Test all IDFW document types map correctly"""
        doc = {
            "docId": f"{doc_type.upper()}-001",
            "title": f"{doc_type} Test",
            "version": "1.0.0",
            "metadata": {"document_type": doc_type}
        }
        
        # Add type-specific fields
        if doc_type == "diagram":
            doc["diagramType"] = "flow"
        elif doc_type == "project":
            doc["projectName"] = "Test"
        elif doc_type == "generator":
            doc["promptText"] = "Generate"
        elif doc_type == "config":
            doc["apiKeys"] = {}
        elif doc_type == "variable":
            doc["variables"] = {"immutable": {}, "mutable": {}}
        
        force_tool = bidirectional.convert(doc, "idfw", "force")
        assert force_tool.category == expected_category