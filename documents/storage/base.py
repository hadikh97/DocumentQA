from abc import ABC, abstractmethod
from typing import Optional


class DocumentStorageBackend(ABC):
    """
    Abstract base class for document content storage backends.

    This interface allows swapping between different storage implementations
    (database, object storage, etc.) without changing the application logic.
    """

    @abstractmethod
    def save_content(self, document_id: int, content: str) -> str:
        """
        Save document content to storage.

        Args:
            document_id: The ID of the document.
            content: The text content to store.

        Returns:
            str: A reference string identifying where the content is stored.
                 For database backend, this is typically "db".
                 For object storage, this might be "s3://bucket/key".
        """
        pass

    @abstractmethod
    def get_content(self, document_id: int, reference: str) -> Optional[str]:
        """
        Retrieve document content from storage.

        Args:
            document_id: The ID of the document.
            reference: The storage reference returned by save_content.

        Returns:
            str: The document content, or None if not found.
        """
        pass

    @abstractmethod
    def delete_content(self, document_id: int, reference: str) -> bool:
        """
        Delete document content from storage.

        Args:
            document_id: The ID of the document.
            reference: The storage reference returned by save_content.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        pass

    def update_content(self, document_id: int, reference: str, content: str) -> str:
        """
        Update document content in storage.

        Default implementation deletes old content and saves new content.
        Subclasses may override for more efficient implementations.

        Args:
            document_id: The ID of the document.
            reference: The current storage reference.
            content: The new content to store.

        Returns:
            str: The new storage reference.
        """
        self.delete_content(document_id, reference)
        return self.save_content(document_id, content)
