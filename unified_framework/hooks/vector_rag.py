"""
Vectorization and RAG (Retrieval Augmented Generation) system for the hooks framework.
"""

import json
import math
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import hashlib
import numpy as np
from collections import defaultdict, Counter

from .core import HookContext


@dataclass
class SemanticChunk:
    """A semantic chunk of text with metadata."""
    chunk_id: str
    content: str
    source_id: str
    source_type: str  # message, link, document, etc.
    created_at: datetime
    chunk_index: int
    total_chunks: int
    overlap_with_previous: int
    overlap_with_next: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'chunk_id': self.chunk_id,
            'content': self.content,
            'source_id': self.source_id,
            'source_type': self.source_type,
            'created_at': self.created_at.isoformat(),
            'chunk_index': self.chunk_index,
            'total_chunks': self.total_chunks,
            'overlap_with_previous': self.overlap_with_previous,
            'overlap_with_next': self.overlap_with_next,
            'metadata': self.metadata
        }


@dataclass
class VectorEmbedding:
    """Vector embedding with metadata."""
    vector_id: str
    chunk_id: str
    embedding: List[float]
    embedding_model: str
    embedding_dimension: int
    created_at: datetime
    norm: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'vector_id': self.vector_id,
            'chunk_id': self.chunk_id,
            'embedding': self.embedding,
            'embedding_model': self.embedding_model,
            'embedding_dimension': self.embedding_dimension,
            'created_at': self.created_at.isoformat(),
            'norm': self.norm
        }


@dataclass
class SimilarityResult:
    """Result from similarity search."""
    chunk_id: str
    content: str
    similarity_score: float
    source_id: str
    source_type: str
    metadata: Dict[str, Any]
    rank: int


class SemanticChunker:
    """Intelligent content segmentation with overlap management."""
    
    def __init__(
        self,
        max_chunk_size: int = 1000,
        min_chunk_size: int = 100,
        overlap_size: int = 100,
        preserve_sentences: bool = True
    ):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.overlap_size = overlap_size
        self.preserve_sentences = preserve_sentences
        
        # Sentence boundary patterns
        self.sentence_endings = re.compile(r'[.!?]+\s+')
        self.paragraph_breaks = re.compile(r'\n\s*\n')
        
        # Semantic boundary indicators
        self.semantic_boundaries = [
            r'\n#{1,6}\s+',  # Markdown headers
            r'\n\*\s+',      # Bullet points
            r'\n\d+\.\s+',   # Numbered lists
            r'\n```',        # Code blocks
            r'\n---+',       # Horizontal rules
        ]
    
    def chunk_content(
        self,
        content: str,
        source_id: str,
        source_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[SemanticChunk]:
        """Chunk content into semantic segments."""
        
        if len(content) <= self.max_chunk_size:
            return [SemanticChunk(
                chunk_id=str(uuid.uuid4()),
                content=content,
                source_id=source_id,
                source_type=source_type,
                created_at=datetime.now(),
                chunk_index=0,
                total_chunks=1,
                overlap_with_previous=0,
                overlap_with_next=0,
                metadata=metadata or {}
            )]
        
        # Find optimal chunk boundaries
        boundaries = self._find_chunk_boundaries(content)
        
        chunks = []
        for i, (start, end) in enumerate(boundaries):
            chunk_content = content[start:end]
            
            # Calculate overlaps
            overlap_prev = 0
            overlap_next = 0
            
            if i > 0:
                prev_end = boundaries[i-1][1]
                overlap_prev = max(0, prev_end - start)
            
            if i < len(boundaries) - 1:
                next_start = boundaries[i+1][0]
                overlap_next = max(0, end - next_start)
            
            chunk = SemanticChunk(
                chunk_id=str(uuid.uuid4()),
                content=chunk_content,
                source_id=source_id,
                source_type=source_type,
                created_at=datetime.now(),
                chunk_index=i,
                total_chunks=len(boundaries),
                overlap_with_previous=overlap_prev,
                overlap_with_next=overlap_next,
                metadata=metadata or {}
            )
            
            chunks.append(chunk)
        
        return chunks
    
    def _find_chunk_boundaries(self, content: str) -> List[Tuple[int, int]]:
        """Find optimal chunk boundaries preserving semantic structure."""
        
        boundaries = []
        current_start = 0
        
        while current_start < len(content):
            # Find the best end position for this chunk
            target_end = current_start + self.max_chunk_size
            
            if target_end >= len(content):
                # Last chunk
                boundaries.append((current_start, len(content)))
                break
            
            # Find the best boundary near the target end
            best_boundary = self._find_best_boundary(
                content, current_start, target_end
            )
            
            boundaries.append((current_start, best_boundary))
            
            # Start next chunk with overlap
            current_start = best_boundary - self.overlap_size
            current_start = max(current_start, current_start)  # Ensure we move forward
        
        return boundaries
    
    def _find_best_boundary(self, content: str, start: int, target_end: int) -> int:
        """Find the best boundary position near the target end."""
        
        # Search window around target end
        search_start = max(start + self.min_chunk_size, target_end - 200)
        search_end = min(len(content), target_end + 200)
        
        search_region = content[search_start:search_end]
        
        # Priority 1: Semantic boundaries (headers, lists, etc.)
        for pattern in self.semantic_boundaries:
            matches = list(re.finditer(pattern, search_region))
            if matches:
                # Find the match closest to target
                closest_match = min(
                    matches,
                    key=lambda m: abs((search_start + m.start()) - target_end)
                )
                return search_start + closest_match.start()
        
        # Priority 2: Paragraph breaks
        paragraph_matches = list(self.paragraph_breaks.finditer(search_region))
        if paragraph_matches:
            closest_para = min(
                paragraph_matches,
                key=lambda m: abs((search_start + m.start()) - target_end)
            )
            return search_start + closest_para.start()
        
        # Priority 3: Sentence boundaries
        if self.preserve_sentences:
            sentence_matches = list(self.sentence_endings.finditer(search_region))
            if sentence_matches:
                closest_sentence = min(
                    sentence_matches,
                    key=lambda m: abs((search_start + m.end()) - target_end)
                )
                return search_start + closest_sentence.end()
        
        # Fallback: Word boundary
        target_in_region = target_end - search_start
        if 0 <= target_in_region < len(search_region):
            # Find nearest word boundary
            for offset in range(50):  # Search within 50 chars
                for direction in [-1, 1]:
                    pos = target_in_region + (offset * direction)
                    if 0 <= pos < len(search_region) and search_region[pos].isspace():
                        return search_start + pos
        
        # Last resort: exact target
        return target_end


class EmbeddingGenerator:
    """Generate vector embeddings for text chunks."""
    
    def __init__(self, model_name: str = "simple_tfidf"):
        self.model_name = model_name
        self.vocabulary: Dict[str, int] = {}
        self.idf_scores: Dict[str, float] = {}
        self.embedding_dimension = 512  # Default dimension
        
        # Load or initialize vocabulary
        self._initialize_vocabulary()
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for text."""
        
        if self.model_name == "simple_tfidf":
            return self._generate_tfidf_embedding(text)
        else:
            # Placeholder for other embedding models
            return self._generate_simple_embedding(text)
    
    def _generate_tfidf_embedding(self, text: str) -> List[float]:
        """Generate TF-IDF based embedding."""
        
        # Tokenize and clean text
        tokens = self._tokenize(text)
        
        # Calculate term frequencies
        token_counts = Counter(tokens)
        total_tokens = len(tokens)
        
        # Initialize embedding vector
        embedding = [0.0] * self.embedding_dimension
        
        # Calculate TF-IDF for each token
        for token, count in token_counts.items():
            if token in self.vocabulary:
                vocab_index = self.vocabulary[token] % self.embedding_dimension
                
                # Term frequency
                tf = count / total_tokens
                
                # Inverse document frequency
                idf = self.idf_scores.get(token, 1.0)
                
                # TF-IDF score
                tfidf = tf * idf
                
                # Add to embedding
                embedding[vocab_index] += tfidf
        
        # Normalize embedding
        norm = math.sqrt(sum(x * x for x in embedding))
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    def _generate_simple_embedding(self, text: str) -> List[float]:
        """Generate simple hash-based embedding."""
        
        # Simple embedding based on text characteristics
        tokens = self._tokenize(text)
        
        embedding = [0.0] * self.embedding_dimension
        
        # Character-based features
        char_counts = Counter(text.lower())
        for i, char in enumerate('abcdefghijklmnopqrstuvwxyz'):
            if i < self.embedding_dimension:
                embedding[i] = char_counts.get(char, 0) / len(text)
        
        # Token-based features
        for i, token in enumerate(tokens[:50]):  # Use first 50 tokens
            if i + 26 < self.embedding_dimension:
                # Simple hash of token
                token_hash = hash(token) % 1000 / 1000.0
                embedding[i + 26] = token_hash
        
        # Text statistics
        if self.embedding_dimension > 100:
            embedding[100] = len(text) / 1000.0  # Text length
            embedding[101] = len(tokens) / 100.0  # Token count
            embedding[102] = len(set(tokens)) / len(tokens) if tokens else 0  # Vocabulary diversity
        
        # Normalize
        norm = math.sqrt(sum(x * x for x in embedding))
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for embedding generation."""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into tokens
        tokens = text.split()
        
        # Filter short tokens and common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'this', 'that', 'these', 'those',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had'
        }
        
        tokens = [
            token for token in tokens
            if len(token) > 2 and token not in stop_words
        ]
        
        return tokens
    
    def _initialize_vocabulary(self):
        """Initialize vocabulary and IDF scores."""
        
        # Common technical vocabulary with initial IDF scores
        common_terms = {
            'api': 2.0, 'database': 2.0, 'function': 1.5, 'class': 1.5,
            'component': 2.0, 'service': 1.8, 'authentication': 2.5,
            'authorization': 2.5, 'deployment': 2.2, 'testing': 1.8,
            'framework': 2.0, 'library': 1.8, 'package': 1.5, 'module': 1.5,
            'configuration': 2.0, 'documentation': 1.8, 'tutorial': 2.0,
            'guide': 1.5, 'example': 1.2, 'implementation': 2.0,
            'integration': 2.2, 'optimization': 2.5, 'performance': 2.0,
            'security': 2.2, 'error': 1.5, 'debug': 2.0, 'fix': 1.5,
            'bug': 1.8, 'feature': 1.5, 'requirement': 2.0, 'specification': 2.2
        }
        
        # Build vocabulary index
        for i, term in enumerate(common_terms.keys()):
            self.vocabulary[term] = i
        
        # Set IDF scores
        self.idf_scores = common_terms
    
    def update_vocabulary(self, texts: List[str]):
        """Update vocabulary based on new texts."""
        
        # Count document frequencies
        doc_frequencies = defaultdict(int)
        total_docs = len(texts)
        
        for text in texts:
            tokens = set(self._tokenize(text))
            for token in tokens:
                doc_frequencies[token] += 1
        
        # Update IDF scores
        for token, doc_freq in doc_frequencies.items():
            if doc_freq > 0:
                idf = math.log(total_docs / doc_freq)
                self.idf_scores[token] = idf
                
                # Add to vocabulary if new
                if token not in self.vocabulary:
                    self.vocabulary[token] = len(self.vocabulary)


class SimilaritySearch:
    """Cosine similarity search engine."""
    
    def __init__(self):
        self.embeddings: Dict[str, VectorEmbedding] = {}
        self.chunks: Dict[str, SemanticChunk] = {}
        
        # Search optimization
        self.search_cache: Dict[str, List[SimilarityResult]] = {}
        self.cache_max_size = 1000
    
    def add_embedding(self, embedding: VectorEmbedding, chunk: SemanticChunk):
        """Add embedding and chunk to search index."""
        self.embeddings[embedding.chunk_id] = embedding
        self.chunks[chunk.chunk_id] = chunk
        
        # Clear cache when index is updated
        self.search_cache.clear()
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        similarity_threshold: float = 0.1
    ) -> List[SimilarityResult]:
        """Search for similar chunks using cosine similarity."""
        
        # Create cache key
        cache_key = hashlib.md5(
            f"{query_embedding[:10]}{top_k}{similarity_threshold}".encode()
        ).hexdigest()
        
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]
        
        similarities = []
        
        for chunk_id, embedding in self.embeddings.items():
            similarity = self._cosine_similarity(query_embedding, embedding.embedding)
            
            if similarity >= similarity_threshold:
                chunk = self.chunks[chunk_id]
                
                result = SimilarityResult(
                    chunk_id=chunk_id,
                    content=chunk.content,
                    similarity_score=similarity,
                    source_id=chunk.source_id,
                    source_type=chunk.source_type,
                    metadata=chunk.metadata,
                    rank=0  # Will be set after sorting
                )
                
                similarities.append(result)
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x.similarity_score, reverse=True)
        
        # Set ranks and limit results
        results = similarities[:top_k]
        for i, result in enumerate(results):
            result.rank = i + 1
        
        # Cache results
        if len(self.search_cache) < self.cache_max_size:
            self.search_cache[cache_key] = results
        
        return results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        
        if len(vec1) != len(vec2):
            return 0.0
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        # Avoid division by zero
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def get_related_chunks(self, chunk_id: str, top_k: int = 5) -> List[SimilarityResult]:
        """Get chunks similar to a given chunk."""
        
        if chunk_id not in self.embeddings:
            return []
        
        embedding = self.embeddings[chunk_id]
        results = self.search(embedding.embedding, top_k + 1)  # +1 to exclude self
        
        # Remove the chunk itself from results
        return [r for r in results if r.chunk_id != chunk_id][:top_k]


class ContextAssembler:
    """Dynamic context window construction for queries."""
    
    def __init__(self, max_context_length: int = 4000):
        self.max_context_length = max_context_length
    
    def assemble_context(
        self,
        query: str,
        search_results: List[SimilarityResult],
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Assemble context from search results."""
        
        context_parts = []
        current_length = 0
        used_sources = set()
        
        # Add query context
        query_section = f"Query: {query}\n\n"
        context_parts.append(query_section)
        current_length += len(query_section)
        
        # Add search results in order of relevance
        for result in search_results:
            # Estimate length if we add this result
            result_text = self._format_result(result, include_metadata)
            result_length = len(result_text)
            
            # Check if we have space
            if current_length + result_length > self.max_context_length:
                # Try to fit a truncated version
                remaining_space = self.max_context_length - current_length - 100  # Leave some buffer
                if remaining_space > 200:  # Only if we have reasonable space
                    truncated_content = result.content[:remaining_space] + "..."
                    result_text = self._format_result_with_content(
                        result, truncated_content, include_metadata
                    )
                    context_parts.append(result_text)
                    current_length += len(result_text)
                break
            
            # Add full result
            context_parts.append(result_text)
            current_length += result_length
            used_sources.add(result.source_id)
        
        # Assemble final context
        context_text = "\n".join(context_parts)
        
        return {
            'context_text': context_text,
            'context_length': current_length,
            'num_results_used': len([r for r in search_results if r.chunk_id in [p for p in context_parts]]),
            'sources_used': list(used_sources),
            'truncated': current_length >= self.max_context_length - 100
        }
    
    def _format_result(
        self,
        result: SimilarityResult,
        include_metadata: bool = True
    ) -> str:
        """Format a search result for context."""
        return self._format_result_with_content(
            result, result.content, include_metadata
        )
    
    def _format_result_with_content(
        self,
        result: SimilarityResult,
        content: str,
        include_metadata: bool = True
    ) -> str:
        """Format a search result with custom content."""
        
        formatted = f"[Rank {result.rank}, Similarity: {result.similarity_score:.3f}]\n"
        
        if include_metadata:
            formatted += f"Source: {result.source_type} ({result.source_id})\n"
            if result.metadata:
                for key, value in result.metadata.items():
                    if isinstance(value, str) and len(value) < 100:
                        formatted += f"{key}: {value}\n"
        
        formatted += f"Content: {content}\n"
        formatted += "---\n"
        
        return formatted


class VectorRAGSystem:
    """Main Vector RAG system coordinating all components."""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / '.claude' / 'vectors'
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.chunker = SemanticChunker()
        self.embedding_generator = EmbeddingGenerator()
        self.similarity_search = SimilaritySearch()
        self.context_assembler = ContextAssembler()

        # Load existing data
        self._load_existing_data()

        # Performance metrics
        self.query_count = 0
        self.total_query_time = 0.0

    def _load_existing_data(self):
        """Load existing vector data from disk."""
        try:
            vectors_file = self.storage_path / 'vectors.json'
            chunks_file = self.storage_path / 'chunks.json'

            # Load chunks
            if chunks_file.exists():
                with open(chunks_file, 'r') as f:
                    chunks_data = json.load(f)
                    for chunk_data in chunks_data:
                        chunk = SemanticChunk(
                            chunk_id=chunk_data['chunk_id'],
                            content=chunk_data['content'],
                            source_id=chunk_data['source_id'],
                            source_type=chunk_data['source_type'],
                            created_at=datetime.fromisoformat(chunk_data['created_at']),
                            chunk_index=chunk_data['chunk_index'],
                            total_chunks=chunk_data['total_chunks'],
                            overlap_with_previous=chunk_data['overlap_with_previous'],
                            overlap_with_next=chunk_data['overlap_with_next'],
                            metadata=chunk_data['metadata']
                        )
                        self.similarity_search.chunks[chunk.chunk_id] = chunk

            # Load vectors
            if vectors_file.exists():
                with open(vectors_file, 'r') as f:
                    vectors_data = json.load(f)
                    for vector_data in vectors_data:
                        embedding = VectorEmbedding(
                            vector_id=vector_data['vector_id'],
                            chunk_id=vector_data['chunk_id'],
                            embedding=vector_data['embedding'],
                            embedding_model=vector_data['embedding_model'],
                            embedding_dimension=vector_data['embedding_dimension'],
                            created_at=datetime.fromisoformat(vector_data['created_at']),
                            norm=vector_data['norm']
                        )
                        self.similarity_search.embeddings[embedding.chunk_id] = embedding

        except Exception as e:
            # If loading fails, start fresh
            pass

    def _save_data(self):
        """Save vector data to disk."""
        try:
            # Save chunks
            chunks_file = self.storage_path / 'chunks.json'
            chunks_data = [chunk.to_dict() for chunk in self.similarity_search.chunks.values()]
            with open(chunks_file, 'w') as f:
                json.dump(chunks_data, f, indent=2)

            # Save vectors
            vectors_file = self.storage_path / 'vectors.json'
            vectors_data = [embedding.to_dict() for embedding in self.similarity_search.embeddings.values()]
            with open(vectors_file, 'w') as f:
                json.dump(vectors_data, f, indent=2)

            return True
        except Exception as e:
            return False

    def add_content(
        self,
        content: str,
        source_id: str = None,
        source_type: str = "message",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add content to the vector database."""

        if source_id is None:
            source_id = str(uuid.uuid4())

        # Chunk the content
        chunks = self.chunker.chunk_content(content, source_id, source_type, metadata)

        # Generate embeddings and add to search index
        added_chunks = []
        for chunk in chunks:
            embedding_vector = self.embedding_generator.generate_embedding(chunk.content)

            # Calculate norm
            norm = math.sqrt(sum(x * x for x in embedding_vector))

            embedding = VectorEmbedding(
                vector_id=str(uuid.uuid4()),
                chunk_id=chunk.chunk_id,
                embedding=embedding_vector,
                embedding_model=self.embedding_generator.model_name,
                embedding_dimension=self.embedding_generator.embedding_dimension,
                created_at=datetime.now(),
                norm=norm
            )

            self.similarity_search.add_embedding(embedding, chunk)
            added_chunks.append(chunk.chunk_id)

        # Update vocabulary with new content
        self.embedding_generator.update_vocabulary([chunk.content for chunk in chunks])

        # Save data
        self._save_data()

        return {
            'source_id': source_id,
            'chunks_added': len(added_chunks),
            'chunk_ids': added_chunks
        }

    def query(
        self,
        query_text: str,
        top_k: int = 10,
        similarity_threshold: float = 0.1,
        include_context: bool = True
    ) -> Dict[str, Any]:
        """Query the vector database."""

        import time
        start_time = time.time()

        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query_text)

        # Search for similar chunks
        results = self.similarity_search.search(query_embedding, top_k, similarity_threshold)

        # Assemble context if requested
        context = None
        if include_context and results:
            context = self.context_assembler.assemble_context(query_text, results)

        # Update metrics
        query_time = time.time() - start_time
        self.query_count += 1
        self.total_query_time += query_time

        return {
            'query': query_text,
            'results_count': len(results),
            'results': [
                {
                    'chunk_id': r.chunk_id,
                    'content': r.content,
                    'similarity_score': r.similarity_score,
                    'source_id': r.source_id,
                    'source_type': r.source_type,
                    'rank': r.rank,
                    'metadata': r.metadata
                }
                for r in results
            ],
            'context': context,
            'query_time': query_time
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get vector database statistics."""

        return {
            'total_chunks': len(self.similarity_search.chunks),
            'total_embeddings': len(self.similarity_search.embeddings),
            'vocabulary_size': len(self.embedding_generator.vocabulary),
            'embedding_dimension': self.embedding_generator.embedding_dimension,
            'embedding_model': self.embedding_generator.model_name,
            'query_count': self.query_count,
            'average_query_time': self.total_query_time / self.query_count if self.query_count > 0 else 0,
            'storage_path': str(self.storage_path),
            'cache_size': len(self.similarity_search.search_cache)
        }

class RAGVectorizer:
    """Compatibility wrapper for VectorRAGSystem.

    This wrapper maintains backward compatibility with existing code
    that uses RAGVectorizer while delegating to VectorRAGSystem.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.system = VectorRAGSystem(storage_path)

    def add_content(
        self,
        content: str,
        source_id: str = None,
        source_type: str = "message",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add content to the vector database."""
        return self.system.add_content(content, source_id, source_type, metadata)

    def query(
        self,
        query_text: str,
        top_k: int = 10,
        similarity_threshold: float = 0.1,
        include_context: bool = True
    ) -> Dict[str, Any]:
        """Query the vector database."""
        return self.system.query(query_text, top_k, similarity_threshold, include_context)

    def _save_data(self):
        """Save vector data to disk."""
        return self.system._save_data()

    def _load_existing_data(self):
        """Load existing vector data from disk."""
        return self.system._load_existing_data()

    def get_statistics(self) -> Dict[str, Any]:
        """Get vector database statistics."""
        return self.system.get_statistics()