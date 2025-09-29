# Agent Status Slash Command

## Command Definition
```
/agent-status [options]
```

## Purpose
Monitor and report on the status of IDFWU agents, including active deployments, performance metrics, health checks, and resource utilization. This command provides comprehensive visibility into the agent orchestration system.

## Command Options

### Status Scope
- `--all` : Show status of all agents (default)
- `--active` : Show only currently active agents
- `--department {name}` : Show agents from specific department (product|project|development|integration|quality)
- `--agent {name}` : Show status of specific agent
- `--team {deployment-id}` : Show status of specific team deployment

### Detail Level
- `--summary` : Brief overview of agent status (default)
- `--detailed` : Comprehensive status information
- `--metrics` : Performance metrics and statistics
- `--health` : Health check and diagnostics information
- `--resources` : Resource utilization and capacity

### Time Range
- `--last {duration}` : Show status for last N minutes/hours/days (e.g., --last 1h)
- `--since {timestamp}` : Show status since specific timestamp
- `--real-time` : Live updating status (refreshes every 30 seconds)

### Output Format
- `--format {table|json|yaml}` : Output format (default: table)
- `--export {filename}` : Export status to file
- `--dashboard` : Open web-based status dashboard

## Usage Examples

### Basic Status Check
```bash
/agent-status
```
Shows summary of all agents with current status.

### Department Status
```bash
/agent-status --department development --detailed
```
Detailed status of all development team agents.

### Active Deployments
```bash
/agent-status --active --metrics --real-time
```
Live monitoring of active agents with performance metrics.

### Specific Agent Health Check
```bash
/agent-status --agent BackendDeveloperAgent --health --detailed
```
Comprehensive health check for BackendDeveloperAgent.

### Team Deployment Status
```bash
/agent-status --team deploy-20241201-001 --detailed
```
Status of specific team deployment with full details.

### Export Status Report
```bash
/agent-status --all --detailed --format json --export agent-status-report.json
```
Export comprehensive status report to JSON file.

## Status Information

### Agent States
- **Idle** : Agent available but not currently executing tasks
- **Active** : Agent currently executing assigned tasks
- **Busy** : Agent at capacity, queuing new tasks
- **Blocked** : Agent waiting for dependencies or resources
- **Failed** : Agent encountered error and requires attention
- **Maintenance** : Agent temporarily unavailable for maintenance
- **Offline** : Agent not responding or unavailable

### Health Indicators
- **🟢 Healthy** : All systems operational
- **🟡 Warning** : Minor issues or resource constraints
- **🔴 Critical** : Significant issues requiring immediate attention
- **⚫ Offline** : Agent not responding

### Performance Metrics
- **Response Time** : Average task response time
- **Throughput** : Tasks completed per hour
- **Success Rate** : Percentage of successful task completions
- **Error Rate** : Percentage of failed tasks
- **Uptime** : Time since last restart or failure

## Status Display Formats

### Summary Table Format
```
AGENT                    STATUS    HEALTH    TASKS    UPTIME    LAST SEEN
ProductOwnerAgent        Active    🟢        3/5      2d 4h     2 min ago
ArchitectAgent          Idle      🟢        0/3      1d 12h    1 min ago
BackendDeveloperAgent   Busy      🟡        5/5      3d 1h     30 sec ago
SecurityAuditorAgent    Blocked   🟡        1/3      1d 8h     5 min ago
QualityAssuranceAgent   Failed    🔴        0/4      6h 15m    15 min ago
```

### Detailed Format
```
Agent: BackendDeveloperAgent
Status: Active
Health: 🟢 Healthy
Department: development
Current Tasks: 3/5
Queue Depth: 2 tasks pending

Performance Metrics:
- Response Time: 145ms (avg)
- Throughput: 12 tasks/hour
- Success Rate: 94.2%
- Error Rate: 5.8%
- Uptime: 3d 1h 23m

Resource Utilization:
- CPU: 72%
- Memory: 1.2GB / 2GB (60%)
- API Quota: 450/1000 calls/hour
- Storage: 45MB / 1GB

Current Tasks:
1. [API-DEV] User profile endpoint - 45% complete
2. [INTEGRATION] Payment gateway integration - 23% complete
3. [OPTIMIZATION] Database query performance - 78% complete

Recent Activity:
- 2 min ago: Completed authentication middleware implementation
- 5 min ago: Started payment gateway integration
- 8 min ago: Updated API documentation for user endpoints
```

### Metrics Format
```
Department Performance Summary:

Development Department:
├── ArchitectAgent: 98.5% uptime, 8.2 tasks/day avg
├── BackendDeveloperAgent: 94.2% uptime, 15.7 tasks/day avg
├── FrontendDeveloperAgent: 96.8% uptime, 12.3 tasks/day avg
├── SchemaEngineerAgent: 99.1% uptime, 6.5 tasks/day avg
└── AgentDeveloperAgent: 91.3% uptime, 4.8 tasks/day avg

Quality Department:
├── QualityAssuranceAgent: 87.6% uptime, 18.9 tasks/day avg
├── SecurityAuditorAgent: 95.4% uptime, 7.2 tasks/day avg
├── PerformanceEngineerAgent: 93.7% uptime, 9.1 tasks/day avg
└── DocumentationAgent: 98.2% uptime, 11.4 tasks/day avg

System-wide Metrics:
- Total Active Agents: 12/20
- Average Response Time: 187ms
- System Throughput: 156 tasks/hour
- Overall Success Rate: 92.8%
- Critical Issues: 1 (SecurityAuditorAgent timeout)
```

## Health Check Details

### Agent Health Indicators
1. **API Connectivity**: Connection to required services
2. **Resource Availability**: CPU, memory, storage capacity
3. **Task Queue Status**: Queue depth and processing rate
4. **Error Rates**: Recent error frequency and patterns
5. **Response Times**: Task execution performance
6. **Dependencies**: Status of required external services

### System Health Indicators
1. **Message Bus**: Inter-agent communication health
2. **Linear Integration**: API connectivity and quota status
3. **Database Connectivity**: Agent state storage access
4. **Resource Pool**: Overall system resource availability
5. **Load Distribution**: Agent workload balance

### Health Check Procedures
- **Ping Test**: Basic agent responsiveness
- **Functional Test**: Execute simple test task
- **Resource Check**: Verify adequate resources available
- **Dependency Validation**: Check external service connectivity
- **Performance Benchmark**: Compare against baseline metrics

## Performance Analytics

### Key Performance Indicators (KPIs)
- **Agent Availability**: Percentage of time agents are operational
- **Task Completion Rate**: Successful task completion percentage
- **Average Response Time**: Mean time to complete tasks
- **Resource Efficiency**: Optimal resource utilization rates
- **Error Resolution Time**: Mean time to resolve agent issues

### Trend Analysis
- **Performance Trends**: Task completion rates over time
- **Resource Usage Patterns**: Peak and low usage periods
- **Error Frequency**: Error rate trends and patterns
- **Capacity Planning**: Projected resource needs

### Benchmarking
- **Department Comparison**: Performance across departments
- **Agent Comparison**: Individual agent performance metrics
- **Historical Comparison**: Current vs. past performance
- **Target Achievement**: Progress toward performance goals

## Resource Monitoring

### Computational Resources
- **CPU Usage**: Processing power utilization
- **Memory Consumption**: RAM usage and availability
- **Storage Usage**: Disk space utilization
- **Network Bandwidth**: Data transfer rates

### API Resources
- **Claude API Quota**: Token usage and limits
- **Linear API Quota**: Request limits and usage
- **GitHub API Quota**: Repository access limits
- **External Service Quotas**: Third-party API limits

### Queue Management
- **Task Queue Depth**: Number of pending tasks
- **Queue Processing Rate**: Tasks processed per unit time
- **Queue Wait Times**: Average time tasks spend queued
- **Priority Distribution**: Task priority breakdown

## Alert and Notification System

### Alert Levels
- **Info**: General status updates and completions
- **Warning**: Performance degradation or resource constraints
- **Critical**: Agent failures or system-wide issues
- **Emergency**: Complete system failure or security breaches

### Alert Triggers
- **Agent Unresponsive**: No response for >5 minutes
- **High Error Rate**: >10% task failure rate
- **Resource Exhaustion**: >90% resource utilization
- **Queue Backup**: >20 tasks queued for single agent
- **Performance Degradation**: >50% increase in response time

### Notification Channels
- **Linear Comments**: Status updates in related issues
- **Slack Alerts**: Real-time team notifications
- **Email Reports**: Daily/weekly status summaries
- **Dashboard Alerts**: Visual indicators in status dashboard

## Troubleshooting Integration

### Automatic Issue Detection
- **Performance Anomalies**: Unusual response time patterns
- **Resource Leaks**: Gradual resource consumption increase
- **Communication Failures**: Inter-agent message failures
- **Dependency Issues**: External service connectivity problems

### Diagnostic Tools
- **Agent Logs**: Detailed execution and error logs
- **Performance Profiling**: Resource usage analysis
- **Communication Tracing**: Message flow visualization
- **Dependency Mapping**: Service dependency visualization

### Remediation Suggestions
- **Restart Recommendations**: When to restart agents
- **Resource Optimization**: How to improve resource usage
- **Load Balancing**: Task redistribution suggestions
- **Capacity Scaling**: When to add agent capacity

## Integration with Agent Orchestration

### Deployment Status
- **Active Deployments**: Currently running agent teams
- **Deployment History**: Recent team deployment records
- **Success Rates**: Team deployment success statistics
- **Resource Allocation**: How resources are distributed across teams

### Coordination Metrics
- **Inter-agent Communication**: Message passing efficiency
- **Dependency Resolution**: Time to resolve blocking dependencies
- **Synchronization Overhead**: Time spent on coordination
- **Conflict Resolution**: Frequency and resolution of agent conflicts

## Data Export and Reporting

### Export Formats
- **JSON**: Machine-readable structured data
- **CSV**: Spreadsheet-compatible format
- **YAML**: Human-readable configuration format
- **PDF**: Formatted reports for stakeholders

### Report Types
- **Executive Summary**: High-level status overview
- **Technical Report**: Detailed technical metrics
- **Performance Report**: Comprehensive performance analysis
- **Incident Report**: Focused on issues and resolutions

### Automated Reporting
- **Daily Status**: Automated daily status emails
- **Weekly Performance**: Weekly performance trend reports
- **Monthly Analytics**: Comprehensive monthly analysis
- **Incident Alerts**: Real-time issue notifications

## Historical Data and Trends

### Data Retention
- **Real-time Data**: Last 24 hours at minute granularity
- **Hourly Aggregates**: Last 30 days at hourly granularity
- **Daily Aggregates**: Last 365 days at daily granularity
- **Monthly Aggregates**: Indefinite retention for trend analysis

### Trend Visualization
- **Performance Graphs**: Task completion rates over time
- **Resource Charts**: Resource utilization trends
- **Error Analysis**: Error frequency and pattern analysis
- **Capacity Trends**: Resource usage growth patterns

## Best Practices

### Regular Monitoring
- **Daily Health Checks**: Review agent health status daily
- **Weekly Performance Review**: Analyze performance trends weekly
- **Monthly Capacity Planning**: Review resource needs monthly
- **Quarterly Optimization**: Comprehensive system optimization

### Proactive Management
- **Threshold Monitoring**: Set appropriate alert thresholds
- **Predictive Analysis**: Use trends to predict issues
- **Resource Planning**: Plan for capacity needs in advance
- **Performance Optimization**: Continuously optimize agent performance

### Incident Response
- **Quick Assessment**: Use status command for rapid issue assessment
- **Root Cause Analysis**: Leverage detailed metrics for diagnosis
- **Impact Assessment**: Understand business impact of agent issues
- **Communication**: Keep stakeholders informed of agent status