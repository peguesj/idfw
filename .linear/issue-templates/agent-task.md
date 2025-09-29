# Agent Task Template

**Template ID**: `agent-task`
**Category**: Development - Agent System
**Default Assignee**: AgentDeveloperAgent (ADA)
**Default Project**: IDFWU - IDEA Framework Unified (`4d649a6501f7`)
**Default Priority**: High

---

## Title Format
```
[Agent] {Task Description}
```

**Examples**:
- `[Agent] Implement SchemaEngineerAgent`
- `[Agent] Add Message Bus Integration`
- `[Agent] Fix Agent Task Execution Timeout`

---

## Description Template

### Overview
<!-- Brief description of the agent functionality -->

**Task Type**: [ ] Agent Implementation | [ ] Message Bus | [ ] Orchestration | [ ] Monitoring | [ ] Other: _______

**Agent Department**: [ ] Product | [ ] Project | [ ] Development | [ ] Integration | [ ] Quality

**Complexity**: [ ] Simple | [ ] Medium | [ ] Complex

**Estimated Hours**: ___ h

---

### Agent Specification

#### Agent Details

**Agent ID**: `[AGENT-ID]` (e.g., SEA, BDA, QAA)
**Agent Name**: `[AgentName]Agent`
**Department**: [Department Name]
**Role**: [Agent Role]

**Responsibilities**:
-
-
-

**Capabilities**:
-
-
-

---

### Requirements

#### Functional Requirements
<!-- What the agent must be able to do -->
1.
2.
3.

#### Task Types Handled
<!-- Types of tasks this agent can execute -->
- [ ] Schema operations
- [ ] Code generation
- [ ] Testing
- [ ] Documentation
- [ ] Integration
- [ ] Other: _______

---

### Implementation Details

#### Files to Create/Modify
```
unified_framework/
├── agents/
│   ├── implementations/
│   │   └── [agent_name].py
│   ├── base_agent.py (reference)
│   └── factory.py (modify)
└── tests/
    └── unit/
        └── agents/
            └── test_[agent_name].py
```

#### Agent Class Structure
```python
class [AgentName]Agent(BaseAgent):
    """
    [Agent Description]

    Responsibilities:
    - [Responsibility 1]
    - [Responsibility 2]
    - [Responsibility 3]
    """

    agent_id: str = "[AGENT-ID]"
    department: str = "[Department]"

    async def execute_task(self, task: Task) -> TaskResult:
        """
        Execute an assigned task

        Args:
            task: Task to execute

        Returns:
            Task execution result
        """
        pass

    async def validate_task(self, task: Task) -> bool:
        """
        Validate if this agent can handle the task

        Args:
            task: Task to validate

        Returns:
            True if agent can handle task
        """
        pass

    def get_capabilities(self) -> List[str]:
        """
        Get list of agent capabilities

        Returns:
            List of capability identifiers
        """
        return [...]
```

---

### Integration Points

#### Message Bus
- **Topics Subscribed**:
  - `agent.tasks.[AGENT-ID]`
  - `[department].broadcast`
  -
- **Topics Published**:
  - `agent.status.[AGENT-ID]`
  - `agent.results.[AGENT-ID]`
  -

#### Linear API
- **Operations**:
  - [ ] Create issues
  - [ ] Update issue status
  - [ ] Add comments
  - [ ] Create sub-tasks
  - [ ] Link issues

#### Core Modules
- [ ] Schema bridge integration
- [ ] Command processor integration
- [ ] State manager integration
- [ ] MCP server integration

---

### Test Cases

#### Unit Tests Required

**Test Coverage Target**: 85%

1. **Agent Initialization**
   - Successful initialization
   - Invalid configuration
   - Connection to message bus

2. **Task Execution**
   - Valid task execution
   - Invalid task handling
   - Task timeout
   - Task cancellation

3. **Message Handling**
   - Send message
   - Receive message
   - Broadcast message
   - Request/response pattern

4. **Linear Integration**
   - Create Linear issue
   - Update issue status
   - Add comment
   - Error handling

5. **Performance Metrics**
   - Metric collection
   - Metric reporting
   - Performance tracking

#### Integration Tests Required
- [ ] Multi-agent workflow
- [ ] Message bus communication
- [ ] Task dependency resolution
- [ ] Agent health monitoring

---

### Acceptance Criteria

**Definition of Done**:
- [ ] Agent class implemented
- [ ] Agent registered in factory
- [ ] Task execution working
- [ ] Message bus integration complete
- [ ] Linear integration working
- [ ] Unit tests passing (coverage > 85%)
- [ ] Integration tests added
- [ ] Documentation updated
- [ ] Performance benchmarked
- [ ] PR created and linked

**Success Metrics**:
- Task execution success rate: > 95%
- Average task execution time: < 5s
- Message handling latency: < 100ms
- Linear API success rate: > 99%
- Health check success rate: 100%

---

### Dependencies

**Blocked By**:
- PEG-XXX: [Related Issue Title]

**Blocks**:
- PEG-XXX: [Related Issue Title]

**Related Issues**:
- PEG-XXX: [Related Issue Title]

---

### Agent Configuration

#### Configuration Schema
```yaml
agents:
  [AGENT-ID]:
    enabled: true
    department: [Department]
    max_concurrent_tasks: 5
    task_timeout: 300  # seconds
    retry_attempts: 3
    linear_integration: true
    message_bus:
      subscribe:
        - agent.tasks.[AGENT-ID]
        - [department].broadcast
      publish:
        - agent.status.[AGENT-ID]
        - agent.results.[AGENT-ID]
    capabilities:
      - [capability-1]
      - [capability-2]
```

---

### Message Formats

#### Task Assignment Message
```json
{
  "id": "msg-123",
  "sender_id": "orchestrator",
  "receiver_id": "[AGENT-ID]",
  "message_type": "TASK_ASSIGNMENT",
  "payload": {
    "task_id": "task-456",
    "description": "Task description",
    "priority": "high",
    "metadata": {}
  }
}
```

#### Task Result Message
```json
{
  "id": "msg-124",
  "sender_id": "[AGENT-ID]",
  "receiver_id": "orchestrator",
  "message_type": "TASK_RESULT",
  "payload": {
    "task_id": "task-456",
    "status": "completed",
    "result": {},
    "execution_time": 2.5,
    "linear_issue_id": "PEG-XXX"
  }
}
```

---

### Performance Considerations

**Target Performance**:
- Task execution: < 5s average
- Message handling: < 100ms
- Linear API calls: < 500ms
- Health check: < 50ms
- Memory usage: < 200MB per agent

**Optimization Notes**:
-
-

---

### GitHub References

**Branch**: `jeremiah/peg-XXX-agent-[description]`
**PR**: #XXX (link when created)
**Commits**: (link to commits)

---

### Testing Instructions

#### Manual Testing
```bash
# Start agent
python -m unified_framework.agents.deploy [AGENT-ID]

# Assign task
python -m unified_framework.agents.assign [AGENT-ID] "Task description"

# Check status
python -m unified_framework.agents.status [AGENT-ID]

# View performance metrics
python -m unified_framework.agents.metrics [AGENT-ID]
```

#### Automated Testing
```bash
# Run unit tests
pytest unified_framework/tests/unit/agents/test_[agent_name].py -v

# Run integration tests
pytest unified_framework/tests/integration/test_agent*.py -v

# Test message bus communication
pytest unified_framework/tests/integration/test_message_bus.py -v
```

---

### Monitoring and Observability

#### Health Checks
- [ ] Heartbeat every 30s
- [ ] Task queue status
- [ ] Message bus connection
- [ ] Linear API connectivity

#### Metrics to Track
- Tasks completed
- Tasks failed
- Average execution time
- Messages sent/received
- Linear issues created
- Error rate

#### Alerts
- Agent not responding (> 1 min)
- Task failure rate > 10%
- Message bus disconnection
- Linear API errors

---

### Documentation Updates

**Files to Update**:
- [ ] Agent reference documentation
- [ ] Architecture documentation
- [ ] API documentation
- [ ] Configuration guide

---

### Security Considerations

- [ ] Authentication for message bus
- [ ] Authorization for task types
- [ ] Linear API key security
- [ ] Input validation
- [ ] Rate limiting

---

### Deployment

#### Deployment Steps
1. Merge PR to main
2. Update agent registry
3. Deploy to staging
4. Run integration tests
5. Deploy to production
6. Monitor for 24 hours

#### Rollback Plan
- Stop agent
- Revert to previous version
- Verify system stability

---

### Labels
`agent`, `implementation`, `[department]`, `development`, `priority:high`

---

**Template Version**: 1.0.0
**Linear Project**: 4d649a6501f7
**Created**: 2025-09-29