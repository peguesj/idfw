# Claude Code Project Instructions - IDFW Unified Framework

## Project Information

### IDFWU - IDEA Framework Unified
**Linear Project ID**: `4d649a6501f7`
**Project URL**: https://linear.app/pegues-innovations/project/idfwu-idea-framework-unified-4d649a6501f7
**Repository**: https://github.com/[to-be-created]/idfw-unified
**Description**: Unification of IDFW (IDEA Definition Framework) and Dev Sentinel into a comprehensive development framework with autonomous agent execution.

## Fix Loop Process
- fix loop is as follows:
- designate specialized agents
- generate combined todo
- generate tasks for agents with callbacks to main todo
- run agents with concurrency

Additionally, always use a new git worktree when attempting large fixes

## Agent Execution Instructions
- **CRITICAL**: All agents are to run concurrently unless they are required to run in order when executing a todo list with agentic delegation
- **API 529 Error Handling**: Automatically adjust concurrency rate when receiving API 529 (rate limit) errors - reduce concurrent requests and implement exponential backoff with retry logic

## Important Instruction Reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

## Build and Test Requirements
- **ALWAYS build first** before marking any task as completed
- **ALWAYS run all tests** (unit, integration, E2E) before marking work as done
- **Deploy monitoring agents** to capture and record all warnings/errors during build/test/lint processes
- **Create bug issues** for all detected problems using specialized agents
- **Concurrent monitoring** - deploy agents that wait for input from other agents to track issues

## Issue Tracking & Version Control Instructions

### Linear Issue Management
When working on the IDFWU project:
1. **Always check Linear first** using the project ID to find existing issues
2. **Create new issues** for significant features or bugs using `mcp__linear-server__create_issue`
3. **Link related issues** by setting `parentId` to create hierarchical relationships
4. **Update issue status** as work progresses (Todo → In Progress → Done)
5. **Add comments** to issues with progress updates and completion details

### Git Commit Standards for Claude Code
When making commits in the IDFWU project:
1. **Include issue reference** in commit messages when applicable (e.g., "PEG-XXX: Description")
2. **Use conventional commits** format: type(scope): description
   - feat: New feature
   - fix: Bug fix
   - docs: Documentation
   - test: Testing
   - refactor: Code refactoring
   - chore: Maintenance

### GitHub Pull Request Standards
When creating PRs for IDFWU:
1. **Reference Linear issues** in PR description using issue identifiers (PEG-XXX)
2. **Include Claude Code attribution** in PR body
3. **Link to Linear project** in PR description
4. **Use PR template**:
   - Summary of changes
   - Related Linear issues
   - Testing performed
   - Deployment notes
   - Claude Code attribution

### Cross-Platform Linking Strategy
Maintain traceability between Claude Code, GitHub, and Linear:

#### Claude Code → GitHub:
- Include issue references in commits (PEG-XXX)
- Add Claude Code attribution in all commits
- Reference Linear issues in PR descriptions

#### GitHub → Linear:
- Add PR links to Linear issue comments
- Update Linear issue status when PRs are merged
- Reference commit SHAs in Linear comments for specific changes

#### Linear → GitHub:
- Use Linear's git branch naming: `jeremiah/peg-XXX-issue-title`
- Include GitHub PR links in Linear issues
- Add commit references in issue updates

### Issue Creation Guidelines
When creating Linear issues from Claude Code:
1. **Title**: Clear, actionable description
2. **Description**: Include:
   - Status (Todo/In Progress/Done)
   - Overview of work
   - Technical details
   - Related issues
   - GitHub references (PRs, commits)
   - Testing/validation notes
3. **Priority**: Set appropriate priority (Urgent/High/Medium/Low)
4. **Project**: Always assign to "IDFWU - IDEA Framework Unified"
5. **Team**: Always assign to "Pegues Innovations"
6. **Parent Issue**: Link to related parent issues when applicable
7. **Granularity**: All issue details must be maximally granular with full cross-platform references
8. **ID Tracking**: Always use Linear IDs (PEG-XXX) and GitHub PR/issue numbers consistently across all documentation and code

### Tracking Work Sessions
For each Claude Code session on IDFWU:
1. Start by checking Linear for relevant issues
2. Create or update issues as work progresses
3. Make commits with proper attribution
4. Create PRs with Linear references
5. Update Linear issues with completion status
6. Add session summary as Linear comment

### Example Workflow
```
1. Check Linear: mcp__linear-server__list_issues project:"IDFWU - IDEA Framework Unified"
2. Start work: Create/update Linear issue
3. Code changes: Commit with "PEG-XXX: Implement unified schema system"
4. Create PR: Reference Linear issues in description
5. Update Linear: Add PR link and mark as Done
```

## Specialized Agent Team for IDFWU Project

### Agent Team Structure

The IDFWU project utilizes a team of specialized agents organized into five departments:
- **Product Agents**: Vision, requirements, and user experience
- **Project Agents**: Planning, coordination, and tracking
- **Development Agents**: Implementation and technical execution
- **Integration Agents**: System integration and deployment
- **Quality Agents**: Testing, monitoring, and compliance

### Product Agents

#### ProductOwnerAgent (POA)
**Role**: Product vision and strategy
**Responsibilities**:
- Define product requirements and acceptance criteria
- Prioritize features and user stories
- Make decisions on scope and trade-offs
- Validate deliverables against business goals
**Linear Integration**: Creates epics and high-level features
**Slash Command**: `/agent-product-owner`

#### UserExperienceAgent (UXA)
**Role**: User experience and interface design
**Responsibilities**:
- Design user workflows and interactions
- Create UI/UX specifications
- Ensure accessibility compliance
- Validate usability of implementations
**Linear Integration**: Creates UX-related issues and design tasks
**Slash Command**: `/agent-ux`

#### RequirementsAnalystAgent (RAA)
**Role**: Requirements analysis and documentation
**Responsibilities**:
- Gather and document requirements
- Create user stories and acceptance criteria
- Maintain requirements traceability matrix
- Validate requirement coverage
**Linear Integration**: Links requirements to implementation tasks
**Slash Command**: `/agent-requirements`

### Project Agents

#### ProjectManagerAgent (PMA)
**Role**: Project coordination and tracking
**Responsibilities**:
- Manage sprint planning and execution
- Track progress and dependencies
- Coordinate agent activities
- Report project status
**Linear Integration**: Manages sprints and milestones
**Slash Command**: `/agent-project-manager`

#### ScrumMasterAgent (SMA)
**Role**: Agile process facilitation
**Responsibilities**:
- Facilitate daily standups (agent sync)
- Remove blockers for other agents
- Optimize team processes
- Ensure agile best practices
**Linear Integration**: Updates daily progress and blockers
**Slash Command**: `/agent-scrum-master`

#### ReleaseManagerAgent (RMA)
**Role**: Release coordination and deployment
**Responsibilities**:
- Plan release schedules
- Coordinate deployment activities
- Manage version control and tagging
- Create release notes
**Linear Integration**: Creates release milestones and tasks
**Slash Command**: `/agent-release-manager`

### Development Agents

#### ArchitectAgent (ARA)
**Role**: System architecture and design
**Responsibilities**:
- Design system architecture
- Make technology decisions
- Define integration patterns
- Review architectural changes
**Linear Integration**: Creates architecture decision records (ADRs)
**Slash Command**: `/agent-architect`

#### BackendDeveloperAgent (BDA)
**Role**: Backend implementation
**Responsibilities**:
- Implement server-side logic
- Create APIs and services
- Manage database operations
- Optimize backend performance
**Linear Integration**: Creates backend development tasks
**Slash Command**: `/agent-backend`

#### FrontendDeveloperAgent (FDA)
**Role**: Frontend implementation
**Responsibilities**:
- Implement user interfaces
- Create responsive designs
- Manage client-side state
- Optimize frontend performance
**Linear Integration**: Creates frontend development tasks
**Slash Command**: `/agent-frontend`

#### SchemaEngineerAgent (SEA)
**Role**: Schema design and integration
**Responsibilities**:
- Design and maintain schemas (IDFW & Force)
- Implement schema conversions
- Validate data structures
- Optimize schema performance
**Linear Integration**: Creates schema-related tasks
**Slash Command**: `/agent-schema`

#### AgentDeveloperAgent (ADA)
**Role**: Agent system implementation
**Responsibilities**:
- Implement new agents
- Maintain agent orchestration
- Optimize agent communication
- Debug agent interactions
**Linear Integration**: Creates agent development tasks
**Slash Command**: `/agent-developer`

### Integration Agents

#### SystemIntegratorAgent (SIA)
**Role**: System integration and interfaces
**Responsibilities**:
- Integrate IDFW with Dev Sentinel
- Implement MCP protocols
- Manage API integrations
- Ensure system interoperability
**Linear Integration**: Creates integration tasks and tracks dependencies
**Slash Command**: `/agent-integrator`

#### DevOpsAgent (DOA)
**Role**: Infrastructure and automation
**Responsibilities**:
- Manage CI/CD pipelines
- Configure infrastructure
- Automate deployment processes
- Monitor system health
**Linear Integration**: Creates infrastructure and automation tasks
**Slash Command**: `/agent-devops`

#### DatabaseAdminAgent (DBA)
**Role**: Database management and optimization
**Responsibilities**:
- Design database schemas
- Optimize queries and indexes
- Manage data migrations
- Ensure data integrity
**Linear Integration**: Creates database-related tasks
**Slash Command**: `/agent-dba`

### Quality Agents

#### QualityAssuranceAgent (QAA)
**Role**: Testing and quality control
**Responsibilities**:
- Create and execute test plans
- Perform integration testing
- Validate acceptance criteria
- Report quality metrics
**Linear Integration**: Creates test cases and bug reports
**Slash Command**: `/agent-qa`

#### SecurityAuditorAgent (SAA)
**Role**: Security analysis and compliance
**Responsibilities**:
- Perform security audits
- Identify vulnerabilities
- Ensure compliance with standards
- Review security implementations
**Linear Integration**: Creates security issues and audit tasks
**Slash Command**: `/agent-security`

#### PerformanceEngineerAgent (PEA)
**Role**: Performance optimization and monitoring
**Responsibilities**:
- Profile system performance
- Identify bottlenecks
- Optimize resource usage
- Create performance benchmarks
**Linear Integration**: Creates performance optimization tasks
**Slash Command**: `/agent-performance`

#### DocumentationAgent (DOC)
**Role**: Documentation and knowledge management
**Responsibilities**:
- Create technical documentation
- Maintain API documentation
- Update user guides
- Ensure documentation completeness
**Linear Integration**: Creates documentation tasks
**Slash Command**: `/agent-documentation`

### Agent Orchestration Commands

#### /deploy-agent-team
Deploys all agents concurrently for maximum parallel execution.
**Usage**: `/deploy-agent-team [department]`
**Options**:
- `--all`: Deploy all agents (default)
- `--product`: Deploy product agents only
- `--project`: Deploy project management agents only
- `--development`: Deploy development agents only
- `--integration`: Deploy integration agents only
- `--quality`: Deploy quality agents only

#### /agent-status
Shows current status of all deployed agents.
**Usage**: `/agent-status [agent-id]`
**Options**:
- `--active`: Show only active agents
- `--idle`: Show idle agents
- `--failed`: Show failed agents
- `--metrics`: Include performance metrics

#### /agent-sync
Synchronizes all agents and redistributes tasks based on current priorities.
**Usage**: `/agent-sync`
**Options**:
- `--force`: Force immediate synchronization
- `--rebalance`: Rebalance task distribution
- `--report`: Generate sync report

### Agent Communication Protocol

Agents communicate through a structured message bus with the following patterns:

1. **Direct Communication**: Agent-to-agent messages for coordination
2. **Broadcast**: Department-wide or team-wide announcements
3. **Request/Response**: Service-style interactions between agents
4. **Event Streaming**: Real-time updates on task progress

### Agent Task Distribution

Tasks are distributed based on:
- **Expertise**: Matching agent specialization to task requirements
- **Availability**: Current agent workload and capacity
- **Priority**: Linear issue priority and sprint goals
- **Dependencies**: Task dependencies and sequencing

### Available Slash Commands

#### /fix-schema-conflicts
Resolves schema conflicts between IDFW and Dev Sentinel. Validates schemas, creates mapping functions, implements conversion utilities, ensures backward compatibility.

#### /implement-unified-cli
Builds unified command-line interface. Creates command router, integrates YUNG and IDFW commands, implements plugin system, adds interactive shell.

#### /setup-mcp-server
Configures unified MCP server. Merges tool registrations, implements protocol handlers, creates VS Code integration, sets up transport layers.

#### /wrap-idfw-generators
Converts IDFW generators to agents. Creates agent wrappers, implements message bus integration, sets up state synchronization, adds task management.

#### /create-state-manager
Builds unified state management. Integrates IDFW variables with agent states, implements conflict resolution, adds persistence layer, creates state observers.

#### /implement-schema-bridge
Creates schema bridging system. Builds conversion functions, implements validation layers, adds type mappings, creates schema registry.

#### /setup-testing-framework
Establishes comprehensive testing. Creates unit tests for components, integration tests for systems, E2E tests for workflows, performance benchmarks.

#### /document-api
Generates API documentation. Creates OpenAPI specs, documents endpoints, generates client SDKs, creates usage examples.

#### /create-linear-epic
Creates Linear epic for major features. Sets up issue hierarchy, defines acceptance criteria, creates sub-tasks, links dependencies.

#### /deploy-monitoring
Sets up monitoring infrastructure. Implements logging, adds metrics collection, creates dashboards, sets up alerting.

#### /autofix
Automatically launches all priority fix agents concurrently to resolve critical issues. Runs fix-schema-conflicts, setup-mcp-server, and implement-unified-cli in parallel. Prioritizes integration blockers and compatibility issues. Creates comprehensive fix report. Always uses /watch-deployment after pushing fixes.

#### /watch-deployment [options]
Monitors Vercel deployment status until completion and verifies the deployed site.
**Options:**
- `--pr <number>`: PR number to monitor (default: checks open PRs)
- `--url <url>`: Specific deployment URL to check
- `--interval <seconds>`: Check interval (default: 30s)
- `--timeout <minutes>`: Maximum wait time (default: 10min)
**Integration**: Other agents should use this after pushing to staging to verify deployments

#### /update-project-status [options]
Creates comprehensive project status updates on Linear. Posts detailed analysis as new issues or comments.

**Options:**
- `--all` : Create full status update with all metrics (default)
- `--issue` : Create as new Linear issue (default)
- `--comment <issue-id>` : Post as comment on existing issue
- `--summary` : Generate status summary without posting
- `--technical` : Include deep technical analysis
- `--metrics` : Focus on project metrics and KPIs
- `--deployments` : Include recent deployment history

**Examples:**
- `/update-project-status` - Creates new Linear issue with full status
- `/update-project-status --comment PEG-XXX` - Adds status to existing issue
- `/update-project-status --summary` - Shows status without posting
- `/update-project-status --technical --deployments` - Technical deep-dive with deployment history

**Extended Actions:**
1. Analyzes current project state and recent changes
2. Reviews deployment history and build status
3. Compiles technical metrics and test coverage
4. Generates comprehensive markdown report
5. Posts to Linear with proper formatting and links
6. Includes root cause analysis for resolved issues
7. Documents lessons learned and next steps
8. Adds progress comments to issues
9. Cross-references Linear PEG-XXX IDs with GitHub issue numbers
10. Generates sprint velocity and progress metrics

### Agent Execution Rules
- All agents run concurrently unless dependencies require ordering
- Automatic rate limit handling with exponential backoff on API 429 errors
- Always run build and tests before marking tasks complete
- Create Linear issues for all detected problems
- Maintain PEG-XXX references across all platforms

## IDFW-Specific Configuration

### Schema Namespace Organization
```
idfw/
├── documents/      # IDFW document schemas
├── diagrams/       # IDFW diagram schemas
├── variables/      # IDFW variable schemas
└── projects/       # IDFW project schemas

force/
├── tools/          # Force tool schemas
├── patterns/       # Force pattern schemas
├── constraints/    # Force constraint schemas
└── governance/     # Force governance schemas

unified/
├── commands/       # Unified command schemas
├── workflows/      # Unified workflow schemas
└── integrations/   # Integration schemas
```

### Command Prefix Configuration
- `$` - YUNG commands (existing Dev Sentinel)
- `@` - IDFW actions (new)
- `#` - Unified framework commands (new)
- `/` - Slash commands for agents

### State Synchronization
- IDFW immutable variables → Agent configuration
- IDFW mutable variables → Agent runtime state
- Project variables → Task context
- Document variables → Tool parameters

## Development Standards

### Code Organization
```
unified_framework/
├── core/           # Core integration components
├── schemas/        # Unified schema definitions
├── commands/       # Command processors
├── agents/         # Agent implementations
├── mcp/           # MCP server implementations
└── tests/         # Test suites
```

### Testing Requirements
- Unit test coverage minimum: 80%
- Integration tests for all major workflows
- E2E tests for critical user journeys
- Performance benchmarks for key operations

### Documentation Standards
- API documentation using OpenAPI 3.0
- Architecture diagrams using Mermaid
- User guides with examples
- Developer documentation with setup instructions

## Monitoring and Alerts

### Key Metrics to Track
- Command execution time
- Agent task completion rate
- Schema validation success rate
- State synchronization latency
- Error rates by component

### Alert Thresholds
- Command execution > 5 seconds
- Agent failure rate > 5%
- Schema validation failure > 10%
- State sync delay > 1 second

## Important Notes

- This project unifies two major frameworks - maintain clear separation of concerns
- Always ensure backward compatibility when making changes
- Document all design decisions in Linear issues
- Use feature flags for experimental features
- Maintain comprehensive test coverage for all integration points

---

*Project Configuration Version: 1.0.0*
*Last Updated: 2025-09-29*
*Linear Project: IDFWU - IDEA Framework Unified*