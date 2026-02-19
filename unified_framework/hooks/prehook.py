"""
Prehook message processor with sentiment analysis and accuracy metrics.
"""

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from .core import HookContext, MessageScope


class SentimentCategory(Enum):
    """8-category sentiment classification."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    URGENT = "urgent"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    CONFUSED = "confused"
    SATISFIED = "satisfied"


@dataclass
class SentimentAnalysis:
    """Sentiment analysis results."""
    primary_sentiment: SentimentCategory
    confidence: float
    secondary_sentiments: List[Tuple[SentimentCategory, float]]
    emotional_indicators: List[str]
    urgency_score: float
    complexity_score: float


@dataclass
class AccuracyMetrics:
    """12-dimensional accuracy evaluation."""
    clarity: float
    completeness: float
    specificity: float
    actionability: float
    technical_accuracy: float
    contextual_relevance: float
    complexity_scoring: float
    urgency_detection: float
    dependency_identification: float
    success_correlation: float
    custom_metrics: Dict[str, float]
    iterative_improvement: float
    
    def overall_score(self) -> float:
        """Calculate overall accuracy score."""
        base_metrics = [
            self.clarity, self.completeness, self.specificity, 
            self.actionability, self.technical_accuracy, 
            self.contextual_relevance, self.complexity_scoring,
            self.urgency_detection, self.dependency_identification,
            self.success_correlation, self.iterative_improvement
        ]
        
        base_score = sum(base_metrics) / len(base_metrics)
        
        # Add custom metrics if any
        if self.custom_metrics:
            custom_score = sum(self.custom_metrics.values()) / len(self.custom_metrics)
            return (base_score + custom_score) / 2
        
        return base_score


@dataclass
class ProcessedMessage:
    """Fully processed message with all analysis."""
    message_id: str
    original_message: str
    processed_timestamp: datetime
    scope: MessageScope
    sentiment_analysis: SentimentAnalysis
    accuracy_metrics: AccuracyMetrics
    token_count: int
    chunks: List[str]
    referential_trail: Dict[str, str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        sentiment_dict = asdict(self.sentiment_analysis)
        # Convert enum values to strings
        sentiment_dict['primary_sentiment'] = sentiment_dict['primary_sentiment'].value
        sentiment_dict['secondary_sentiments'] = [
            (sentiment.value, score) for sentiment, score in self.sentiment_analysis.secondary_sentiments
        ]
        
        return {
            'message_id': self.message_id,
            'original_message': self.original_message,
            'processed_timestamp': self.processed_timestamp.isoformat(),
            'scope': self.scope.value,
            'sentiment_analysis': sentiment_dict,
            'accuracy_metrics': asdict(self.accuracy_metrics),
            'token_count': self.token_count,
            'chunks': self.chunks,
            'referential_trail': self.referential_trail,
            'metadata': self.metadata
        }


class SentimentAnalyzer:
    """Sentiment analysis component."""
    
    def __init__(self):
        # Keyword patterns for sentiment detection
        self.sentiment_patterns = {
            SentimentCategory.URGENT: [
                r'\b(urgent|emergency|critical|asap|immediately|now|quick)\b',
                r'\b(can\'t wait|time sensitive|deadline|rush)\b',
                r'!{2,}',  # Multiple exclamation marks
            ],
            SentimentCategory.FRUSTRATED: [
                r'\b(frustrated|annoyed|stuck|broken|failing|error)\b',
                r'\b(doesn\'t work|not working|problem|issue|bug)\b',
                r'\b(why|what\'s wrong|help)\b',
            ],
            SentimentCategory.EXCITED: [
                r'\b(excited|great|awesome|amazing|perfect|love)\b',
                r'\b(can\'t wait|looking forward|fantastic)\b',
                r'!+$',  # Exclamation at end
            ],
            SentimentCategory.CONFUSED: [
                r'\b(confused|unclear|not sure|don\'t understand)\b',
                r'\b(how do|what does|where is|which|what\'s)\b',
                r'\?{2,}',  # Multiple question marks
            ],
            SentimentCategory.SATISFIED: [
                r'\b(thanks|thank you|perfect|good|nice|appreciate)\b',
                r'\b(works|working|solved|fixed|done)\b',
            ],
            SentimentCategory.POSITIVE: [
                r'\b(good|great|nice|excellent|wonderful|please)\b',
                r'\b(yes|sure|absolutely|definitely)\b',
            ],
            SentimentCategory.NEGATIVE: [
                r'\b(no|not|don\'t|can\'t|won\'t|bad|terrible)\b',
                r'\b(remove|delete|stop|cancel|disable)\b',
            ]
        }
        
        # Complexity indicators
        self.complexity_indicators = [
            r'\b(integrate|complex|architecture|framework|system)\b',
            r'\b(multiple|several|various|different|across)\b',
            r'\b(database|API|authentication|deployment|testing)\b',
            r'\b(concurrent|parallel|async|sync|state)\b',
        ]
        
        # Urgency indicators
        self.urgency_indicators = [
            r'\b(urgent|emergency|critical|asap|immediately)\b',
            r'\b(deadline|due|time|quick|fast|now)\b',
            r'!{2,}',
            r'\b(production|live|client|customer)\b',
        ]
    
    def analyze(self, message: str) -> SentimentAnalysis:
        """Analyze sentiment of message."""
        message_lower = message.lower()
        
        # Calculate sentiment scores
        sentiment_scores = {}
        for sentiment, patterns in self.sentiment_patterns.items():
            score = 0.0
            indicators = []
            
            for pattern in patterns:
                matches = re.findall(pattern, message_lower, re.IGNORECASE)
                if matches:
                    score += len(matches) * 0.3
                    indicators.extend(matches)
            
            sentiment_scores[sentiment] = min(score, 1.0)
        
        # Determine primary sentiment
        primary_sentiment = max(sentiment_scores.items(), key=lambda x: x[1])
        
        # If no clear sentiment, default to neutral
        if primary_sentiment[1] < 0.1:
            primary_sentiment = (SentimentCategory.NEUTRAL, 0.5)
        
        # Get secondary sentiments
        secondary_sentiments = [
            (sentiment, score) for sentiment, score in sentiment_scores.items()
            if sentiment != primary_sentiment[0] and score > 0.1
        ]
        secondary_sentiments.sort(key=lambda x: x[1], reverse=True)
        
        # Calculate urgency and complexity scores
        urgency_score = self._calculate_urgency(message_lower)
        complexity_score = self._calculate_complexity(message_lower)
        
        # Extract emotional indicators
        emotional_indicators = self._extract_emotional_indicators(message)
        
        return SentimentAnalysis(
            primary_sentiment=primary_sentiment[0],
            confidence=primary_sentiment[1],
            secondary_sentiments=secondary_sentiments[:3],  # Top 3
            emotional_indicators=emotional_indicators,
            urgency_score=urgency_score,
            complexity_score=complexity_score
        )
    
    def _calculate_urgency(self, message: str) -> float:
        """Calculate urgency score."""
        score = 0.0
        
        for pattern in self.urgency_indicators:
            matches = re.findall(pattern, message, re.IGNORECASE)
            score += len(matches) * 0.25
        
        return min(score, 1.0)
    
    def _calculate_complexity(self, message: str) -> float:
        """Calculate complexity score."""
        score = 0.0
        
        # Technical term density
        for pattern in self.complexity_indicators:
            matches = re.findall(pattern, message, re.IGNORECASE)
            score += len(matches) * 0.2
        
        # Message length factor
        word_count = len(message.split())
        if word_count > 100:
            score += 0.3
        elif word_count > 50:
            score += 0.2
        elif word_count > 20:
            score += 0.1
        
        # Multiple requests/questions
        question_marks = message.count('?')
        if question_marks > 2:
            score += 0.2
        
        return min(score, 1.0)
    
    def _extract_emotional_indicators(self, message: str) -> List[str]:
        """Extract emotional indicators from message."""
        indicators = []
        
        # Punctuation patterns
        if '!!' in message:
            indicators.append('high_excitement')
        if '??' in message:
            indicators.append('high_confusion')
        if message.count('!') > 2:
            indicators.append('multiple_exclamations')
        
        # Capitalization patterns
        caps_words = re.findall(r'\b[A-Z]{2,}\b', message)
        if caps_words:
            indicators.append('caps_emphasis')
        
        # Emotional expressions
        if re.search(r'\b(omg|wow|ugh|argh|hmm)\b', message, re.IGNORECASE):
            indicators.append('emotional_expression')
        
        return indicators


class AccuracyEvaluator:
    """Accuracy metrics evaluator."""
    
    def __init__(self):
        # Patterns for different accuracy dimensions
        self.clarity_patterns = {
            'clear': [r'\b(please|can you|I need|I want|implement|create|fix)\b'],
            'unclear': [r'\b(maybe|perhaps|kind of|sort of|I think)\b']
        }
        
        self.specificity_patterns = {
            'specific': [r'\b(in file|at line|function|class|component)\b'],
            'vague': [r'\b(something|anything|stuff|things|it)\b']
        }
        
        self.actionability_patterns = {
            'actionable': [r'\b(create|implement|fix|update|add|remove|delete)\b'],
            'non_actionable': [r'\b(think about|consider|maybe|might)\b']
        }
    
    def evaluate(self, message: str, context: HookContext) -> AccuracyMetrics:
        """Evaluate message accuracy across 12 dimensions."""
        
        clarity = self._evaluate_clarity(message)
        completeness = self._evaluate_completeness(message, context)
        specificity = self._evaluate_specificity(message)
        actionability = self._evaluate_actionability(message)
        technical_accuracy = self._evaluate_technical_accuracy(message)
        contextual_relevance = self._evaluate_contextual_relevance(message, context)
        complexity_scoring = self._evaluate_complexity_scoring(message)
        urgency_detection = self._evaluate_urgency_detection(message)
        dependency_identification = self._evaluate_dependency_identification(message)
        success_correlation = self._evaluate_success_correlation(message, context)
        iterative_improvement = self._evaluate_iterative_improvement(message, context)
        
        # Custom metrics (extensible)
        custom_metrics = self._evaluate_custom_metrics(message, context)
        
        return AccuracyMetrics(
            clarity=clarity,
            completeness=completeness,
            specificity=specificity,
            actionability=actionability,
            technical_accuracy=technical_accuracy,
            contextual_relevance=contextual_relevance,
            complexity_scoring=complexity_scoring,
            urgency_detection=urgency_detection,
            dependency_identification=dependency_identification,
            success_correlation=success_correlation,
            custom_metrics=custom_metrics,
            iterative_improvement=iterative_improvement
        )
    
    def _evaluate_clarity(self, message: str) -> float:
        """Evaluate message clarity."""
        score = 0.5  # Base score
        
        # Clear indicators boost score
        for pattern in self.clarity_patterns['clear']:
            if re.search(pattern, message, re.IGNORECASE):
                score += 0.1
        
        # Unclear indicators reduce score
        for pattern in self.clarity_patterns['unclear']:
            if re.search(pattern, message, re.IGNORECASE):
                score -= 0.1
        
        # Grammar and structure
        sentences = message.split('.')
        if len(sentences) > 1:  # Multiple sentences
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _evaluate_completeness(self, message: str, context: HookContext) -> float:
        """Evaluate message completeness."""
        score = 0.3  # Base score
        
        # Check for essential elements
        word_count = len(message.split())
        if word_count > 10:
            score += 0.2
        if word_count > 30:
            score += 0.2
        
        # Context information
        if context.metadata:
            score += 0.1
        
        # Technical details
        if re.search(r'\b(file|function|error|code|implementation)\b', message, re.IGNORECASE):
            score += 0.2
        
        return min(1.0, score)
    
    def _evaluate_specificity(self, message: str) -> float:
        """Evaluate message specificity."""
        score = 0.4  # Base score
        
        # Specific indicators
        for pattern in self.specificity_patterns['specific']:
            if re.search(pattern, message, re.IGNORECASE):
                score += 0.15
        
        # Vague indicators
        for pattern in self.specificity_patterns['vague']:
            if re.search(pattern, message, re.IGNORECASE):
                score -= 0.1
        
        # Specific file paths, numbers, names
        if re.search(r'[/\\][a-zA-Z_][a-zA-Z0-9_/\\]*\.[a-zA-Z]+', message):
            score += 0.2  # File paths
        
        if re.search(r'\b\d+\b', message):
            score += 0.1  # Numbers
        
        return max(0.0, min(1.0, score))
    
    def _evaluate_actionability(self, message: str) -> float:
        """Evaluate message actionability."""
        score = 0.3  # Base score
        
        # Actionable verbs
        for pattern in self.actionability_patterns['actionable']:
            if re.search(pattern, message, re.IGNORECASE):
                score += 0.15
        
        # Non-actionable patterns
        for pattern in self.actionability_patterns['non_actionable']:
            if re.search(pattern, message, re.IGNORECASE):
                score -= 0.1
        
        # Imperative mood
        if message.strip().startswith(('Create', 'Implement', 'Fix', 'Update', 'Add', 'Remove')):
            score += 0.2
        
        return max(0.0, min(1.0, score))
    
    def _evaluate_technical_accuracy(self, message: str) -> float:
        """Evaluate technical accuracy."""
        # This would ideally use a more sophisticated model
        # For now, basic pattern matching
        technical_terms = [
            'API', 'database', 'function', 'class', 'component',
            'authentication', 'authorization', 'deployment', 'testing',
            'framework', 'library', 'repository', 'branch', 'commit'
        ]
        
        score = 0.5  # Neutral base
        for term in technical_terms:
            if term.lower() in message.lower():
                score += 0.05
        
        return min(1.0, score)
    
    def _evaluate_contextual_relevance(self, message: str, context: HookContext) -> float:
        """Evaluate contextual relevance."""
        score = 0.5  # Base score
        
        # Project-specific terms
        if context.project_id and 'idfwu' in message.lower():
            score += 0.2
        
        # Scope relevance
        if context.scope == MessageScope.AGENT and 'agent' in message.lower():
            score += 0.1
        elif context.scope == MessageScope.TASK and any(word in message.lower() for word in ['task', 'todo', 'implement']):
            score += 0.1
        
        return min(1.0, score)
    
    def _evaluate_complexity_scoring(self, message: str) -> float:
        """Evaluate complexity scoring accuracy."""
        # Assess if the message complexity is well-understood
        complexity_indicators = len(re.findall(r'\b(complex|integrate|system|multiple)\b', message, re.IGNORECASE))
        
        if complexity_indicators > 3:
            return 0.8  # High complexity well identified
        elif complexity_indicators > 1:
            return 0.6  # Medium complexity
        else:
            return 0.4  # Low complexity
    
    def _evaluate_urgency_detection(self, message: str) -> float:
        """Evaluate urgency detection accuracy."""
        urgency_words = ['urgent', 'emergency', 'asap', 'immediately', 'critical']
        urgency_count = sum(1 for word in urgency_words if word in message.lower())
        
        if urgency_count > 0:
            return min(1.0, 0.6 + urgency_count * 0.2)
        return 0.3  # No urgency detected
    
    def _evaluate_dependency_identification(self, message: str) -> float:
        """Evaluate dependency identification."""
        dependency_words = ['depends', 'requires', 'needs', 'after', 'before', 'integration']
        dependency_count = sum(1 for word in dependency_words if word in message.lower())
        
        return min(1.0, 0.4 + dependency_count * 0.2)
    
    def _evaluate_success_correlation(self, message: str, context: HookContext) -> float:
        """Evaluate success correlation (would use historical data)."""
        # This would correlate with past success rates
        # For now, basic heuristic
        if context.scope in [MessageScope.TASK, MessageScope.PROJECT]:
            return 0.7
        return 0.5
    
    def _evaluate_iterative_improvement(self, message: str, context: HookContext) -> float:
        """Evaluate iterative improvement potential."""
        improvement_words = ['improve', 'optimize', 'refactor', 'enhance', 'better']
        improvement_count = sum(1 for word in improvement_words if word in message.lower())
        
        return min(1.0, 0.3 + improvement_count * 0.2)
    
    def _evaluate_custom_metrics(self, message: str, context: HookContext) -> Dict[str, float]:
        """Evaluate custom extensible metrics."""
        return {
            'code_quality_focus': self._evaluate_code_quality_focus(message),
            'user_experience_focus': self._evaluate_ux_focus(message),
            'security_awareness': self._evaluate_security_awareness(message)
        }
    
    def _evaluate_code_quality_focus(self, message: str) -> float:
        """Evaluate focus on code quality."""
        quality_terms = ['test', 'coverage', 'lint', 'clean', 'refactor', 'best practices']
        return min(1.0, sum(0.15 for term in quality_terms if term in message.lower()))
    
    def _evaluate_ux_focus(self, message: str) -> float:
        """Evaluate focus on user experience."""
        ux_terms = ['user', 'interface', 'experience', 'usability', 'accessibility']
        return min(1.0, sum(0.2 for term in ux_terms if term in message.lower()))
    
    def _evaluate_security_awareness(self, message: str) -> float:
        """Evaluate security awareness."""
        security_terms = ['security', 'auth', 'permission', 'encrypt', 'validate']
        return min(1.0, sum(0.2 for term in security_terms if term in message.lower()))


class TokenManager:
    """Token management with chunking, caching, and batching."""
    
    def __init__(self, max_chunk_size: int = 1000):
        self.max_chunk_size = max_chunk_size
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def chunk_message(self, message: str, overlap: int = 100) -> List[str]:
        """Chunk message with overlap for context preservation."""
        if len(message) <= self.max_chunk_size:
            return [message]
        
        chunks = []
        start = 0
        
        while start < len(message):
            end = start + self.max_chunk_size
            
            if end >= len(message):
                chunks.append(message[start:])
                break
            
            # Try to break at sentence or word boundary
            chunk_text = message[start:end]
            
            # Find last sentence break
            last_period = chunk_text.rfind('.')
            last_newline = chunk_text.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > start + self.max_chunk_size // 2:
                end = start + break_point + 1
            else:
                # Find last word break
                last_space = chunk_text.rfind(' ')
                if last_space > start + self.max_chunk_size // 2:
                    end = start + last_space
            
            chunks.append(message[start:end])
            start = end - overlap  # Overlap for context
        
        return chunks


class PrehookProcessor:
    """Main prehook processor coordinating all components."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / '.claude' / 'hooks' / 'messages'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.sentiment_analyzer = SentimentAnalyzer()
        self.accuracy_evaluator = AccuracyEvaluator()
        self.token_manager = TokenManager()
        
        # Load processing history for pattern learning
        self.processing_history: List[ProcessedMessage] = []
        self._load_history()
    
    async def process_message(self, context: HookContext) -> ProcessedMessage:
        """Process a message through all analysis components."""
        
        message = context.message
        message_id = str(uuid.uuid4())
        
        # Sentiment analysis
        sentiment_analysis = self.sentiment_analyzer.analyze(message)
        
        # Accuracy evaluation
        accuracy_metrics = self.accuracy_evaluator.evaluate(message, context)
        
        # Token management
        token_count = self.token_manager.count_tokens(message)
        chunks = self.token_manager.chunk_message(message)
        
        # Create referential trail
        referential_trail = self._create_referential_trail(context)
        
        # Create processed message
        processed_message = ProcessedMessage(
            message_id=message_id,
            original_message=message,
            processed_timestamp=datetime.now(),
            scope=context.scope,
            sentiment_analysis=sentiment_analysis,
            accuracy_metrics=accuracy_metrics,
            token_count=token_count,
            chunks=chunks,
            referential_trail=referential_trail,
            metadata=context.metadata
        )
        
        # Store processed message
        await self._store_processed_message(processed_message)
        
        # Add to history for learning
        self.processing_history.append(processed_message)
        
        return processed_message
    
    def _create_referential_trail(self, context: HookContext) -> Dict[str, str]:
        """Create referential trail across scopes."""
        trail = {
            'message_scope': context.scope.value,
            'timestamp': context.timestamp.isoformat()
        }
        
        if context.task_id:
            trail['task_id'] = context.task_id
        if context.thread_id:
            trail['thread_id'] = context.thread_id
        if context.project_id:
            trail['project_id'] = context.project_id
        if context.user_id:
            trail['user_id'] = context.user_id
        
        return trail
    
    async def _store_processed_message(self, processed_message: ProcessedMessage):
        """Store processed message to disk."""
        timestamp = processed_message.processed_timestamp
        date_str = timestamp.strftime('%Y-%m-%d')
        
        # Create daily storage file
        daily_file = self.storage_path / f'messages_{date_str}.jsonl'
        
        # Append to file
        with open(daily_file, 'a') as f:
            f.write(json.dumps(processed_message.to_dict()) + '\n')
    
    def _load_history(self, days: int = 7):
        """Load recent processing history for pattern learning."""
        # Load last N days of processed messages
        # This would be implemented for pattern learning
        pass
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        if not self.processing_history:
            return {'total_processed': 0}
        
        total = len(self.processing_history)
        
        # Sentiment distribution
        sentiment_counts = {}
        for msg in self.processing_history:
            sentiment = msg.sentiment_analysis.primary_sentiment.value
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        # Average accuracy scores
        avg_accuracy = sum(msg.accuracy_metrics.overall_score() for msg in self.processing_history) / total
        
        # Scope distribution
        scope_counts = {}
        for msg in self.processing_history:
            scope = msg.scope.value
            scope_counts[scope] = scope_counts.get(scope, 0) + 1
        
        return {
            'total_processed': total,
            'sentiment_distribution': sentiment_counts,
            'average_accuracy_score': avg_accuracy,
            'scope_distribution': scope_counts,
            'average_token_count': sum(msg.token_count for msg in self.processing_history) / total
        }