"""
Unit tests for FORCE Tool Parser
Linear Issue: PEG-883 (SB-002)
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from unified_framework.core.force_parser import (
    FORCEToolParser,
    FORCETool,
    FORCECategory,
    FORCEParameter,
    FORCEReturn,
    FORCEDependency,
    SchemaRegistry
)


class TestFORCEToolParser:
    """Test suite for FORCE Tool Parser"""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return FORCEToolParser()
    
    @pytest.fixture
    def sample_tool(self):
        """Sample FORCE tool data"""
        return {
            "tool_id": "force_tool_001",
            "name": "Data Transformer",
            "category": "tool",
            "version": "1.0.0",
            "description": "Transform data between formats",
            "command": "$transform",
            "parameters": [
                {
                    "name": "input",
                    "type": "string",
                    "required": True,
                    "description": "Input data"
                },
                {
                    "name": "format",
                    "type": "string",
                    "required": False,
                    "default": "json",
                    "description": "Output format"
                }
            ],
            "returns": {
                "type": "object",
                "description": "Transformed data"
            },
            "dependencies": [
                {
                    "tool_id": "force_parser_001",
                    "version": "1.0.0"
                }
            ],
            "variants": ["force_tool_001_xml", "force_tool_001_yaml"],
            "protocols": ["transformation", "data_processing"],
            "metadata": {
                "author": "test",
                "tags": ["data", "transform"]
            }
        }
    
    @pytest.fixture
    def sample_pattern(self):
        """Sample FORCE pattern data"""
        return {
            "tool_id": "force_pattern_001",
            "name": "Singleton Pattern",
            "category": "pattern",
            "version": "1.0.0",
            "description": "Singleton design pattern",
            "pattern_type": "creational",
            "template": "singleton.tpl"
        }
    
    @pytest.fixture
    def sample_constraint(self):
        """Sample FORCE constraint data"""
        return {
            "tool_id": "force_constraint_001",
            "name": "Rate Limiter",
            "category": "constraint",
            "version": "1.0.0",
            "constraints": [
                {"type": "rate_limit", "value": 100},
                {"type": "timeout", "value": 30}
            ]
        }
    
    def test_parser_initialization(self):
        """Test parser initializes correctly"""
        parser = FORCEToolParser()
        assert parser.registry is not None
        assert parser.tools == {}
        assert parser.YUNG_PREFIX == "$"
        
        # Check component counts
        assert parser.COMPONENT_COUNTS["tools"] == 50
        assert parser.COMPONENT_COUNTS["patterns"] == 25
        assert sum(parser.COMPONENT_COUNTS.values()) == 171
        
        # Check base schema is registered
        base_schema = parser.registry.get_schema("force", "force_tool_base")
        assert base_schema is not None
    
    def test_parse_valid_tool_file(self, parser, sample_tool, tmp_path):
        """Test parsing valid tool file"""
        file_path = tmp_path / "tool.json"
        file_path.write_text(json.dumps(sample_tool))
        
        tool = parser.parse(file_path)
        
        assert isinstance(tool, FORCETool)
        assert tool.tool_id == "force_tool_001"
        assert tool.name == "Data Transformer"
        assert tool.category == FORCECategory.TOOL
        assert tool.command == "$transform"
        assert len(tool.parameters) == 2
        assert len(tool.dependencies) == 1
    
    def test_parse_invalid_json_file(self, parser, tmp_path):
        """Test parsing invalid JSON file"""
        file_path = tmp_path / "invalid.json"
        file_path.write_text("{ invalid json }")
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            parser.parse(file_path)
    
    def test_parse_nonexistent_file(self, parser):
        """Test parsing non-existent file"""
        with pytest.raises(FileNotFoundError):
            parser.parse("/nonexistent/file.json")
    
    def test_parse_tool_from_dict(self, parser, sample_tool):
        """Test parsing tool from dictionary"""
        tool = parser.parse_tool(sample_tool)
        
        assert isinstance(tool, FORCETool)
        assert tool.tool_id == "force_tool_001"
        assert tool.name == "Data Transformer"
        
        # Check parameters are parsed correctly
        assert isinstance(tool.parameters[0], FORCEParameter)
        assert tool.parameters[0].name == "input"
        assert tool.parameters[0].required is True
        
        # Check returns is parsed
        assert isinstance(tool.returns, FORCEReturn)
        assert tool.returns.type == "object"
        
        # Check dependencies are parsed
        assert isinstance(tool.dependencies[0], FORCEDependency)
        assert tool.dependencies[0].tool_id == "force_parser_001"
        
        # Check tool is stored in registry
        assert parser.tools["force_tool_001"] == tool
    
    def test_parse_tool_invalid_structure(self, parser):
        """Test parsing tool with invalid structure"""
        invalid_tool = {"name": "Invalid"}  # Missing required fields
        
        with pytest.raises(ValueError, match="Invalid FORCE tool structure"):
            parser.parse_tool(invalid_tool)
    
    def test_validate_valid_tool(self, parser, sample_tool):
        """Test validating valid tool"""
        tool = parser.parse_tool(sample_tool)
        is_valid, error = parser.validate(tool)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_invalid_tool(self, parser):
        """Test validating invalid tool"""
        invalid_tool = {"name": "Invalid"}  # Missing required fields
        is_valid, error = parser.validate(invalid_tool)
        
        assert is_valid is False
        assert "tool_id" in error or "required" in error
    
    def test_detect_category_explicit(self, parser):
        """Test detecting category from explicit field"""
        assert parser.detect_category({"category": "tool"}) == FORCECategory.TOOL
        assert parser.detect_category({"category": "pattern"}) == FORCECategory.PATTERN
        assert parser.detect_category({"category": "constraint"}) == FORCECategory.CONSTRAINT
    
    def test_detect_category_by_fields(self, parser):
        """Test detecting category by field patterns"""
        assert parser.detect_category({"constraints": []}) == FORCECategory.CONSTRAINT
        assert parser.detect_category({"governance_rules": []}) == FORCECategory.GOVERNANCE
        assert parser.detect_category({"pattern_type": "creational"}) == FORCECategory.PATTERN
        assert parser.detect_category({"variant_of": "base"}) == FORCECategory.VARIANT
        assert parser.detect_category({"protocol_type": "http"}) == FORCECategory.PROTOCOL
        assert parser.detect_category({"transformation": {}}) == FORCECategory.TRANSFORMATION
        assert parser.detect_category({"validation_rules": []}) == FORCECategory.VALIDATION
        assert parser.detect_category({"workflow_steps": []}) == FORCECategory.WORKFLOW
        assert parser.detect_category({"integration_type": "api"}) == FORCECategory.INTEGRATION
    
    def test_detect_category_default(self, parser):
        """Test default category detection"""
        assert parser.detect_category({}) == FORCECategory.TOOL
        assert parser.detect_category({"random": "field"}) == FORCECategory.TOOL
    
    def test_extract_yung_command_explicit(self, parser, sample_tool):
        """Test extracting YUNG command from explicit field"""
        tool = parser.parse_tool(sample_tool)
        command = parser.extract_yung_command(tool)
        
        assert command == "$transform"
    
    def test_extract_yung_command_from_metadata(self, parser):
        """Test extracting YUNG command from metadata"""
        tool = FORCETool(
            tool_id="test",
            name="Test Tool",
            category=FORCECategory.TOOL,
            metadata={"yung_command": "test_command"}
        )
        
        command = parser.extract_yung_command(tool)
        assert command == "$test_command"
    
    def test_extract_yung_command_generated(self, parser):
        """Test generating YUNG command from tool name"""
        tool = FORCETool(
            tool_id="test",
            name="Data Processor",
            category=FORCECategory.TOOL
        )
        
        command = parser.extract_yung_command(tool)
        assert command == "$data_processor"
    
    def test_extract_parameters(self, parser, sample_tool):
        """Test extracting parameter definitions"""
        tool = parser.parse_tool(sample_tool)
        params = parser.extract_parameters(tool)
        
        assert "input" in params
        assert params["input"]["type"] == "string"
        assert params["input"]["required"] is True
        
        assert "format" in params
        assert params["format"]["default"] == "json"
    
    def test_extract_dependencies(self, parser, sample_tool):
        """Test extracting dependencies"""
        tool = parser.parse_tool(sample_tool)
        deps = parser.extract_dependencies(tool)
        
        assert len(deps) == 1
        assert "force_parser_001" in deps
    
    def test_resolve_dependency_chain_simple(self, parser):
        """Test resolving simple dependency chain"""
        # Create tools with dependencies
        tool1 = FORCETool(
            tool_id="tool1",
            name="Tool 1",
            category=FORCECategory.TOOL
        )
        tool2 = FORCETool(
            tool_id="tool2",
            name="Tool 2",
            category=FORCECategory.TOOL,
            dependencies=[FORCEDependency(tool_id="tool1")]
        )
        tool3 = FORCETool(
            tool_id="tool3",
            name="Tool 3",
            category=FORCECategory.TOOL,
            dependencies=[FORCEDependency(tool_id="tool2")]
        )
        
        parser.tools = {
            "tool1": tool1,
            "tool2": tool2,
            "tool3": tool3
        }
        
        chain = parser.resolve_dependency_chain("tool3")
        assert chain == ["tool1", "tool2"]
    
    def test_resolve_dependency_chain_circular(self, parser):
        """Test detecting circular dependencies"""
        # Create circular dependency
        tool1 = FORCETool(
            tool_id="tool1",
            name="Tool 1",
            category=FORCECategory.TOOL,
            dependencies=[FORCEDependency(tool_id="tool2")]
        )
        tool2 = FORCETool(
            tool_id="tool2",
            name="Tool 2",
            category=FORCECategory.TOOL,
            dependencies=[FORCEDependency(tool_id="tool1")]
        )
        
        parser.tools = {
            "tool1": tool1,
            "tool2": tool2
        }
        
        with pytest.raises(ValueError, match="Circular dependency"):
            parser.resolve_dependency_chain("tool1")
    
    def test_get_tools_by_category(self, parser):
        """Test getting tools by category"""
        tool1 = FORCETool(
            tool_id="t1",
            name="Tool",
            category=FORCECategory.TOOL
        )
        pattern1 = FORCETool(
            tool_id="p1",
            name="Pattern",
            category=FORCECategory.PATTERN
        )
        pattern2 = FORCETool(
            tool_id="p2",
            name="Pattern 2",
            category=FORCECategory.PATTERN
        )
        
        parser.tools = {"t1": tool1, "p1": pattern1, "p2": pattern2}
        
        tools = parser.get_tools_by_category(FORCECategory.TOOL)
        assert len(tools) == 1
        assert tools[0].tool_id == "t1"
        
        patterns = parser.get_tools_by_category(FORCECategory.PATTERN)
        assert len(patterns) == 2
    
    def test_get_tool_variants(self, parser):
        """Test getting tool variants"""
        base_tool = FORCETool(
            tool_id="base",
            name="Base Tool",
            category=FORCECategory.TOOL
        )
        variant1 = FORCETool(
            tool_id="v1",
            name="Variant 1",
            category=FORCECategory.VARIANT,
            variants=["base"]
        )
        variant2 = FORCETool(
            tool_id="v2",
            name="Variant 2",
            category=FORCECategory.VARIANT,
            metadata={"variant_of": "base"}
        )
        
        parser.tools = {
            "base": base_tool,
            "v1": variant1,
            "v2": variant2
        }
        
        variants = parser.get_tool_variants("base")
        assert len(variants) == 2
        assert any(v.tool_id == "v1" for v in variants)
        assert any(v.tool_id == "v2" for v in variants)
    
    def test_parse_batch(self, parser, sample_tool, sample_pattern, tmp_path):
        """Test parsing multiple tool files"""
        # Create test files
        (tmp_path / "tool1.json").write_text(json.dumps(sample_tool))
        (tmp_path / "pattern1.json").write_text(json.dumps(sample_pattern))
        (tmp_path / "invalid.txt").write_text("not json")
        
        tools = parser.parse_batch(tmp_path)
        
        assert len(tools) == 2
        assert "force_tool_001" in tools
        assert "force_pattern_001" in tools
    
    def test_parse_batch_nonexistent_directory(self, parser):
        """Test parsing batch from non-existent directory"""
        with pytest.raises(FileNotFoundError):
            parser.parse_batch("/nonexistent/dir")
    
    def test_export_to_schema_registry(self, parser, sample_tool):
        """Test exporting tools to schema registry"""
        tool = parser.parse_tool(sample_tool)
        parser.export_to_schema_registry()
        
        # Check that tool schema was registered
        tool_schema = parser.registry.get_schema("force", "force_tool_001")
        assert tool_schema is not None
        assert tool_schema.metadata.name == "force_tool_001"
        assert tool_schema.metadata.version == "1.0.0"
    
    def test_force_parameter_model(self):
        """Test FORCEParameter model"""
        param = FORCEParameter(
            name="test_param",
            type="string",
            required=True,
            default="default_value",
            description="Test parameter",
            constraints={"min_length": 5}
        )
        
        assert param.name == "test_param"
        assert param.required is True
        assert param.constraints["min_length"] == 5
    
    def test_force_return_model(self):
        """Test FORCEReturn model"""
        ret = FORCEReturn(
            type="array",
            description="List of results",
            schema={"items": {"type": "string"}}
        )
        
        assert ret.type == "array"
        assert ret.schema["items"]["type"] == "string"
    
    def test_force_dependency_model(self):
        """Test FORCEDependency model"""
        dep = FORCEDependency(
            tool_id="required_tool",
            version="2.0.0",
            required=False
        )
        
        assert dep.tool_id == "required_tool"
        assert dep.version == "2.0.0"
        assert dep.required is False
    
    def test_force_tool_model(self):
        """Test FORCETool model"""
        tool = FORCETool(
            tool_id="test_tool",
            name="Test Tool",
            category=FORCECategory.WORKFLOW,
            version="1.2.3",
            description="A test tool"
        )
        
        assert tool.tool_id == "test_tool"
        assert tool.category == FORCECategory.WORKFLOW
        assert tool.version == "1.2.3"
    
    @pytest.mark.parametrize("category,value", [
        (FORCECategory.TOOL, "tool"),
        (FORCECategory.PATTERN, "pattern"),
        (FORCECategory.CONSTRAINT, "constraint"),
        (FORCECategory.GOVERNANCE, "governance"),
        (FORCECategory.VARIANT, "variant"),
        (FORCECategory.PROTOCOL, "protocol"),
        (FORCECategory.TRANSFORMATION, "transformation"),
        (FORCECategory.VALIDATION, "validation"),
        (FORCECategory.INTEGRATION, "integration"),
        (FORCECategory.WORKFLOW, "workflow")
    ])
    def test_force_category_enum(self, category, value):
        """Test FORCECategory enum values"""
        assert category.value == value
    
    def test_integration_with_schema_registry(self):
        """Test integration with schema registry"""
        registry = SchemaRegistry()
        parser = FORCEToolParser(registry)
        
        # Check that base schema is registered
        schemas = registry.list_schemas(namespace="force")
        assert len(schemas) > 0
        
        base_schema = registry.get_schema("force", "force_tool_base")
        assert base_schema is not None