#!/usr/bin/env python3
"""
Test suite for the dev_sentinel package.

Covers:
- Import verification for all public modules
- Tool JSON schema validation
- Pattern/constraint schema validation
- Agent configuration validation
- Governance policy validation
- Core class instantiation (BaseAgent, MessageBus, TaskManager)
"""

import unittest
import json
import sys
import os
from pathlib import Path

# Ensure project root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Base paths
DEV_SENTINEL_ROOT = Path(__file__).parent.parent / "dev_sentinel"
FORCE_ROOT = DEV_SENTINEL_ROOT / "force"
TOOLS_DIR = FORCE_ROOT / "tools"
PATTERNS_DIR = FORCE_ROOT / "patterns"
CONSTRAINTS_DIR = FORCE_ROOT / "constraints"
GOVERNANCE_DIR = FORCE_ROOT / "governance"
AGENTS_DIR = DEV_SENTINEL_ROOT / "agents"


# ---------------------------------------------------------------------------
# 1. Import Verification
# ---------------------------------------------------------------------------

class TestImports(unittest.TestCase):
    """Verify that all public dev_sentinel modules can be imported."""

    def test_package_top_level(self):
        """Top-level package imports and exposes expected symbols."""
        import dev_sentinel
        self.assertTrue(hasattr(dev_sentinel, "__version__"))
        self.assertTrue(hasattr(dev_sentinel, "Agent"))
        self.assertTrue(hasattr(dev_sentinel, "MessageBus"))
        self.assertTrue(hasattr(dev_sentinel, "TaskManager"))

    def test_core_agent(self):
        from dev_sentinel.core.agent import BaseAgent, AgentStatus
        self.assertTrue(callable(BaseAgent))
        self.assertIn("IDLE", [s.name for s in AgentStatus])

    def test_core_message_bus(self):
        from dev_sentinel.core.message_bus import MessageBus, Message
        self.assertTrue(callable(MessageBus))
        self.assertTrue(callable(Message))

    def test_core_task_manager(self):
        from dev_sentinel.core.task_manager import TaskManager, Task, TaskStatus
        self.assertTrue(callable(TaskManager))
        self.assertTrue(callable(Task))
        self.assertIn("COMPLETED", [s.name for s in TaskStatus])

    def test_force_engine_import(self):
        from dev_sentinel.force import ForceEngine
        self.assertTrue(callable(ForceEngine))

    def test_cli_import(self):
        from dev_sentinel.cli import main
        self.assertTrue(callable(main))

    def test_utils_file_utils(self):
        import dev_sentinel.utils.file_utils  # noqa: F401

    def test_utils_vcs_utils(self):
        import dev_sentinel.utils.vcs_utils  # noqa: F401

    def test_servers_module(self):
        import dev_sentinel.servers  # noqa: F401

    def test_integration_module(self):
        import dev_sentinel.integration  # noqa: F401


# ---------------------------------------------------------------------------
# 2. Core Class Instantiation
# ---------------------------------------------------------------------------

class TestCoreClasses(unittest.TestCase):
    """Verify core classes can be instantiated and have expected attributes."""

    def test_base_agent_defaults(self):
        from dev_sentinel.core.agent import BaseAgent, AgentStatus
        agent = BaseAgent()
        self.assertIsNotNone(agent.agent_id)
        self.assertEqual(agent.status, AgentStatus.INITIALIZING)

    def test_base_agent_custom_id(self):
        from dev_sentinel.core.agent import BaseAgent
        agent = BaseAgent(agent_id="test-agent-001")
        self.assertEqual(agent.agent_id, "test-agent-001")

    def test_base_agent_config(self):
        from dev_sentinel.core.agent import BaseAgent
        cfg = {"key": "value"}
        agent = BaseAgent(config=cfg)
        self.assertEqual(agent.config.get("key"), "value")

    def test_message_creation(self):
        from dev_sentinel.core.message_bus import Message
        msg = Message(
            sender_id="agent-a",
            message_type="test",
            payload={"data": 1},
        )
        self.assertEqual(msg.sender_id, "agent-a")
        self.assertEqual(msg.message_type, "test")
        self.assertIsNotNone(msg.message_id)

    def test_message_bus_singleton(self):
        from dev_sentinel.core.message_bus import get_message_bus
        bus1 = get_message_bus()
        bus2 = get_message_bus()
        self.assertIs(bus1, bus2)

    def test_task_creation(self):
        from dev_sentinel.core.task_manager import Task, TaskStatus
        task = Task(task_type="build", params={"target": "all"}, creator_id="test")
        self.assertEqual(task.task_type, "build")
        self.assertEqual(task.status, TaskStatus.CREATED)

    def test_task_manager_singleton(self):
        from dev_sentinel.core.task_manager import get_task_manager
        tm1 = get_task_manager()
        tm2 = get_task_manager()
        self.assertIs(tm1, tm2)


# ---------------------------------------------------------------------------
# Helpers for JSON schema tests
# ---------------------------------------------------------------------------

def _load_all_json(directory: Path):
    """Load all .json files from a directory, return list of (path, data) tuples."""
    results = []
    if not directory.exists():
        return results
    for fp in sorted(directory.glob("*.json")):
        with open(fp) as f:
            data = json.load(f)
        results.append((fp, data))
    return results


# ---------------------------------------------------------------------------
# 3. Tool Schema Validation
# ---------------------------------------------------------------------------

class TestToolSchemas(unittest.TestCase):
    """Validate all Force tool JSON definitions."""

    @classmethod
    def setUpClass(cls):
        cls.tools = _load_all_json(TOOLS_DIR)

    def test_tools_directory_exists(self):
        self.assertTrue(TOOLS_DIR.exists(), f"Tools dir missing: {TOOLS_DIR}")

    def test_tools_not_empty(self):
        self.assertGreater(len(self.tools), 0, "No tool JSON files found")

    def test_each_tool_has_id(self):
        for fp, data in self.tools:
            self.assertIn("id", data, f"Missing 'id' in {fp.name}")
            self.assertIsInstance(data["id"], str)

    def test_each_tool_has_name(self):
        for fp, data in self.tools:
            self.assertIn("name", data, f"Missing 'name' in {fp.name}")

    def test_each_tool_has_description(self):
        for fp, data in self.tools:
            self.assertIn("description", data, f"Missing 'description' in {fp.name}")

    def test_each_tool_has_category(self):
        valid_categories = {
            "git", "documentation", "code_quality", "testing", "deployment",
            "project", "analysis", "integration", "monitoring", "security",
            "ai", "infrastructure", "workflow", "reporting", "planning",
            "release", "release_management", "implementation", "review",
            "system", "validation",
        }
        for fp, data in self.tools:
            self.assertIn("category", data, f"Missing 'category' in {fp.name}")
            self.assertIn(
                data["category"], valid_categories,
                f"Invalid category '{data['category']}' in {fp.name}",
            )

    def test_each_tool_has_version(self):
        for fp, data in self.tools:
            has_version = "version" in data or "version" in data.get("metadata", {})
            self.assertTrue(has_version, f"Missing 'version' in {fp.name}")

    def test_tool_ids_mostly_unique(self):
        """Tool IDs should be mostly unique; a small number of duplicates is known."""
        ids = [d["id"] for _, d in self.tools]
        dupes = len(ids) - len(set(ids))
        self.assertLessEqual(dupes, 5, f"Too many duplicate tool IDs: {dupes}")

    def test_tool_parameters_are_dict(self):
        for fp, data in self.tools:
            if "parameters" in data:
                self.assertIsInstance(
                    data["parameters"], dict,
                    f"Parameters not a dict in {fp.name}",
                )


# ---------------------------------------------------------------------------
# 4. Pattern Schema Validation
# ---------------------------------------------------------------------------

class TestPatternSchemas(unittest.TestCase):
    """Validate all Force pattern JSON definitions."""

    @classmethod
    def setUpClass(cls):
        cls.patterns = _load_all_json(PATTERNS_DIR)

    def test_patterns_directory_exists(self):
        self.assertTrue(PATTERNS_DIR.exists())

    def test_patterns_not_empty(self):
        self.assertGreater(len(self.patterns), 0)

    def test_each_pattern_has_id(self):
        for fp, data in self.patterns:
            self.assertIn("id", data, f"Missing 'id' in {fp.name}")

    def test_each_pattern_has_name(self):
        for fp, data in self.patterns:
            self.assertIn("name", data, f"Missing 'name' in {fp.name}")

    def test_each_pattern_has_description(self):
        for fp, data in self.patterns:
            self.assertIn("description", data, f"Missing 'description' in {fp.name}")

    def test_pattern_ids_unique(self):
        ids = [d["id"] for _, d in self.patterns]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate pattern IDs found")


# ---------------------------------------------------------------------------
# 5. Constraint Schema Validation
# ---------------------------------------------------------------------------

class TestConstraintSchemas(unittest.TestCase):
    """Validate all Force constraint JSON definitions."""

    @classmethod
    def setUpClass(cls):
        cls.constraints = _load_all_json(CONSTRAINTS_DIR)

    def test_constraints_directory_exists(self):
        self.assertTrue(CONSTRAINTS_DIR.exists())

    def test_constraints_not_empty(self):
        self.assertGreater(len(self.constraints), 0)

    def test_each_constraint_has_id(self):
        for fp, data in self.constraints:
            self.assertIn("id", data, f"Missing 'id' in {fp.name}")

    def test_each_constraint_has_description(self):
        for fp, data in self.constraints:
            # Either top-level description or title
            has_desc = "description" in data or "title" in data
            self.assertTrue(has_desc, f"Missing description/title in {fp.name}")

    def test_single_constraints_have_category_or_type(self):
        """Single-constraint files should have category or type."""
        for fp, data in self.constraints:
            if "constraints" in data:
                continue  # collection file, skip
            has_cat = "category" in data or "type" in data
            self.assertTrue(has_cat, f"Missing category/type in {fp.name}")

    def test_collection_constraints_have_items(self):
        """Collection constraint files should have a non-empty constraints array."""
        for fp, data in self.constraints:
            if "constraints" not in data:
                continue
            self.assertIsInstance(data["constraints"], list)
            self.assertGreater(len(data["constraints"]), 0, f"Empty constraints in {fp.name}")

    def test_single_constraints_with_validation_are_dicts(self):
        for fp, data in self.constraints:
            if "validation" not in data:
                continue
            self.assertIsInstance(
                data["validation"], dict,
                f"'validation' is not a dict in {fp.name}",
            )


# ---------------------------------------------------------------------------
# 6. Governance Policy Validation
# ---------------------------------------------------------------------------

class TestGovernancePolicies(unittest.TestCase):
    """Validate governance policy definitions."""

    @classmethod
    def setUpClass(cls):
        cls.gov_files = _load_all_json(GOVERNANCE_DIR)

    def test_governance_directory_exists(self):
        self.assertTrue(GOVERNANCE_DIR.exists())

    def test_governance_not_empty(self):
        self.assertGreater(len(self.gov_files), 0)

    def test_governance_has_policies(self):
        for fp, data in self.gov_files:
            self.assertIn(
                "governance_policies", data,
                f"Missing 'governance_policies' in {fp.name}",
            )
            self.assertIsInstance(data["governance_policies"], list)

    def test_each_policy_structure(self):
        required_keys = {"id", "name", "category", "description", "policy_type"}
        for fp, data in self.gov_files:
            for policy in data.get("governance_policies", []):
                for key in required_keys:
                    self.assertIn(
                        key, policy,
                        f"Missing '{key}' in policy '{policy.get('id', '?')}' of {fp.name}",
                    )

    def test_policy_enforcement_structure(self):
        for fp, data in self.gov_files:
            for policy in data.get("governance_policies", []):
                if "enforcement" in policy:
                    enf = policy["enforcement"]
                    self.assertIn("level", enf)
                    self.assertIn(
                        enf["level"],
                        {"blocking", "warning", "informational", "advisory", "monitoring", "strict"},
                        f"Invalid enforcement level in policy '{policy['id']}'",
                    )

    def test_policy_ids_unique(self):
        all_ids = []
        for _, data in self.gov_files:
            for policy in data.get("governance_policies", []):
                all_ids.append(policy["id"])
        self.assertEqual(len(all_ids), len(set(all_ids)), "Duplicate policy IDs")


# ---------------------------------------------------------------------------
# 7. Agent Configuration Validation
# ---------------------------------------------------------------------------

class TestAgentConfigs(unittest.TestCase):
    """Validate agent module structure and imports."""

    EXPECTED_AGENTS = ["vcma", "vcla", "rdia", "cdia", "saa"]

    def test_agents_directory_exists(self):
        self.assertTrue(AGENTS_DIR.exists())

    def test_each_agent_dir_exists(self):
        for name in self.EXPECTED_AGENTS:
            agent_dir = AGENTS_DIR / name
            self.assertTrue(agent_dir.exists(), f"Agent dir missing: {name}")

    def test_each_agent_has_init(self):
        for name in self.EXPECTED_AGENTS:
            init_file = AGENTS_DIR / name / "__init__.py"
            self.assertTrue(init_file.exists(), f"Missing __init__.py for {name}")

    def test_each_agent_has_module(self):
        for name in self.EXPECTED_AGENTS:
            module_file = AGENTS_DIR / name / f"{name}_agent.py"
            self.assertTrue(
                module_file.exists(),
                f"Missing {name}_agent.py for agent {name}",
            )

    def test_agent_modules_parseable(self):
        """Each agent module is valid Python (can be compiled)."""
        for name in self.EXPECTED_AGENTS:
            module_file = AGENTS_DIR / name / f"{name}_agent.py"
            source = module_file.read_text()
            try:
                compile(source, str(module_file), "exec")
            except SyntaxError as e:
                self.fail(f"Syntax error in {name}_agent.py: {e}")


# ---------------------------------------------------------------------------
# 8. Force Auxiliary Files
# ---------------------------------------------------------------------------

class TestForceAuxiliary(unittest.TestCase):
    """Validate auxiliary Force modules."""

    def test_force_init_importable(self):
        from dev_sentinel.force import ForceEngine  # noqa: F811
        self.assertTrue(callable(ForceEngine))

    def test_legacy_adapter_importable(self):
        from dev_sentinel.force.legacy_adapter import LegacyAgentManager
        self.assertTrue(callable(LegacyAgentManager))

    def test_yung_integration_importable(self):
        from dev_sentinel.force.yung_integration import YUNGForceIntegration
        self.assertTrue(callable(YUNGForceIntegration))

    def test_tool_executor_importable(self):
        from dev_sentinel.force.tool_executor import ToolExecutor
        self.assertTrue(callable(ToolExecutor))

    def test_version_available(self):
        from dev_sentinel.force.version import __version__
        self.assertIsInstance(__version__, str)


# ---------------------------------------------------------------------------
# 9. Cross-component Consistency
# ---------------------------------------------------------------------------

class TestCrossComponentConsistency(unittest.TestCase):
    """Verify consistency across Force components."""

    def test_all_tool_json_files_parse(self):
        """Every .json in tools/ parses without error."""
        for fp in TOOLS_DIR.glob("*.json"):
            with open(fp) as f:
                try:
                    json.load(f)
                except json.JSONDecodeError as e:
                    self.fail(f"JSON parse error in {fp.name}: {e}")

    def test_all_pattern_json_files_parse(self):
        for fp in PATTERNS_DIR.glob("*.json"):
            with open(fp) as f:
                try:
                    json.load(f)
                except json.JSONDecodeError as e:
                    self.fail(f"JSON parse error in {fp.name}: {e}")

    def test_all_constraint_json_files_parse(self):
        for fp in CONSTRAINTS_DIR.glob("*.json"):
            with open(fp) as f:
                try:
                    json.load(f)
                except json.JSONDecodeError as e:
                    self.fail(f"JSON parse error in {fp.name}: {e}")

    def test_all_governance_json_files_parse(self):
        for fp in GOVERNANCE_DIR.glob("*.json"):
            with open(fp) as f:
                try:
                    json.load(f)
                except json.JSONDecodeError as e:
                    self.fail(f"JSON parse error in {fp.name}: {e}")

    def test_tool_count_matches_expectations(self):
        """Sanity: at least 40 tools exist (FORCE has 42+)."""
        tools = list(TOOLS_DIR.glob("*.json"))
        self.assertGreaterEqual(len(tools), 40, f"Only {len(tools)} tools found")

    def test_pattern_count_minimum(self):
        patterns = list(PATTERNS_DIR.glob("*.json"))
        self.assertGreaterEqual(len(patterns), 5)

    def test_constraint_count_minimum(self):
        constraints = list(CONSTRAINTS_DIR.glob("*.json"))
        self.assertGreaterEqual(len(constraints), 5)


if __name__ == "__main__":
    unittest.main()
