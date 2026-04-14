"""
Unit tests for IDFW-FORCE Converters
Linear Issues: PEG-884 (SB-003), PEG-885 (SB-004)
"""

import pytest
from unified_framework.core.converters import (
    IDFWToFORCEConverter,
    FORCEToIDFWConverter,
    BidirectionalConverter
)
from unified_framework.core.force_parser import (
    FORCETool,
    FORCECategory,
    FORCEParameter,
)


@pytest.fixture
def sample_idfw_doc():
    return {
        "docId": "IDDA-001",
        "title": "API Documentation",
        "version": "2.0.0",
        "revision": "_b2",
        "description": "REST API documentation",
        "variables": {"api_version": "v2", "timeout": 30},
        "tasks": [{"taskId": "auth-task", "description": "Auth"}],
        "references": ["IDDA-002"],
        "metadata": {"author": "John Doe", "created_at": "2025-09-29T10:00:00Z"},
    }


@pytest.fixture
def sample_force_tool():
    return FORCETool(
        tool_id="force-001",
        name="Code Analysis",
        category=FORCECategory.TOOL,
        version="1.0.0",
        description="Analyze code",
        command="$code_analysis",
        parameters=[
            FORCEParameter(name="target", type="string", required=True,
                         default=None, description="Target path"),
        ],
        metadata={"author": "system", "source": "force"},
    )


class TestIDFWToFORCEConverter:

    def test_convert_document_returns_force_tool(self, sample_idfw_doc):
        converter = IDFWToFORCEConverter()
        result = converter.convert_document(sample_idfw_doc)
        assert isinstance(result, FORCETool)
        assert result.tool_id == "IDDA-001"
        assert result.name == "API Documentation"

    def test_convert_variables_to_parameters(self, sample_idfw_doc):
        converter = IDFWToFORCEConverter()
        result = converter.convert_document(sample_idfw_doc)
        param_names = [p.name for p in result.parameters]
        assert "api_version" in param_names
        assert "timeout" in param_names

    def test_convert_tasks_to_dependencies(self, sample_idfw_doc):
        converter = IDFWToFORCEConverter()
        result = converter.convert_document(sample_idfw_doc)
        assert len(result.dependencies) >= 1

    def test_convert_references_to_variants(self, sample_idfw_doc):
        converter = IDFWToFORCEConverter()
        result = converter.convert_document(sample_idfw_doc)
        assert "IDDA-002" in result.variants

    def test_convert_metadata(self, sample_idfw_doc):
        converter = IDFWToFORCEConverter()
        result = converter.convert_document(sample_idfw_doc)
        assert result.metadata["source"] == "idfw"
        assert result.metadata["original_doc_id"] == "IDDA-001"

    def test_convert_minimal_doc(self):
        converter = IDFWToFORCEConverter()
        doc = {"docId": "MIN-001", "title": "Minimal", "version": "1.0"}
        result = converter.convert_document(doc)
        assert result.tool_id == "MIN-001"
        assert result.parameters == []

    def test_conversion_stats(self, sample_idfw_doc):
        converter = IDFWToFORCEConverter()
        converter.convert_document(sample_idfw_doc)
        stats = converter.get_conversion_stats()
        assert isinstance(stats, dict)
        assert stats.get("total_conversions", stats.get("documents_converted", stats.get("tools_converted", 0))) >= 1


class TestFORCEToIDFWConverter:

    def test_convert_tool_returns_dict(self, sample_force_tool):
        converter = FORCEToIDFWConverter()
        result = converter.convert_tool(sample_force_tool)
        assert isinstance(result, dict)
        assert "docId" in result or "title" in result

    def test_convert_parameters_to_variables(self, sample_force_tool):
        converter = FORCEToIDFWConverter()
        result = converter.convert_tool(sample_force_tool)
        assert "variables" in result

    def test_convert_metadata(self, sample_force_tool):
        converter = FORCEToIDFWConverter()
        result = converter.convert_tool(sample_force_tool)
        assert "metadata" in result

    def test_convert_generates_doc_id(self, sample_force_tool):
        converter = FORCEToIDFWConverter()
        result = converter.convert_tool(sample_force_tool)
        assert result.get("docId") is not None

    def test_convert_tool_dict_input(self):
        converter = FORCEToIDFWConverter()
        tool_dict = {
            "tool_id": "test-tool",
            "name": "Test",
            "category": "tool",
        }
        result = converter.convert_tool(tool_dict)
        assert isinstance(result, dict)

    def test_conversion_stats(self, sample_force_tool):
        converter = FORCEToIDFWConverter()
        converter.convert_tool(sample_force_tool)
        stats = converter.get_conversion_stats()
        assert isinstance(stats, dict)
        assert stats.get("total_conversions", stats.get("documents_converted", stats.get("tools_converted", 0))) >= 1


class TestBidirectionalConverter:

    def test_convert_idfw_to_force(self, sample_idfw_doc):
        converter = BidirectionalConverter()
        result = converter.convert(sample_idfw_doc, source_format="idfw", target_format="force")
        assert result is not None

    def test_convert_force_to_idfw(self, sample_force_tool):
        converter = BidirectionalConverter()
        result = converter.convert(sample_force_tool, source_format="force", target_format="idfw")
        assert isinstance(result, dict)

    def test_convert_invalid_format(self, sample_idfw_doc):
        converter = BidirectionalConverter()
        with pytest.raises(Exception):
            converter.convert(sample_idfw_doc, source_format="idfw", target_format="xml")

    def test_round_trip(self, sample_idfw_doc):
        converter = BidirectionalConverter()
        result = converter.validate_round_trip(sample_idfw_doc, source_format="idfw")
        assert result is not None

    def test_batch_convert(self, sample_idfw_doc):
        converter = BidirectionalConverter()
        docs = [sample_idfw_doc, {"docId": "D2", "title": "Doc 2", "version": "1.0"}]
        results = converter.convert_batch(docs, source_format="idfw", target_format="force")
        assert len(results) == 2

    def test_conversion_report(self, sample_idfw_doc):
        converter = BidirectionalConverter()
        converter.convert(sample_idfw_doc, source_format="idfw", target_format="force")
        report = converter.get_conversion_report()
        assert isinstance(report, str)
        assert len(report) > 0
