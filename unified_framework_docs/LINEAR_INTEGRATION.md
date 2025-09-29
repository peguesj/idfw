# Linear Integration Guide for IDFW Unified Framework

## Project Information
**Project ID**: 4d649a6501f7
**Project URL**: https://linear.app/projects/4d649a6501f7
**Team**: IDFWU (IDFW Unified Framework)

## Overview

This guide outlines the comprehensive integration strategy between the IDFW Unified Framework and Linear project management. The integration ensures complete traceability, automated progress tracking, and seamless workflow coordination.

## Linear Project Structure

### Epic Hierarchy

#### Parent Epic: IDFW Unified Framework
- **Epic ID**: IDFWU-MAIN
- **Description**: Complete unification of IDFW and Dev Sentinel frameworks
- **Timeline**: 10-week implementation cycle
- **Status**: In Progress

#### Child Epics

1. **Foundation & Schema Integration** (IDFWU-FOUNDATION)
   - Schema mapping framework
   - Unified directory structure
   - Basic command routing
   - Validation layer implementation

2. **Command System Unification** (IDFWU-COMMANDS)
   - YUNG command extension
   - Unified CLI development
   - Command mapping and routing
   - Context-aware execution

3. **Agent Integration Framework** (IDFWU-AGENTS)
   - IDFW generator wrapping
   - Message bus integration
   - State synchronization
   - Task orchestration

4. **Protocol & MCP Implementation** (IDFWU-PROTOCOL)
   - MCP server development
   - VS Code extension updates
   - Transport layer implementation
   - Protocol testing

5. **Testing & Documentation** (IDFWU-TESTING)
   - Comprehensive test suite
   - API documentation
   - Integration guides
   - Performance benchmarking

## Issue Creation Guidelines

### Issue Templates

#### Feature Implementation
```markdown
## Summary
Brief description of the feature to be implemented

## Epic
Link to parent epic: IDFWU-[EPIC-NAME]

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

## Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2
- [ ] Criteria 3

## Technical Details
- Implementation approach
- Dependencies
- Risk factors

## Related Issues
- Blocks: IDFWU-XXX
- Related: IDFWU-YYY

## Testing Plan
- Unit tests required
- Integration tests required
- Manual testing steps

## Documentation Updates
- API docs
- User guides
- Technical specs
```

#### Bug Report
```markdown
## Bug Description
Clear description of the issue

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS:
- Node.js version:
- IDFW version:

## Related Code
Link to relevant files or components

## Severity
- [ ] Critical (Blocks development)
- [ ] High (Major feature impact)
- [ ] Medium (Minor feature impact)
- [ ] Low (Cosmetic/Enhancement)
```

### Issue Labeling System

#### Priority Labels
- `Priority: Critical` - Blocks development or deployment
- `Priority: High` - Major feature impact
- `Priority: Medium` - Standard feature work
- `Priority: Low` - Enhancement or cleanup

#### Component Labels
- `Component: Schema` - Schema-related work
- `Component: CLI` - Command-line interface
- `Component: Agent` - Agent system
- `Component: MCP` - MCP protocol integration
- `Component: Testing` - Test framework
- `Component: Docs` - Documentation

#### Type Labels
- `Type: Feature` - New functionality
- `Type: Bug` - Bug fixes
- `Type: Enhancement` - Improvements to existing features
- `Type: Refactor` - Code refactoring
- `Type: Documentation` - Documentation updates

#### Status Labels
- `Status: Blocked` - Cannot proceed due to dependencies
- `Status: In Review` - Under code review
- `Status: Ready for QA` - Ready for quality assurance
- `Status: Deployed` - Deployed to production

## Sprint Planning Strategy

### Sprint Duration
- **Length**: 2 weeks
- **Capacity**: Based on team velocity
- **Planning**: Every 2 weeks with retrospectives

### Sprint Goals Alignment
Each sprint should align with the current implementation phase:

#### Phase 1 Sprints (Weeks 1-2)
- Sprint 1: Foundation setup and schema mapping
- Focus: Core infrastructure and project structure

#### Phase 2 Sprints (Weeks 3-4)
- Sprint 2: Schema integration and validation
- Focus: Schema merging and conflict resolution

#### Phase 3 Sprints (Weeks 5-6)
- Sprint 3: Command system unification
- Focus: CLI development and command routing

#### Phase 4 Sprints (Weeks 7-8)
- Sprint 4: Agent integration and orchestration
- Focus: Agent wrapping and message bus

#### Phase 5 Sprints (Weeks 9-10)
- Sprint 5: Protocol implementation and deployment
- Focus: MCP integration and testing

### Story Point Estimation
- **1 Point**: Simple configuration or documentation updates
- **2 Points**: Basic feature implementation
- **3 Points**: Standard feature with testing
- **5 Points**: Complex feature requiring integration
- **8 Points**: Major component development
- **13 Points**: Epic-level work (should be broken down)

## Progress Tracking Strategies

### Automated Status Updates
Configure automated Linear updates for:
- CI/CD pipeline status
- Test execution results
- Deployment status
- Code review completion

### Milestone Tracking
Create milestones for each phase completion:
- **Foundation Complete**: All basic infrastructure ready
- **Schema Integration Complete**: Unified schemas working
- **Command System Complete**: Unified CLI functional
- **Agent Integration Complete**: All agents operational
- **Protocol Complete**: MCP integration deployed

### Metrics Dashboard
Track key metrics in Linear:
- Sprint velocity
- Burndown charts
- Issue cycle time
- Bug resolution rate
- Test coverage trends

## Integration with Development Workflow

### Git Integration
- Include Linear issue IDs in commit messages: `IDFWU-123: Implement schema bridge`
- Link pull requests to Linear issues
- Automated status updates on merge

### Code Review Process
- Require Linear issue link in PR descriptions
- Update issue status during code review
- Link review comments to relevant issues

### CI/CD Integration
- Post build status to related Linear issues
- Create issues for build failures
- Update deployment status automatically

### Testing Integration
- Link test failures to relevant issues
- Track test coverage per component
- Create issues for test gaps

## Slash Command Integration

The following slash commands are integrated with Linear tracking:

### Project Management Commands
- `/create-linear-epic` - Creates comprehensive Linear epics
- `/update-project-status` - Posts detailed project status updates
- `/watch-deployment` - Monitors deployments with Linear updates

### Development Commands
- `/setup-mcp-server` - MCP server setup with progress tracking
- `/implement-schema-bridge` - Schema integration with Linear issues
- `/create-state-manager` - State management with milestone tracking
- `/autofix` - Automated fixes with issue creation

### Monitoring Commands
- `/deploy-monitoring` - Monitoring setup with Linear integration
- `/setup-testing-framework` - Test framework with progress tracking

## Best Practices

### Issue Management
1. **Keep issues atomic**: One issue per feature or bug
2. **Use descriptive titles**: Clear, searchable issue names
3. **Link related issues**: Use blocks/blocked by relationships
4. **Update regularly**: Keep status and progress current
5. **Close promptly**: Close completed issues immediately

### Communication
1. **Use issue comments**: Document decisions and progress
2. **Tag relevant team members**: Ensure visibility
3. **Reference code**: Link to commits and PRs
4. **Document blockers**: Clearly identify and escalate issues

### Documentation
1. **Update documentation**: Keep Linear descriptions current
2. **Link external resources**: Connect to relevant documentation
3. **Maintain traceability**: Clear links between issues and code
4. **Archive completed work**: Maintain historical context

## Reporting and Analytics

### Weekly Reports
Generate weekly reports including:
- Sprint progress summary
- Blocked issues status
- Velocity trends
- Risk assessment

### Monthly Reviews
Monthly reviews should cover:
- Epic progress against timeline
- Resource allocation effectiveness
- Process improvements
- Stakeholder updates

### Project Dashboard
Maintain a real-time dashboard showing:
- Overall project health
- Current sprint status
- Critical path items
- Resource utilization

## Troubleshooting Common Issues

### Integration Problems
- **Issue**: Linear API rate limits
- **Solution**: Implement exponential backoff and caching

- **Issue**: Webhook failures
- **Solution**: Retry mechanism with dead letter queue

### Workflow Issues
- **Issue**: Issues not updating automatically
- **Solution**: Check webhook configuration and API permissions

- **Issue**: Duplicate issues created
- **Solution**: Implement deduplication logic

### Performance Issues
- **Issue**: Slow Linear queries
- **Solution**: Optimize queries and implement caching

- **Issue**: High API usage
- **Solution**: Batch operations and reduce polling frequency

## Migration Strategy

### From Existing Project Management
1. **Export existing data**: Issues, milestones, documentation
2. **Map to Linear structure**: Epics, issues, labels
3. **Import systematically**: Maintain relationships
4. **Validate migration**: Ensure data integrity
5. **Update team processes**: Train on new workflow

### Timeline
- **Week 1**: Setup Linear project and configure integrations
- **Week 2**: Create epic structure and initial issues
- **Week 3**: Migrate existing issues and documentation
- **Week 4**: Train team and refine processes
- **Week 5**: Full adoption and monitoring

## Support and Resources

### Documentation Links
- [Linear API Documentation](https://developers.linear.app/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [IDFW Framework Documentation](./README.md)

### Team Contacts
- **Project Lead**: TBD
- **Linear Admin**: TBD
- **Technical Lead**: TBD

### Training Resources
- Linear workspace orientation
- Issue management best practices
- Integration troubleshooting guide

---

*Document Version: 1.0.0*
*Date: 2025-09-29*
*Linear Project ID: 4d649a6501f7*
*Status: Initial Implementation*