#!/usr/bin/env python3
"""
Linear Integration Utility for IDFWU
Provides enhanced Linear MCP integration with comprehensive project management features.
"""

import os
import sys
import json
from pathlib import Path
import requests
import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LinearIssue:
    """Data class for Linear issue representation"""
    id: str
    identifier: str
    title: str
    description: str
    state: str
    priority: int
    progress: float
    assignee: Optional[str]
    labels: List[str]
    created_at: str
    updated_at: str
    parent_id: Optional[str] = None
    project_id: Optional[str] = None

class LinearIntegration:
    """Enhanced Linear MCP integration for IDFWU project management"""
    
    def __init__(self, config_path: str = None):
        """Initialize Linear integration with configuration"""
        self.config = self._load_config(config_path)
        self.api_key = self._get_api_key()
        self.base_url = self.config.get('linear', {}).get('base_url', 'https://api.linear.app/graphql')
        self.project_id = self.config.get('linear', {}).get('project_id')
        self.team = self.config.get('linear', {}).get('team')
        self.workspace = self.config.get('linear', {}).get('workspace')
        
        if not self.api_key:
            raise ValueError("Linear API key not found. Please set LINEAR_API_KEY environment variable or update config.")
        
        self.headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
        
        logger.info(f"Linear integration initialized for project: {self.project_id}")
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            return {}
    
    def _get_api_key(self) -> str:
        """Get API key from environment variable or config"""
        # Try environment variable first
        api_key = os.getenv('LINEAR_API_KEY')
        if api_key:
            return api_key
        
        # Fall back to config file
        return self.config.get('linear', {}).get('api_key', '')
    
    def _make_graphql_request(self, query: str, variables: Dict = None) -> Dict[str, Any]:
        """Make GraphQL request to Linear API"""
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            if 'errors' in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                raise Exception(f"GraphQL errors: {data['errors']}")
            
            return data.get('data', {})
        
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"GraphQL request failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test connection to Linear API"""
        query = '''
        query {
            viewer {
                id
                name
                email
            }
        }
        '''
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={'query': query},
                timeout=30
            )
            
            # Debug: Print response details
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 401:
                logger.error("Authentication failed. Please check your Linear API key.")
                return False
            elif response.status_code == 400:
                logger.error(f"Bad request. Response: {response.text}")
                return False
            
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return False
            
            viewer = data.get('data', {}).get('viewer')
            if viewer:
                logger.info(f"Successfully connected to Linear as: {viewer['name']} ({viewer['email']})")
                return True
            else:
                logger.error("Failed to get viewer information")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Connection test failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get project information"""
        query = '''
        query($projectId: String!) {
            project(id: $projectId) {
                id
                name
                description
                state
                progress
                createdAt
                updatedAt
                lead {
                    id
                    name
                    email
                }
                teams {
                    nodes {
                        id
                        name
                        key
                    }
                }
                issues {
                    nodes {
                        id
                        identifier
                        title
                        state {
                            name
                        }
                        priority
                        assignee {
                            name
                        }
                    }
                }
            }
        }
        '''
        
        try:
            data = self._make_graphql_request(query, {'projectId': self.project_id})
            return data.get('project', {})
        except Exception as e:
            logger.error(f"Failed to get project info: {e}")
            return {}
    
    def list_issues(self, filter_params: Dict = None) -> List[LinearIssue]:
        """List issues in the project"""
        query = '''
        query($projectId: String!, $first: Int, $after: String) {
            project(id: $projectId) {
                issues(first: $first, after: $after) {
                    nodes {
                        id
                        identifier
                        title
                        description
                        state {
                            name
                        }
                        priority
                        assignee {
                            name
                        }
                        labels {
                            nodes {
                                name
                            }
                        }
                        createdAt
                        updatedAt
                        parent {
                            id
                        }
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
        '''
        
        variables = {
            'projectId': self.project_id,
            'first': 50
        }
        
        issues = []
        try:
            data = self._make_graphql_request(query, variables)
            project = data.get('project', {})
            issues_data = project.get('issues', {}).get('nodes', [])
            
            for issue_data in issues_data:
                issue = LinearIssue(
                    id=issue_data['id'],
                    identifier=issue_data['identifier'],
                    title=issue_data['title'],
                    description=issue_data.get('description', ''),
                    state=issue_data['state']['name'],
                    priority=issue_data.get('priority', 0),
                    progress=0.0,  # Calculate based on state
                    assignee=issue_data['assignee']['name'] if issue_data.get('assignee') else None,
                    labels=[label['name'] for label in issue_data.get('labels', {}).get('nodes', [])],
                    created_at=issue_data['createdAt'],
                    updated_at=issue_data['updatedAt'],
                    parent_id=issue_data['parent']['id'] if issue_data.get('parent') else None,
                    project_id=self.project_id
                )
                issues.append(issue)
            
            logger.info(f"Retrieved {len(issues)} issues from project")
            return issues
            
        except Exception as e:
            logger.error(f"Failed to list issues: {e}")
            return []
    
    def create_issue(self, title: str, description: str = '', **kwargs) -> Dict[str, Any]:
        """Create a new issue in the project"""
        mutation = '''
        mutation($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    state {
                        name
                    }
                }
            }
        }
        '''
        
        # Get team ID for the project
        team_id = self._get_team_id()
        if not team_id:
            raise ValueError("Unable to determine team ID for issue creation")
        
        input_data = {
            'title': title,
            'description': description,
            'teamId': team_id,
            'projectId': self.project_id
        }
        
        # Add optional parameters
        if 'priority' in kwargs:
            input_data['priority'] = kwargs['priority']
        if 'assigneeId' in kwargs:
            input_data['assigneeId'] = kwargs['assigneeId']
        if 'parentId' in kwargs:
            input_data['parentId'] = kwargs['parentId']
        if 'labelIds' in kwargs:
            input_data['labelIds'] = kwargs['labelIds']
        
        try:
            data = self._make_graphql_request(mutation, {'input': input_data})
            result = data.get('issueCreate', {})
            
            if result.get('success'):
                issue = result.get('issue', {})
                logger.info(f"Created issue: {issue['identifier']} - {issue['title']}")
                return issue
            else:
                logger.error("Failed to create issue")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            return {}
    
    def _get_team_id(self) -> str:
        """Get team ID for the configured team"""
        query = '''
        query($teamKey: String!) {
            team(id: $teamKey) {
                id
                name
                key
            }
        }
        '''
        
        try:
            # Try with team name/key from config
            team_identifier = self.team or self.workspace
            data = self._make_graphql_request(query, {'teamKey': team_identifier})
            team = data.get('team')
            
            if team:
                return team['id']
            else:
                # Fallback: get first team
                teams_query = '''
                query {
                    teams(first: 1) {
                        nodes {
                            id
                            name
                            key
                        }
                    }
                }
                '''
                data = self._make_graphql_request(teams_query)
                teams = data.get('teams', {}).get('nodes', [])
                if teams:
                    return teams[0]['id']
                
        except Exception as e:
            logger.error(f"Failed to get team ID: {e}")
        
        return ''
    
    def generate_project_visualization_data(self) -> Dict[str, Any]:
        """Generate data structure for the visualization"""
        issues = self.list_issues()
        
        # Organize issues by type and hierarchy
        milestones = []
        epics = []
        sub_issues = []
        
        for issue in issues:
            # Categorize by identifier pattern or labels
            if 'milestone' in issue.labels or issue.identifier.startswith('M'):
                milestones.append(issue)
            elif 'epic' in issue.labels or issue.identifier.startswith('E'):
                epics.append(issue)
            else:
                sub_issues.append(issue)
        
        # Build visualization data structure
        visualization_data = {
            'project': {
                'id': self.project_id,
                'name': 'IDFWU - IDEA Framework Unified',
                'status': 'active',
                'last_updated': datetime.now().isoformat()
            },
            'nodes': [],
            'links': []
        }
        
        # Add nodes
        for milestone in milestones:
            visualization_data['nodes'].append({
                'id': milestone.identifier,
                'name': milestone.title,
                'type': 'milestone',
                'status': milestone.state.lower(),
                'progress': self._calculate_progress(milestone, issues),
                'linear_id': milestone.id,
                'description': milestone.description
            })
        
        for epic in epics:
            visualization_data['nodes'].append({
                'id': epic.identifier,
                'name': epic.title,
                'type': 'epic',
                'status': epic.state.lower(),
                'progress': self._calculate_progress(epic, issues),
                'parent': self._find_parent_identifier(epic, milestones),
                'linear_id': epic.id,
                'description': epic.description
            })
        
        for issue in sub_issues:
            visualization_data['nodes'].append({
                'id': issue.identifier,
                'name': issue.title,
                'type': 'issue',
                'status': issue.state.lower(),
                'progress': 100 if issue.state.lower() == 'done' else 50 if issue.state.lower() == 'in progress' else 0,
                'parent': self._find_parent_identifier(issue, epics),
                'linear_id': issue.id,
                'description': issue.description
            })
        
        # Add hierarchy links
        for node in visualization_data['nodes']:
            if 'parent' in node and node['parent']:
                visualization_data['links'].append({
                    'source': node['parent'],
                    'target': node['id'],
                    'type': 'hierarchy'
                })
        
        return visualization_data
    
    def _calculate_progress(self, parent_issue: LinearIssue, all_issues: List[LinearIssue]) -> float:
        """Calculate progress based on child issues"""
        child_issues = [issue for issue in all_issues if issue.parent_id == parent_issue.id]
        
        if not child_issues:
            # No children, use state-based progress
            state = parent_issue.state.lower()
            if state == 'done':
                return 100.0
            elif state == 'in progress':
                return 50.0
            else:
                return 0.0
        
        # Calculate based on children
        total_children = len(child_issues)
        completed_children = len([issue for issue in child_issues if issue.state.lower() == 'done'])
        in_progress_children = len([issue for issue in child_issues if issue.state.lower() == 'in progress'])
        
        return (completed_children * 100 + in_progress_children * 50) / total_children
    
    def _find_parent_identifier(self, issue: LinearIssue, potential_parents: List[LinearIssue]) -> Optional[str]:
        """Find parent identifier based on parent_id"""
        if not issue.parent_id:
            return None
        
        for parent in potential_parents:
            if parent.id == issue.parent_id:
                return parent.identifier
        
        return None

def main():
    """Main function for testing Linear integration"""
    try:
        # Initialize Linear integration
        linear = LinearIntegration()
        
        # Test connection
        print("Testing Linear API connection...")
        if linear.test_connection():
            print("✅ Connection successful!")
        else:
            print("❌ Connection failed!")
            return
        
        # Get project information
        print(f"\nGetting project information for: {linear.project_id}")
        project_info = linear.get_project_info()
        if project_info:
            print(f"Project: {project_info.get('name', 'Unknown')}")
            print(f"State: {project_info.get('state', 'Unknown')}")
            print(f"Progress: {project_info.get('progress', 0)}%")
        
        # List issues
        print("\nListing project issues...")
        issues = linear.list_issues()
        print(f"Found {len(issues)} issues:")
        
        for issue in issues[:5]:  # Show first 5 issues
            print(f"  {issue.identifier}: {issue.title} ({issue.state})")
        
        # Generate visualization data
        print("\nGenerating visualization data...")
        viz_data = linear.generate_project_visualization_data()
        print(f"Generated data for {len(viz_data['nodes'])} nodes and {len(viz_data['links'])} links")
        
        # Save visualization data
        output_file = str(Path(__file__).parent.parent / 'docs' / 'project_data.json')
        with open(output_file, 'w') as f:
            json.dump(viz_data, f, indent=2)
        print(f"Visualization data saved to: {output_file}")
        
        print("\n✅ Linear integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()