# /watch-deployment

## Description
Monitors deployment status until completion and verifies deployed applications. Tracks build progress, deployment health, and creates Linear updates (Project ID: 4d649a6501f7) for deployment tracking.

## Tasks
1. Monitor build and deployment pipelines
2. Track deployment progress in real-time
3. Verify application health post-deployment
4. Check deployment environment status
5. Validate critical functionality
6. Monitor performance metrics
7. Create deployment status reports
8. Update Linear issues with deployment status
9. Alert on deployment failures or issues
10. Verify rollback procedures if needed
11. Document deployment lessons learned
12. Create post-deployment monitoring

## Usage Example
```bash
/watch-deployment [options]
```

**Options:**
- `--pr <number>`: PR number to monitor (default: checks open PRs)
- `--url <url>`: Specific deployment URL to check
- `--interval <seconds>`: Check interval (default: 30s)
- `--timeout <minutes>`: Maximum wait time (default: 10min)

## Expected Output
- Real-time deployment status monitoring
- Build pipeline progress tracked
- Application health verified
- Performance metrics collected
- Status reports generated
- Linear issues updated with progress
- Alerts sent for critical issues
- Rollback procedures documented
- Lessons learned captured
- Post-deployment monitoring active

## Success Criteria
- Deployment completes successfully
- Application health verified
- Performance within acceptable ranges
- Team informed of deployment status
- Linear project tracking updated
- Issues documented and addressed