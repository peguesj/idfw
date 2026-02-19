"""
Converters module for processing tool results from different sources.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from .core import HookContext


class LinearConverter:
    """Converter for Linear tool results."""
    
    def __init__(self):
        self.tool_mappings = {
            'create_issue': self._process_create_issue,
            'get_issue': self._process_get_issue,
            'update_issue': self._process_update_issue,
            'create_comment': self._process_create_comment,
            'list_issues': self._process_list_issues,
        }
    
    def process_tool_result(self, context: HookContext) -> Dict[str, Any]:
        """Process a Linear tool result."""
        
        tool_name = context.metadata.get('tool_name', '')
        
        # Find appropriate processor
        for key, processor in self.tool_mappings.items():
            if key in tool_name:
                return processor(context)
        
        # Default processing
        return self._process_generic(context)
    
    def _process_create_issue(self, context: HookContext) -> Dict[str, Any]:
        """Process create_issue tool result."""
        
        tool_result = context.metadata.get('tool_result', {})
        tool_args = context.metadata.get('tool_args', {})
        
        return {
            'action': 'create_issue',
            'issue_title': tool_args.get('title', 'Unknown'),
            'issue_id': tool_result.get('id'),
            'success': tool_result.get('success', False),
            'timestamp': datetime.now().isoformat()
        }
    
    def _process_get_issue(self, context: HookContext) -> Dict[str, Any]:
        """Process get_issue tool result."""
        
        tool_result = context.metadata.get('tool_result', {})
        tool_args = context.metadata.get('tool_args', {})
        
        return {
            'action': 'get_issue',
            'issue_id': tool_args.get('id'),
            'issue_data': tool_result,
            'success': bool(tool_result),
            'timestamp': datetime.now().isoformat()
        }
    
    def _process_update_issue(self, context: HookContext) -> Dict[str, Any]:
        """Process update_issue tool result."""
        
        tool_result = context.metadata.get('tool_result', {})
        tool_args = context.metadata.get('tool_args', {})
        
        return {
            'action': 'update_issue',
            'issue_id': tool_args.get('id'),
            'updates': tool_args,
            'success': tool_result.get('success', False),
            'timestamp': datetime.now().isoformat()
        }
    
    def _process_create_comment(self, context: HookContext) -> Dict[str, Any]:
        """Process create_comment tool result."""
        
        tool_result = context.metadata.get('tool_result', {})
        tool_args = context.metadata.get('tool_args', {})
        
        return {
            'action': 'create_comment',
            'issue_id': tool_args.get('issueId'),
            'comment_id': tool_result.get('id'),
            'success': tool_result.get('success', False),
            'timestamp': datetime.now().isoformat()
        }
    
    def _process_list_issues(self, context: HookContext) -> Dict[str, Any]:
        """Process list_issues tool result."""
        
        tool_result = context.metadata.get('tool_result', {})
        
        issues = tool_result.get('issues', [])
        
        return {
            'action': 'list_issues',
            'issue_count': len(issues),
            'issues': issues,
            'success': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def _process_generic(self, context: HookContext) -> Dict[str, Any]:
        """Process generic Linear tool result."""
        
        tool_name = context.metadata.get('tool_name', '')
        tool_result = context.metadata.get('tool_result', {})
        
        return {
            'action': 'generic_linear',
            'tool_name': tool_name,
            'success': tool_result.get('success', True),
            'timestamp': datetime.now().isoformat()
        }