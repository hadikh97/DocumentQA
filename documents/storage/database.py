from typing import Optional

from .base import DocumentStorageBackend


class DatabaseStorageBackend(DocumentStorageBackend):
    """
    Database storage backend for document content.

    Stores content directly in the Document model's TextField.
    This is the default backend and requires no additional infrastructure.

    The content is stored inline in the database, and the reference
    is always "db" to indicate database storage.
    """

    REFERENCE = 'db'

    def save_content(self, document_id: int, content: str) -> str:
        """
        Save content to the database.

        For database storage, the content is saved directly to the
        Document.content field. This method updates the document
        in place.

        Args:
            document_id: The ID of the document.
            content: The text content to store.

        Returns:
            str: Always returns "db" as the reference.
        """
        from documents.models import Document

        Document.objects.filter(id=document_id).update(
            content=content,
            content_reference=self.REFERENCE
        )
        return self.REFERENCE

    def get_content(self, document_id: int, reference: str) -> Optional[str]:
        """
        Retrieve content from the database.

        Args:
            document_id: The ID of the document.
            reference: The storage reference (ignored for database backend).

        Returns:
            str: The document content, or None if not found.
        """
        from documents.models import Document

        try:
            document = Document.objects.get(id=document_id)
            return document.content
        except Document.DoesNotExist:
            return None

    def delete_content(self, document_id: int, reference: str) -> bool:
        """
        Delete content from the database.

        For database storage, this clears the content field.
        The document record itself is not deleted.

        Args:
            document_id: The ID of the document.
            reference: The storage reference (ignored for database backend).

        Returns:
            bool: True if the document was found and updated.
        """
        from documents.models import Document

        updated = Document.objects.filter(id=document_id).update(content='')
        return updated > 0

    def update_content(self, document_id: int, reference: str, content: str) -> str:
        """
        Update content in the database.

        Optimized implementation that directly updates the content field.

        Args:
            document_id: The ID of the document.
            reference: The current storage reference (ignored).
            content: The new content to store.

        Returns:
            str: Always returns "db" as the reference.
        """
        return self.save_content(document_id, content)
