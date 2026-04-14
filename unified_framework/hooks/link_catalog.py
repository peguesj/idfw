"""
PostToolUse hook for link cataloging and resource management.
"""

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from urllib.parse import urlparse, urljoin
import hashlib

from .core import HookContext


class LinkType(Enum):
    """Types of links that can be catalogued."""
    DOCUMENTATION = "documentation"
    API_REFERENCE = "api_reference"
    TUTORIAL = "tutorial"
    REPOSITORY = "repository"
    ISSUE_TRACKER = "issue_tracker"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    PACKAGE_REGISTRY = "package_registry"
    COMMUNITY = "community"
    TOOL = "tool"
    UNKNOWN = "unknown"


class LinkStatus(Enum):
    """Status of catalogued links."""
    ACTIVE = "active"
    DEAD = "dead"
    REDIRECT = "redirect"
    UNKNOWN = "unknown"
    PENDING_VERIFICATION = "pending_verification"


@dataclass
class LinkMetadata:
    """Metadata extracted from links."""
    title: Optional[str]
    description: Optional[str]
    author: Optional[str]
    publication_date: Optional[datetime]
    last_modified: Optional[datetime]
    content_type: Optional[str]
    language: Optional[str]
    keywords: List[str]
    estimated_reading_time: Optional[int]
    difficulty_level: Optional[str]


@dataclass
class DependencyInfo:
    """Dependency information for links."""
    framework_version: Optional[str]
    language_version: Optional[str]
    platform_requirements: List[str]
    dependency_packages: List[str]
    compatibility_notes: Optional[str]


@dataclass
class CataloguedLink:
    """Comprehensive link catalogue entry."""
    link_id: str
    url: str
    original_context: str
    discovered_at: datetime
    link_type: LinkType
    status: LinkStatus
    metadata: LinkMetadata
    dependencies: DependencyInfo
    categories: List[str]
    tags: List[str]
    confidence_score: float
    verification_history: List[Dict[str, Any]]
    related_links: List[str]
    usage_count: int
    last_accessed: Optional[datetime]
    notes: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'link_id': self.link_id,
            'url': self.url,
            'original_context': self.original_context,
            'discovered_at': self.discovered_at.isoformat(),
            'link_type': self.link_type.value,
            'status': self.status.value,
            'metadata': asdict(self.metadata),
            'dependencies': asdict(self.dependencies),
            'categories': self.categories,
            'tags': self.tags,
            'confidence_score': self.confidence_score,
            'verification_history': self.verification_history,
            'related_links': self.related_links,
            'usage_count': self.usage_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'notes': self.notes
        }


class LinkExtractor:
    """Extract and classify links from various content sources."""
    
    def __init__(self):
        # URL patterns for different link types
        self.url_patterns = {
            LinkType.DOCUMENTATION: [
                r'docs?\.',
                r'documentation',
                r'guide',
                r'manual',
                r'wiki',
                r'readme'
            ],
            LinkType.API_REFERENCE: [
                r'api\.',
                r'reference',
                r'swagger',
                r'openapi',
                r'postman'
            ],
            LinkType.REPOSITORY: [
                r'github\.com',
                r'gitlab\.com',
                r'bitbucket\.org',
                r'sourceforge\.net'
            ],
            LinkType.PACKAGE_REGISTRY: [
                r'npmjs\.com',
                r'pypi\.org',
                r'packagist\.org',
                r'rubygems\.org',
                r'nuget\.org'
            ],
            LinkType.DEPLOYMENT: [
                r'vercel\.app',
                r'netlify\.app',
                r'heroku\.com',
                r'aws\.amazon\.com',
                r'cloud\.google\.com',
                r'azure\.microsoft\.com'
            ],
            LinkType.MONITORING: [
                r'sentry\.io',
                r'datadog\.com',
                r'newrelic\.com',
                r'grafana\.com'
            ]
        }
        
        # Content patterns for link classification
        self.context_patterns = {
            LinkType.TUTORIAL: [
                'tutorial', 'walkthrough', 'step by step', 'how to', 'guide'
            ],
            LinkType.ISSUE_TRACKER: [
                'issue', 'bug', 'feature request', 'enhancement', 'problem'
            ],
            LinkType.COMMUNITY: [
                'forum', 'community', 'discussion', 'chat', 'discord', 'slack'
            ]
        }
    
    def extract_links(self, content: str, context: str = "") -> List[Tuple[str, str]]:
        """Extract all links from content with their surrounding context."""
        
        # Updated regex to be more permissive with URLs
        url_pattern = r'https?://[^\s<>"\'{}|\\^`\[\]]+[^\s<>"\'{}|\\^`\[\].,;:]'
        
        links = []
        for match in re.finditer(url_pattern, content):
            url = match.group(0)
            start = max(0, match.start() - 100)
            end = min(len(content), match.end() + 100)
            link_context = content[start:end].strip()
            
            links.append((url, link_context))
        
        return links
    
    def classify_link(self, url: str, context: str) -> Tuple[LinkType, float]:
        """Classify a link and return confidence score."""
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()
        full_url = url.lower()
        context_lower = context.lower()
        
        # Check URL patterns
        for link_type, patterns in self.url_patterns.items():
            for pattern in patterns:
                if re.search(pattern, domain) or re.search(pattern, path):
                    return link_type, 0.8
        
        # Check context patterns
        for link_type, patterns in self.context_patterns.items():
            for pattern in patterns:
                if pattern in context_lower:
                    return link_type, 0.6
        
        # Domain-specific classification
        if 'github.com' in domain:
            if '/issues/' in path:
                return LinkType.ISSUE_TRACKER, 0.9
            else:
                return LinkType.REPOSITORY, 0.9
        
        if 'stackoverflow.com' in domain:
            return LinkType.COMMUNITY, 0.8
        
        if any(doc_indicator in path for doc_indicator in ['doc', 'guide', 'manual']):
            return LinkType.DOCUMENTATION, 0.7
        
        return LinkType.UNKNOWN, 0.3


class MetadataExtractor:
    """Extract metadata from links and content."""
    
    def __init__(self):
        self.title_patterns = [
            r'<title[^>]*>([^<]+)</title>',
            r'# ([^\n]+)',
            r'## ([^\n]+)'
        ]
        
        self.description_patterns = [
            r'<meta name="description" content="([^"]+)"',
            r'<meta property="og:description" content="([^"]+)"'
        ]
    
    def extract_metadata(self, url: str, context: str, content: str = "") -> LinkMetadata:
        """Extract metadata from URL, context, and content."""
        
        # Extract title
        title = self._extract_title(url, context, content)
        
        # Extract description
        description = self._extract_description(context, content)
        
        # Extract keywords from context
        keywords = self._extract_keywords(context)
        
        # Estimate reading time
        reading_time = self._estimate_reading_time(content)
        
        # Determine content type
        content_type = self._determine_content_type(url, context)
        
        return LinkMetadata(
            title=title,
            description=description,
            author=None,  # Would require content fetching
            publication_date=None,  # Would require content parsing
            last_modified=None,  # Would require HTTP headers
            content_type=content_type,
            language=None,  # Would require content analysis
            keywords=keywords,
            estimated_reading_time=reading_time,
            difficulty_level=self._assess_difficulty(context)
        )
    
    def _extract_title(self, url: str, context: str, content: str) -> Optional[str]:
        """Extract title from various sources."""
        
        # Try to extract from HTML content
        if content:
            for pattern in self.title_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    return match.group(1).strip()
        
        # Extract from URL path
        parsed_url = urlparse(url)
        path_parts = [part for part in parsed_url.path.split('/') if part]
        if path_parts:
            # Clean up filename/path
            title = path_parts[-1].replace('-', ' ').replace('_', ' ')
            return title.title()
        
        # Use domain as fallback
        return parsed_url.netloc
    
    def _extract_description(self, context: str, content: str) -> Optional[str]:
        """Extract description from context or content."""
        
        # Try to extract from HTML meta tags
        if content:
            for pattern in self.description_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        # Use context as description if it's descriptive
        if len(context) > 50 and len(context) < 300:
            return context.strip()
        
        return None
    
    def _extract_keywords(self, context: str) -> List[str]:
        """Extract keywords from context."""
        
        # Technical keywords that are commonly relevant
        tech_keywords = [
            'api', 'documentation', 'tutorial', 'guide', 'framework',
            'library', 'package', 'tool', 'deployment', 'monitoring',
            'testing', 'security', 'performance', 'optimization',
            'database', 'authentication', 'authorization', 'integration'
        ]
        
        keywords = []
        context_lower = context.lower()
        
        for keyword in tech_keywords:
            if keyword in context_lower:
                keywords.append(keyword)
        
        # Extract quoted terms as keywords
        quoted_terms = re.findall(r'"([^"]+)"', context)
        keywords.extend(quoted_terms)
        
        # Extract capitalized terms (likely proper nouns/technologies)
        capitalized_terms = re.findall(r'\b[A-Z][a-zA-Z]+\b', context)
        keywords.extend(capitalized_terms)
        
        return list(set(keywords))  # Remove duplicates
    
    def _estimate_reading_time(self, content: str) -> Optional[int]:
        """Estimate reading time in minutes."""
        
        if not content:
            return None
        
        # Average reading speed: 200-250 words per minute
        word_count = len(content.split())
        reading_time = max(1, word_count // 225)  # Round up to at least 1 minute
        
        return reading_time
    
    def _determine_content_type(self, url: str, context: str) -> Optional[str]:
        """Determine the type of content."""
        
        if any(indicator in url.lower() for indicator in ['.pdf', 'pdf']):
            return 'PDF'
        
        if any(indicator in url.lower() for indicator in ['.md', 'markdown']):
            return 'Markdown'
        
        if any(indicator in context.lower() for indicator in ['video', 'youtube', 'vimeo']):
            return 'Video'
        
        if any(indicator in context.lower() for indicator in ['api', 'swagger', 'openapi']):
            return 'API Documentation'
        
        return 'Web Page'
    
    def _assess_difficulty(self, context: str) -> Optional[str]:
        """Assess the difficulty level of the content."""
        
        beginner_indicators = ['beginner', 'intro', 'getting started', 'basics', 'simple']
        intermediate_indicators = ['intermediate', 'advanced guide', 'deep dive']
        advanced_indicators = ['advanced', 'expert', 'complex', 'sophisticated']
        
        context_lower = context.lower()
        
        if any(indicator in context_lower for indicator in advanced_indicators):
            return 'Advanced'
        elif any(indicator in context_lower for indicator in intermediate_indicators):
            return 'Intermediate'
        elif any(indicator in context_lower for indicator in beginner_indicators):
            return 'Beginner'
        
        return None


class DependencyAnalyzer:
    """Analyze dependencies and requirements from links."""
    
    def __init__(self):
        self.version_patterns = {
            'node': r'node[^\w]*(v?\d+\.\d+\.\d+)',
            'npm': r'npm[^\w]*(v?\d+\.\d+\.\d+)',
            'python': r'python[^\w]*(v?\d+\.\d+\.?\d*)',
            'react': r'react[^\w]*(v?\d+\.\d+\.\d+)',
            'next': r'next\.js[^\w]*(v?\d+\.\d+\.\d+)',
            'typescript': r'typescript[^\w]*(v?\d+\.\d+\.\d+)'
        }
        
        self.platform_indicators = {
            'windows': ['windows', 'win32', 'win64'],
            'macos': ['macos', 'darwin', 'osx', 'mac'],
            'linux': ['linux', 'ubuntu', 'debian', 'centos'],
            'docker': ['docker', 'container', 'dockerfile'],
            'web': ['browser', 'web', 'client-side'],
            'mobile': ['mobile', 'ios', 'android', 'react native']
        }
    
    def analyze_dependencies(self, url: str, context: str) -> DependencyInfo:
        """Analyze dependencies from URL and context."""
        
        # Extract version information
        framework_version = self._extract_framework_version(context)
        language_version = self._extract_language_version(context)
        
        # Identify platform requirements
        platform_requirements = self._identify_platforms(context)
        
        # Extract package dependencies
        dependency_packages = self._extract_packages(context)
        
        # Generate compatibility notes
        compatibility_notes = self._generate_compatibility_notes(url, context)
        
        return DependencyInfo(
            framework_version=framework_version,
            language_version=language_version,
            platform_requirements=platform_requirements,
            dependency_packages=dependency_packages,
            compatibility_notes=compatibility_notes
        )
    
    def _extract_framework_version(self, context: str) -> Optional[str]:
        """Extract framework version information."""
        
        for framework, pattern in self.version_patterns.items():
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return f"{framework} {match.group(1)}"
        
        return None
    
    def _extract_language_version(self, context: str) -> Optional[str]:
        """Extract language version information."""
        
        language_patterns = ['python', 'node', 'typescript', 'javascript']
        
        for lang in language_patterns:
            pattern = self.version_patterns.get(lang)
            if pattern:
                match = re.search(pattern, context, re.IGNORECASE)
                if match:
                    return f"{lang} {match.group(1)}"
        
        return None
    
    def _identify_platforms(self, context: str) -> List[str]:
        """Identify platform requirements."""
        
        platforms = []
        context_lower = context.lower()
        
        for platform, indicators in self.platform_indicators.items():
            if any(indicator in context_lower for indicator in indicators):
                platforms.append(platform)
        
        return platforms
    
    def _extract_packages(self, context: str) -> List[str]:
        """Extract package dependencies."""
        
        packages = []
        
        # Look for npm packages
        npm_pattern = r'npm install ([a-zA-Z0-9@\-_/]+)'
        npm_matches = re.findall(npm_pattern, context)
        packages.extend(npm_matches)
        
        # Look for pip packages
        pip_pattern = r'pip install ([a-zA-Z0-9\-_]+)'
        pip_matches = re.findall(pip_pattern, context)
        packages.extend(pip_matches)
        
        # Look for package.json references
        if 'package.json' in context:
            packages.append('package.json dependencies')
        
        # Look for requirements.txt references
        if 'requirements.txt' in context:
            packages.append('requirements.txt dependencies')
        
        return packages
    
    def _generate_compatibility_notes(self, url: str, context: str) -> Optional[str]:
        """Generate compatibility notes."""
        
        notes = []
        
        # Version-specific notes
        if 'deprecated' in context.lower():
            notes.append("This resource may contain deprecated information")
        
        if 'beta' in context.lower() or 'alpha' in context.lower():
            notes.append("This resource refers to pre-release software")
        
        if 'legacy' in context.lower():
            notes.append("This resource may be for legacy systems")
        
        # Framework-specific notes
        if 'react' in context.lower() and 'class component' in context.lower():
            notes.append("May use older React class component patterns")
        
        if 'javascript' in context.lower() and 'var ' in context:
            notes.append("May use older JavaScript syntax")
        
        return '; '.join(notes) if notes else None


class LinkCatalogHook:
    """Main link cataloguing hook for PostToolUse events."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / '.claude' / 'hooks' / 'links'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.extractor = LinkExtractor()
        self.metadata_extractor = MetadataExtractor()
        self.dependency_analyzer = DependencyAnalyzer()
        
        # Link database
        self.link_database: Dict[str, CataloguedLink] = {}
        self.url_to_id: Dict[str, str] = {}
        
        # Load existing links
        self._load_existing_links()
        
        # Dead link cleanup agent queue
        self.dead_link_queue: List[str] = []
    
    async def process_tool_use(self, context: HookContext) -> Dict[str, Any]:
        """Process tool use to extract and catalogue links."""
        
        # Extract content from tool result
        content = str(context.metadata.get('tool_result', ''))
        prompt_body = context.message
        
        # Extract links from both prompt and result
        prompt_links = self.extractor.extract_links(prompt_body, "user prompt")
        result_links = self.extractor.extract_links(content, "tool result")
        
        all_links = prompt_links + result_links
        
        catalogued_links = []
        new_links = 0
        updated_links = 0
        
        for url, link_context in all_links:
            link_info = await self._process_single_link(url, link_context, context)
            if link_info:
                catalogued_links.append(link_info)
                if link_info['is_new']:
                    new_links += 1
                else:
                    updated_links += 1
        
        # Save updated database
        await self._save_link_database()
        
        return {
            'total_links_found': len(all_links),
            'catalogued_links': len(catalogued_links),
            'new_links': new_links,
            'updated_links': updated_links,
            'dead_links_queued': len(self.dead_link_queue),
            'link_details': catalogued_links
        }
    
    async def _process_single_link(
        self,
        url: str,
        link_context: str,
        context: HookContext
    ) -> Optional[Dict[str, Any]]:
        """Process a single link for cataloguing."""
        
        # Check if link already exists
        url_hash = hashlib.md5(url.encode()).hexdigest()
        existing_id = self.url_to_id.get(url_hash)
        
        is_new = existing_id is None
        
        if existing_id:
            # Update existing link
            existing_link = self.link_database[existing_id]
            existing_link.usage_count += 1
            existing_link.last_accessed = datetime.now()
            
            # Update context if more detailed
            if len(link_context) > len(existing_link.original_context):
                existing_link.original_context = link_context
            
            return {
                'link_id': existing_id,
                'url': url,
                'status': 'updated',
                'is_new': False,
                'usage_count': existing_link.usage_count
            }
        
        # Create new link entry
        link_id = str(uuid.uuid4())
        
        # Classify link
        link_type, confidence = self.extractor.classify_link(url, link_context)
        
        # Extract metadata
        metadata = self.metadata_extractor.extract_metadata(url, link_context)
        
        # Analyze dependencies
        dependencies = self.dependency_analyzer.analyze_dependencies(url, link_context)
        
        # Generate categories and tags
        categories = self._generate_categories(url, link_context, link_type)
        tags = self._generate_tags(url, link_context, metadata)
        
        # Create catalogued link
        catalogued_link = CataloguedLink(
            link_id=link_id,
            url=url,
            original_context=link_context,
            discovered_at=datetime.now(),
            link_type=link_type,
            status=LinkStatus.PENDING_VERIFICATION,
            metadata=metadata,
            dependencies=dependencies,
            categories=categories,
            tags=tags,
            confidence_score=confidence,
            verification_history=[],
            related_links=[],
            usage_count=1,
            last_accessed=datetime.now(),
            notes=None
        )
        
        # Store in database
        self.link_database[link_id] = catalogued_link
        self.url_to_id[url_hash] = link_id
        
        # Queue for verification if needed
        if confidence < 0.5:
            self.dead_link_queue.append(link_id)
        
        return {
            'link_id': link_id,
            'url': url,
            'status': 'new',
            'is_new': True,
            'link_type': link_type.value,
            'confidence': confidence,
            'categories': categories,
            'tags': tags
        }
    
    def _generate_categories(self, url: str, context: str, link_type: LinkType) -> List[str]:
        """Generate categories for the link."""
        
        categories = [link_type.value]
        
        # Technology categories
        tech_categories = {
            'web_development': ['html', 'css', 'javascript', 'web', 'frontend', 'backend'],
            'mobile_development': ['mobile', 'ios', 'android', 'react native', 'flutter'],
            'devops': ['docker', 'kubernetes', 'ci/cd', 'deployment', 'infrastructure'],
            'testing': ['test', 'testing', 'qa', 'unit test', 'integration test'],
            'security': ['security', 'auth', 'authentication', 'encryption', 'vulnerability'],
            'performance': ['performance', 'optimization', 'speed', 'caching', 'benchmark']
        }
        
        context_lower = context.lower()
        url_lower = url.lower()
        
        for category, keywords in tech_categories.items():
            if any(keyword in context_lower or keyword in url_lower for keyword in keywords):
                categories.append(category)
        
        # Framework-specific categories
        frameworks = ['react', 'vue', 'angular', 'next.js', 'nuxt', 'svelte']
        for framework in frameworks:
            if framework in context_lower or framework in url_lower:
                categories.append(f"framework_{framework.replace('.', '_')}")
        
        return categories
    
    def _generate_tags(self, url: str, context: str, metadata: LinkMetadata) -> List[str]:
        """Generate tags for the link."""
        
        tags = []
        
        # Add keywords as tags
        if metadata.keywords:
            tags.extend(metadata.keywords)
        
        # Add difficulty as tag
        if metadata.difficulty_level:
            tags.append(metadata.difficulty_level.lower())
        
        # Add content type as tag
        if metadata.content_type:
            tags.append(metadata.content_type.lower().replace(' ', '_'))
        
        # Domain-based tags
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        if 'github.com' in domain:
            tags.append('github')
        elif 'stackoverflow.com' in domain:
            tags.append('stackoverflow')
        elif 'medium.com' in domain:
            tags.append('medium')
        elif 'dev.to' in domain:
            tags.append('dev_to')
        
        # Remove duplicates and clean
        tags = list(set(tag.lower().replace(' ', '_') for tag in tags if tag))
        
        return tags
    
    async def _save_link_database(self):
        """Save link database to disk."""
        
        database_file = self.storage_path / 'link_database.json'
        
        # Convert to serializable format
        serializable_db = {
            link_id: link.to_dict()
            for link_id, link in self.link_database.items()
        }
        
        with open(database_file, 'w') as f:
            json.dump({
                'links': serializable_db,
                'url_mapping': self.url_to_id,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
        
        # Save daily backup
        timestamp = datetime.now().strftime('%Y-%m-%d')
        backup_file = self.storage_path / f'backup_{timestamp}.json'
        
        with open(backup_file, 'w') as f:
            json.dump(serializable_db, f, indent=2)
    
    def _load_existing_links(self):
        """Load existing links from disk."""
        
        database_file = self.storage_path / 'link_database.json'
        
        if database_file.exists():
            try:
                with open(database_file) as f:
                    data = json.load(f)
                
                self.url_to_id = data.get('url_mapping', {})
                
                # Reconstruct link objects
                for link_id, link_data in data.get('links', {}).items():
                    # Convert string dates back to datetime
                    link_data['discovered_at'] = datetime.fromisoformat(link_data['discovered_at'])
                    if link_data['last_accessed']:
                        link_data['last_accessed'] = datetime.fromisoformat(link_data['last_accessed'])
                    
                    # Reconstruct enum values
                    link_data['link_type'] = LinkType(link_data['link_type'])
                    link_data['status'] = LinkStatus(link_data['status'])
                    
                    # Reconstruct nested objects
                    metadata_data = link_data['metadata']
                    if metadata_data.get('publication_date'):
                        metadata_data['publication_date'] = datetime.fromisoformat(metadata_data['publication_date'])
                    if metadata_data.get('last_modified'):
                        metadata_data['last_modified'] = datetime.fromisoformat(metadata_data['last_modified'])
                    
                    link_data['metadata'] = LinkMetadata(**metadata_data)
                    link_data['dependencies'] = DependencyInfo(**link_data['dependencies'])
                    
                    # Create link object
                    self.link_database[link_id] = CataloguedLink(**link_data)
                    
            except Exception as e:
                print(f"Warning: Could not load existing link database: {e}")
    
    def search_links(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        link_type: Optional[LinkType] = None
    ) -> List[CataloguedLink]:
        """Search catalogued links."""
        
        results = []
        query_lower = query.lower()
        
        for link in self.link_database.values():
            # Text search
            if query_lower in link.url.lower() or query_lower in link.original_context.lower():
                score = 1.0
            elif link.metadata.title and query_lower in link.metadata.title.lower():
                score = 0.8
            elif link.metadata.description and query_lower in link.metadata.description.lower():
                score = 0.6
            elif any(query_lower in tag.lower() for tag in link.tags):
                score = 0.5
            else:
                continue
            
            # Filter by categories
            if categories and not any(cat in link.categories for cat in categories):
                continue
            
            # Filter by tags
            if tags and not any(tag in link.tags for tag in tags):
                continue
            
            # Filter by type
            if link_type and link.link_type != link_type:
                continue
            
            results.append((link, score))
        
        # Sort by score and usage
        results.sort(key=lambda x: (x[1], x[0].usage_count), reverse=True)
        
        return [link for link, score in results]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cataloguing statistics."""
        
        if not self.link_database:
            return {'total_links': 0}
        
        total_links = len(self.link_database)
        
        # Type distribution
        type_counts = {}
        for link in self.link_database.values():
            link_type = link.link_type.value
            type_counts[link_type] = type_counts.get(link_type, 0) + 1
        
        # Status distribution
        status_counts = {}
        for link in self.link_database.values():
            status = link.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Top categories
        category_counts = {}
        for link in self.link_database.values():
            for category in link.categories:
                category_counts[category] = category_counts.get(category, 0) + 1
        
        # Most used links
        most_used = sorted(
            self.link_database.values(),
            key=lambda x: x.usage_count,
            reverse=True
        )[:5]
        
        return {
            'total_links': total_links,
            'type_distribution': type_counts,
            'status_distribution': status_counts,
            'top_categories': sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'most_used_links': [
                {'url': link.url, 'usage_count': link.usage_count, 'title': link.metadata.title}
                for link in most_used
            ],
            'dead_links_pending': len(self.dead_link_queue)
        }