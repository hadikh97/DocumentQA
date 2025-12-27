from dataclasses import dataclass
from typing import List, Optional, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


@dataclass
class RetrievalResult:
    """Represents a document retrieval result with similarity score."""
    document_id: int
    title: str
    score: float
    content_preview: str


class DocumentRetriever:
    """
    TF-IDF based document retrieval service.

    Uses scikit-learn's TfidfVectorizer to build a document index
    and cosine similarity to find relevant documents for a query.
    """

    def __init__(self):
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._tfidf_matrix = None
        self._document_ids: List[int] = []
        self._document_titles: List[str] = []
        self._document_previews: List[str] = []
        self._is_indexed = False

    def index_documents(self) -> int:
        """
        Build TF-IDF index from all documents in the database.

        Returns:
            int: Number of documents indexed.
        """
        from documents.models import Document

        documents = Document.objects.all().values_list('id', 'title', 'content')

        if not documents:
            self._is_indexed = False
            self._vectorizer = None
            self._tfidf_matrix = None
            self._document_ids = []
            self._document_titles = []
            self._document_previews = []
            return 0

        self._document_ids = []
        self._document_titles = []
        self._document_previews = []
        contents = []

        for doc_id, title, content in documents:
            self._document_ids.append(doc_id)
            self._document_titles.append(title)
            self._document_previews.append(
                content[:200] + '...' if len(content) > 200 else content
            )
            contents.append(content)

        self._vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=10000,
            ngram_range=(1, 2),
        )

        self._tfidf_matrix = self._vectorizer.fit_transform(contents)
        self._is_indexed = True

        return len(self._document_ids)

    def find_relevant(
        self,
        question: str,
        top_k: int = 3,
        min_score: float = 0.0
    ) -> List[RetrievalResult]:
        """
        Find the most relevant documents for a given question.

        Args:
            question: The search query or question.
            top_k: Maximum number of documents to return.
            min_score: Minimum similarity score threshold (0.0 to 1.0).

        Returns:
            List of RetrievalResult objects sorted by relevance.
        """
        if not self._is_indexed or self._vectorizer is None:
            self.index_documents()

        if not self._is_indexed or self._tfidf_matrix is None:
            return []

        question_vector = self._vectorizer.transform([question])

        similarities = cosine_similarity(question_vector, self._tfidf_matrix).flatten()

        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= min_score:
                results.append(RetrievalResult(
                    document_id=self._document_ids[idx],
                    title=self._document_titles[idx],
                    score=score,
                    content_preview=self._document_previews[idx]
                ))

        return results

    def find_relevant_documents(
        self,
        question: str,
        top_k: int = 3,
        min_score: float = 0.0
    ):
        """
        Find relevant Document model instances.

        Args:
            question: The search query or question.
            top_k: Maximum number of documents to return.
            min_score: Minimum similarity score threshold.

        Returns:
            List of tuples (Document, score) sorted by relevance.
        """
        from documents.models import Document

        results = self.find_relevant(question, top_k, min_score)

        if not results:
            return []

        doc_ids = [r.document_id for r in results]
        documents = Document.objects.filter(id__in=doc_ids)
        doc_map = {doc.id: doc for doc in documents}

        return [
            (doc_map[r.document_id], r.score)
            for r in results
            if r.document_id in doc_map
        ]

    @property
    def is_indexed(self) -> bool:
        """Check if documents have been indexed."""
        return self._is_indexed

    @property
    def document_count(self) -> int:
        """Get the number of indexed documents."""
        return len(self._document_ids)

    def clear_index(self) -> None:
        """Clear the current index."""
        self._vectorizer = None
        self._tfidf_matrix = None
        self._document_ids = []
        self._document_titles = []
        self._document_previews = []
        self._is_indexed = False


# Singleton instance for caching the index
_retriever_instance: Optional[DocumentRetriever] = None


def get_retriever() -> DocumentRetriever:
    """
    Get the singleton DocumentRetriever instance.

    Returns:
        DocumentRetriever: The shared retriever instance.
    """
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = DocumentRetriever()
    return _retriever_instance


def refresh_index() -> int:
    """
    Refresh the document index.

    Call this when documents are added, updated, or deleted.

    Returns:
        int: Number of documents indexed.
    """
    retriever = get_retriever()
    return retriever.index_documents()
