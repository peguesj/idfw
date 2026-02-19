"""
Unit tests for IDFW Document Parser
Linear Issue: PEG-882 (SB-001)
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from unified_framework.core.schema_bridge import (
    IDFWDocumentParser,
    SchemaRegistry,
    SchemaFormat,
    SchemaNamespace
)


class TestIDFWDocumentParser:
    """Test suite for IDFW Document Parser"""

    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return IDFWDocumentParser()

    @pytest.fixture
    def sample_document(self):
        """Sample IDFW document data"""
        return {
            "docId": "IDDA-001",
            "title": "Test Document",
            "version": "1.0.0",
            "revision": "_a1",
            "description": "Test description",
            "variables": {
                "project_name": "Test Project",
                "author": "Test Author"
            },
            "metadata": {
                "created_at": "2025-09-29T00:00:00Z",
                "status": "draft"
            },
            "references": ["IDDA-002", "IDDG-001"],
            "tasks": [
                {
                    "taskId": "task-001",
                    "name": "Generate Documentation",
                    "params": {"format": "markdown"}
                }
            ]
        }

    @pytest.fixture
    def sample_diagram(self):
        """Sample IDFW diagram data"""
        return {
            "diagId": "IDDG-001",
            "title": "System Architecture",
            "version": "1.0.0",
            "diagramType": "architecture",
            "typeTool": "mermaid",
            "generatorLibId": "gen-mermaid-flow"
        }

    @pytest.fixture
    def sample_project(self):
        """Sample IDFW project data"""
        return {
            "docId": "IDPJ-001",
            "title": "IDFWU Project",
            "version": "2.1.1",
            "projectName": "IDFWU",
            "tasks": [
                {"taskId": "T1", "name": "Initialize"},
                {"taskId": "T2", "name": "Build"}
            ]
        }

    def test_parser_initialization(self):
        """Test parser initializes correctly"""
        parser = IDFWDocumentParser()
        assert parser.registry is not None
        assert len(parser.DOCUMENT_TYPES) == 6
        
        # Check that base schema is registered
        base_schema = parser.registry.get_schema("idfw", "idfw_document_base")
        assert base_schema is not None
        assert base_schema.metadata.version == "2.1.1"

    def test_parse_valid_json_file(self, parser, sample_document, tmp_path):
        """Test parsing valid JSON file"""
        # Create temporary file
        file_path = tmp_path / "test_doc.json"
        file_path.write_text(json.dumps(sample_document))
        
        # Parse file
        data = parser.parse(file_path)
        
        assert data["title"] == "Test Document"
        assert data["version"] == "1.0.0"
        assert "variables" in data

    def test_parse_invalid_json_file(self, parser, tmp_path):
        """Test parsing invalid JSON file"""
        # Create file with invalid JSON
        file_path = tmp_path / "invalid.json"
        file_path.write_text("{ invalid json }")
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            parser.parse(file_path)

    def test_parse_nonexistent_file(self, parser):
        """Test parsing non-existent file"""
        with pytest.raises(FileNotFoundError):
            parser.parse("/nonexistent/file.json")

    def test_validate_valid_document(self, parser, sample_document):
        """Test validating valid IDFW document"""
        is_valid, error = parser.validate(sample_document)
        assert is_valid is True
        assert error is None

    def test_validate_invalid_document_missing_required(self, parser):
        """Test validating document missing required fields"""
        invalid_doc = {"description": "Missing title and version"}
        is_valid, error = parser.validate(invalid_doc)
        assert is_valid is False
        assert "title" in error.lower() or "required" in error.lower()

    def test_validate_invalid_version_format(self, parser, sample_document):
        """Test validating document with invalid version format"""
        sample_document["version"] = "1.0"  # Should be X.Y.Z
        is_valid, error = parser.validate(sample_document)
        assert is_valid is False
        assert "version" in error.lower() or "pattern" in error.lower()

    def test_detect_document_type_by_doc_id(self, parser):
        """Test detecting document type by docId prefix"""
        assert parser.detect_document_type({"docId": "IDDA-001"}) == "documentation"
        assert parser.detect_document_type({"docId": "IDDG-001"}) == "diagram"
        assert parser.detect_document_type({"docId": "IDPJ-001"}) == "project"
        assert parser.detect_document_type({"docId": "IDPG-001"}) == "generator"
        assert parser.detect_document_type({"docId": "IDPC-001"}) == "config"
        assert parser.detect_document_type({"docId": "IDFV-001"}) == "variable"

    def test_detect_document_type_by_fields(self, parser):
        """Test detecting document type by specific fields"""
        assert parser.detect_document_type({"diagramType": "flow"}) == "diagram"
        assert parser.detect_document_type({"typeTool": "mermaid"}) == "diagram"
        assert parser.detect_document_type({"promptText": "Generate"}) == "generator"
        assert parser.detect_document_type({"apiKeys": {}}) == "config"
        assert parser.detect_document_type({"projectName": "Test"}) == "project"
        assert parser.detect_document_type({
            "variables": {"immutable": {}, "mutable": {}}
        }) == "variable"

    def test_detect_document_type_default(self, parser):
        """Test default document type detection"""
        assert parser.detect_document_type({}) == "documentation"
        assert parser.detect_document_type({"title": "Test"}) == "documentation"

    def test_extract_metadata(self, parser, sample_document):
        """Test extracting metadata from document"""
        metadata = parser.extract_metadata(sample_document)
        
        assert metadata["title"] == "Test Document"
        assert metadata["version"] == "1.0.0"
        assert metadata["revision"] == "_a1"
        assert metadata["document_type"] == "documentation"
        assert metadata["has_variables"] is True
        assert metadata["has_tasks"] is True
        assert metadata["has_references"] is True
        assert metadata["status"] == "draft"

    def test_extract_metadata_defaults(self, parser):
        """Test extracting metadata with defaults"""
        metadata = parser.extract_metadata({})
        
        assert metadata["title"] == "Untitled"
        assert metadata["version"] == "1.0.0"
        assert metadata["revision"] == "_a1"
        assert metadata["has_variables"] is False
        assert metadata["has_tasks"] is False
        assert metadata["has_references"] is False

    def test_extract_variables_flat(self, parser):
        """Test extracting flat variables structure"""
        data = {
            "variables": {
                "project_version": "1.0.0",
                "author_name": "John Doe",
                "max_retries": 3,
                "enable_debug": True
            }
        }
        
        variables = parser.extract_variables(data)
        
        # Version and author should be immutable
        assert "project_version" in variables["immutable"]
        assert "author_name" in variables["immutable"]
        
        # Others should be mutable
        assert "max_retries" in variables["mutable"]
        assert "enable_debug" in variables["mutable"]

    def test_extract_variables_categorized(self, parser):
        """Test extracting pre-categorized variables"""
        data = {
            "variables": {
                "immutable": {
                    "project_id": "123",
                    "created_date": "2025-09-29"
                },
                "mutable": {
                    "status": "active",
                    "counter": 0
                }
            }
        }
        
        variables = parser.extract_variables(data)
        
        assert variables["immutable"]["project_id"] == "123"
        assert variables["mutable"]["status"] == "active"

    def test_extract_variables_empty(self, parser):
        """Test extracting variables when none exist"""
        variables = parser.extract_variables({})
        
        assert variables == {}

    def test_parse_nested_references_strings(self, parser):
        """Test parsing string references"""
        data = {
            "references": ["DOC-001", "DOC-002", "DIAG-001"]
        }
        
        refs = parser.parse_nested_references(data)
        
        assert len(refs) == 3
        assert refs[0]["type"] == "document"
        assert refs[0]["id"] == "DOC-001"
        assert refs[0]["resolved"] is False

    def test_parse_nested_references_objects(self, parser):
        """Test parsing object references"""
        data = {
            "references": [
                {
                    "type": "diagram",
                    "id": "DIAG-001",
                    "version": "2.0.0",
                    "resolved": True
                },
                {
                    "docId": "DOC-003",
                    "type": "document"
                }
            ]
        }
        
        refs = parser.parse_nested_references(data)
        
        assert len(refs) == 2
        assert refs[0]["type"] == "diagram"
        assert refs[0]["version"] == "2.0.0"
        assert refs[0]["resolved"] is True
        assert refs[1]["id"] == "DOC-003"

    def test_parse_nested_references_empty(self, parser):
        """Test parsing when no references exist"""
        refs = parser.parse_nested_references({})
        assert refs == []

    def test_parse_with_validation_success(self, parser, sample_document, tmp_path):
        """Test parse with validation - success case"""
        # Create temporary file
        file_path = tmp_path / "valid_doc.json"
        file_path.write_text(json.dumps(sample_document))
        
        data, is_valid, error = parser.parse_with_validation(file_path)
        
        assert is_valid is True
        assert error is None
        assert data["title"] == "Test Document"

    def test_parse_with_validation_invalid_json(self, parser, tmp_path):
        """Test parse with validation - invalid JSON"""
        file_path = tmp_path / "invalid.json"
        file_path.write_text("{ invalid }")
        
        data, is_valid, error = parser.parse_with_validation(file_path)
        
        assert is_valid is False
        assert error is not None
        assert "Invalid JSON" in error
        assert data == {}

    def test_parse_with_validation_schema_error(self, parser, tmp_path):
        """Test parse with validation - schema validation error"""
        invalid_doc = {"description": "Missing required fields"}
        
        file_path = tmp_path / "invalid_schema.json"
        file_path.write_text(json.dumps(invalid_doc))
        
        data, is_valid, error = parser.parse_with_validation(file_path)
        
        assert is_valid is False
        assert error is not None
        assert "title" in error.lower() or "required" in error.lower()

    def test_format_validation_error_with_path(self, parser):
        """Test formatting validation error with path"""
        # Create a mock validation error
        from jsonschema import ValidationError
        
        error = ValidationError(
            message="'version' does not match pattern",
            path=["metadata", "version"]
        )
        
        formatted = parser._format_validation_error(error)
        assert "metadata.version" in formatted
        assert "does not match pattern" in formatted

    def test_format_validation_error_root_level(self, parser):
        """Test formatting validation error at root level"""
        from jsonschema import ValidationError
        
        error = ValidationError(
            message="'title' is a required property",
            path=[]
        )
        
        formatted = parser._format_validation_error(error)
        assert "root" in formatted
        assert "'title' is a required property" in formatted

    def test_idfw_schema_version_constant(self, parser):
        """Test IDFW schema version is correct"""
        assert parser.IDFW_SCHEMA_VERSION == "http://json-schema.org/draft/2020-12/schema"

    def test_document_types_complete(self, parser):
        """Test all document types are defined"""
        expected_types = {
            "documentation", "diagram", "variable", 
            "project", "generator", "config"
        }
        assert set(parser.DOCUMENT_TYPES.keys()) == expected_types

    @pytest.mark.parametrize("doc_type,prefix", [
        ("documentation", "IDDA"),
        ("diagram", "IDDG"),
        ("variable", "IDFV"),
        ("project", "IDPJ"),
        ("generator", "IDPG"),
        ("config", "IDPC")
    ])
    def test_document_type_prefixes(self, parser, doc_type, prefix):
        """Test document type prefixes are correct"""
        assert parser.DOCUMENT_TYPES[doc_type] == prefix

    def test_integration_with_schema_registry(self):
        """Test integration with schema registry"""
        registry = SchemaRegistry()
        parser = IDFWDocumentParser(registry)
        
        # Check that schemas are registered
        schemas = registry.list_schemas(namespace=SchemaNamespace.IDFW)
        assert len(schemas) > 0
        
        base_schema = registry.get_schema("idfw", "idfw_document_base")
        assert base_schema is not None

    def test_parse_all_document_types(self, parser, tmp_path):
        """Test parsing all different IDFW document types"""
        test_docs = {
            "documentation": {
                "docId": "IDDA-001",
                "title": "Documentation",
                "version": "1.0.0"
            },
            "diagram": {
                "diagId": "IDDG-001",
                "title": "Diagram",
                "version": "1.0.0",
                "diagramType": "flow"
            },
            "project": {
                "docId": "IDPJ-001",
                "title": "Project",
                "version": "1.0.0",
                "projectName": "Test"
            }
        }
        
        for doc_type, doc_data in test_docs.items():
            file_path = tmp_path / f"{doc_type}.json"
            file_path.write_text(json.dumps(doc_data))
            
            data, is_valid, error = parser.parse_with_validation(file_path)
            detected_type = parser.detect_document_type(data)
            
            assert is_valid is True
            assert detected_type == doc_type