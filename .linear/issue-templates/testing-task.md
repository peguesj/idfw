# Testing Task Template

**Template ID**: `testing-task`
**Category**: Quality Assurance - Testing
**Default Assignee**: QualityAssuranceAgent (QAA)
**Default Project**: IDFWU - IDEA Framework Unified (`4d649a6501f7`)
**Default Priority**: High

---

## Title Format
```
[Test] {Task Description}
```

**Examples**:
- `[Test] Create Schema Bridge Unit Tests`
- `[Test] Add Integration Tests for Command System`
- `[Test] Fix Flaky E2E Test in Agent Workflow`

---

## Description Template

### Overview
<!-- Brief description of what needs to be tested -->

**Test Type**: [ ] Unit | [ ] Integration | [ ] E2E | [ ] Performance | [ ] Other: _______

**Module Under Test**: [Module Name]

**Complexity**: [ ] Simple | [ ] Medium | [ ] Complex

**Estimated Hours**: ___ h

---

### Testing Requirements

#### Test Scope

**Components to Test**:
- [ ] Core module: _______
- [ ] Command handler: _______
- [ ] Agent: _______
- [ ] MCP server: _______
- [ ] Integration: _______

**Test Categories**:
- [ ] Happy path scenarios
- [ ] Error handling
- [ ] Edge cases
- [ ] Performance benchmarks
- [ ] Security tests

---

### Implementation Details

#### Files to Create/Modify
```
unified_framework/tests/
├── unit/
│   └── [module]/
│       └── test_[component].py
├── integration/
│   └── test_[workflow].py
├── e2e/
│   └── test_[user_story].py
└── performance/
    └── test_[benchmark].py
```

#### Test Count Target
- **Unit Tests**: ___ tests
- **Integration Tests**: ___ tests
- **E2E Tests**: ___ tests
- **Total**: ___ tests

#### Coverage Target
- **Current Coverage**: ___ %
- **Target Coverage**: ___ %
- **Minimum Required**: 80%

---

### Test Cases

#### Test Case 1: [Test Name]
**Type**: Unit | Integration | E2E
**Priority**: High | Medium | Low

**Description**:
<!-- What is being tested -->

**Pre-conditions**:
1.
2.

**Test Steps**:
1.
2.
3.

**Expected Result**:
<!-- What should happen -->

**Assertions**:
```python
assert result.status == "success"
assert result.data is not None
assert len(result.items) == expected_count
```

---

#### Test Case 2: [Test Name]
**Type**: Unit | Integration | E2E
**Priority**: High | Medium | Low

**Description**:
<!-- What is being tested -->

**Pre-conditions**:
1.
2.

**Test Steps**:
1.
2.
3.

**Expected Result**:
<!-- What should happen -->

**Assertions**:
```python
with pytest.raises(ValidationError):
    component.validate(invalid_input)
```

---

#### Test Case 3: [Test Name]
**Type**: Unit | Integration | E2E
**Priority**: High | Medium | Low

**Description**:
<!-- What is being tested -->

**Pre-conditions**:
1.
2.

**Test Steps**:
1.
2.
3.

**Expected Result**:
<!-- What should happen -->

**Assertions**:
```python
assert benchmark.stats.mean < 0.1  # 100ms target
```

---

### Test Implementation

#### Unit Tests
```python
import pytest
from unified_framework.[module] import [Component]


class Test[Component]:
    """Unit tests for [Component]"""

    @pytest.fixture
    def component(self):
        """Create component instance for testing"""
        return [Component]()

    def test_[scenario]_success(self, component):
        """Test successful [operation]"""
        # Arrange
        input_data = {...}

        # Act
        result = component.method(input_data)

        # Assert
        assert result.status == "success"
        assert result.data is not None

    def test_[scenario]_failure(self, component):
        """Test [operation] with invalid input"""
        # Arrange
        invalid_data = {...}

        # Act & Assert
        with pytest.raises(ValidationError):
            component.method(invalid_data)

    @pytest.mark.parametrize("input,expected", [
        (input1, expected1),
        (input2, expected2),
        (input3, expected3),
    ])
    def test_[scenario]_variations(self, component, input, expected):
        """Test [operation] with various inputs"""
        result = component.method(input)
        assert result == expected
```

#### Integration Tests
```python
import pytest
from unified_framework.[module1] import [Component1]
from unified_framework.[module2] import [Component2]


@pytest.mark.integration
class Test[Workflow]:
    """Integration tests for [workflow]"""

    @pytest.fixture
    async def setup_environment(self):
        """Set up test environment"""
        # Start services (Redis, etc.)
        yield
        # Cleanup

    @pytest.mark.asyncio
    async def test_[workflow]_end_to_end(self, setup_environment):
        """Test complete [workflow] workflow"""
        # Create components
        component1 = [Component1]()
        component2 = [Component2]()

        # Execute workflow
        result1 = await component1.process(input_data)
        result2 = await component2.process(result1.output)

        # Verify results
        assert result2.status == "success"
        assert result2.data.meets_requirements()
```

#### Performance Tests
```python
import pytest
from unified_framework.[module] import [Component]


@pytest.mark.performance
class Test[Component]Performance:
    """Performance tests for [Component]"""

    def test_[operation]_performance(self, benchmark):
        """
        Benchmark [operation] performance

        Target: < 100ms
        """
        component = [Component]()
        input_data = create_test_data()

        result = benchmark(component.method, input_data)

        assert benchmark.stats.mean < 0.1  # 100ms
        assert benchmark.stats.stddev < 0.01  # Low variance

    def test_[operation]_under_load(self):
        """Test [operation] under concurrent load"""
        component = [Component]()

        # Simulate 100 concurrent operations
        results = asyncio.gather(*[
            component.method(data)
            for data in test_data_batch
        ])

        # Verify all succeeded
        assert all(r.status == "success" for r in results)
```

---

### Test Fixtures

#### Required Fixtures
```python
@pytest.fixture
def sample_[data_type]():
    """Sample [data] for testing"""
    return {
        "field1": "value1",
        "field2": "value2",
    }

@pytest.fixture
def mock_[dependency]():
    """Mock [external dependency]"""
    mock = Mock(spec=[DependencyClass])
    mock.method.return_value = expected_result
    return mock

@pytest.fixture
async def [resource]_connection():
    """Set up [resource] connection"""
    connection = await connect_to_resource()
    yield connection
    await connection.close()
```

---

### Mocking Strategy

#### External Dependencies to Mock
- [ ] Redis (use fakeredis)
- [ ] Linear API (use unittest.mock)
- [ ] File system (use pytest tmp_path)
- [ ] HTTP requests (use responses/httpx.mock)
- [ ] Time functions (use freezegun)
- [ ] Database (use in-memory DB)

#### Mock Examples
```python
from unittest.mock import Mock, patch
import fakeredis
import responses


@pytest.fixture
def mock_redis():
    """Mock Redis connection"""
    return fakeredis.FakeStrictRedis()


@pytest.fixture
def mock_linear_client():
    """Mock Linear API client"""
    mock = Mock()
    mock.create_issue.return_value = {"id": "PEG-123"}
    return mock


@responses.activate
def test_external_api_call():
    """Test external API with mocked responses"""
    responses.add(
        responses.POST,
        "https://api.example.com/endpoint",
        json={"status": "success"},
        status=200
    )

    result = make_api_call()
    assert result.status == "success"
```

---

### Acceptance Criteria

**Definition of Done**:
- [ ] All test cases implemented
- [ ] Test coverage target met (> 80%)
- [ ] All tests passing
- [ ] No flaky tests
- [ ] Performance benchmarks met
- [ ] Test documentation updated
- [ ] CI/CD integration verified
- [ ] Code reviewed
- [ ] PR created and linked

**Success Metrics**:
- Test pass rate: 100%
- Code coverage: > 80% (target)
- Test execution time: < [target]s
- Zero flaky tests
- Zero skipped tests

---

### Dependencies

**Blocked By**:
- PEG-XXX: [Related Issue - Implementation Task]

**Blocks**:
- PEG-XXX: [Related Issue - Deployment Task]

**Related Issues**:
- PEG-XXX: [Related Issue Title]

---

### Test Data

#### Test Data Requirements
- [ ] Sample schemas (IDFW, FORCE)
- [ ] Sample commands
- [ ] Sample agent messages
- [ ] Mock Linear responses
- [ ] Performance test data

#### Test Data Location
```
unified_framework/tests/fixtures/
├── schemas/
│   ├── idfw/
│   │   ├── simple_document.idfw
│   │   └── complex_document.idfw
│   └── force/
│       └── sample_tool.force
├── commands/
│   └── sample_commands.txt
└── data/
    └── test_data.json
```

---

### Performance Targets

**Performance Benchmarks**:
- [ ] Schema parsing: < 50ms
- [ ] Schema conversion: < 100ms
- [ ] Command parsing: < 10ms
- [ ] Command execution overhead: < 50ms
- [ ] Agent task execution: < 5s
- [ ] Message bus throughput: > 1000 msgs/sec
- [ ] MCP tool invocation: < 100ms

**Load Testing Targets**:
- Concurrent users: 100+
- Requests per second: 1000+
- Error rate: < 1%
- Response time (95th percentile): < 500ms

---

### GitHub References

**Branch**: `jeremiah/peg-XXX-test-[description]`
**PR**: #XXX (link when created)
**Commits**: (link to commits)

---

### Testing Instructions

#### Run Tests Locally
```bash
# Run all tests
pytest unified_framework/tests/ -v

# Run specific test file
pytest unified_framework/tests/unit/[module]/test_[component].py -v

# Run with coverage
pytest unified_framework/tests/ --cov --cov-report=html

# Run only failed tests
pytest --lf

# Run tests matching pattern
pytest -k "test_schema" -v

# Run with specific markers
pytest -m integration -v
pytest -m "not slow" -v
```

#### Run Performance Tests
```bash
# Run benchmarks
pytest unified_framework/tests/performance/ --benchmark-only

# Compare with baseline
pytest unified_framework/tests/performance/ --benchmark-compare

# Save benchmark results
pytest unified_framework/tests/performance/ --benchmark-save=baseline
```

#### CI/CD Integration
```bash
# GitHub Actions will run:
- Unit tests on every commit
- Integration tests on every PR
- E2E tests on merge to main
- Performance tests daily
```

---

### Coverage Report

#### Current Coverage
```
Module                                Coverage
-----------------------------------------------
unified_framework/core/               XX%
unified_framework/commands/           XX%
unified_framework/agents/             XX%
unified_framework/mcp/                XX%
-----------------------------------------------
Total                                 XX%
```

#### Coverage Goals
- **Overall**: 80% minimum
- **Critical paths**: 95% minimum
- **New code**: 90% minimum

---

### Flaky Test Handling

**If tests are flaky**:
1. Identify root cause (timing, race conditions, external dependencies)
2. Add retries for known flaky tests (use pytest-rerunfailures)
3. Improve test isolation
4. Use proper async/await patterns
5. Add timeouts and sleeps where needed
6. Mock external dependencies better

**Flaky Test Marker**:
```python
@pytest.mark.flaky(reruns=3, reruns_delay=1)
def test_potentially_flaky():
    """Test that may fail intermittently"""
    pass
```

---

### Documentation Updates

**Files to Update**:
- [ ] Testing plan documentation
- [ ] Test coverage report
- [ ] CI/CD documentation
- [ ] Developer guide

---

### Quality Gates

**Before Merge**:
- [ ] All tests passing
- [ ] Coverage target met
- [ ] No flaky tests
- [ ] Performance benchmarks met
- [ ] Code review completed
- [ ] CI/CD green

---

### Labels
`testing`, `qa`, `unit|integration|e2e|performance`, `priority:high`

---

**Template Version**: 1.0.0
**Linear Project**: 4d649a6501f7
**Created**: 2025-09-29