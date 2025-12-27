from django.conf import settings
from django.utils.module_loading import import_string


def get_storage_backend():
    """
    Get the configured storage backend instance.

    Returns:
        DocumentStorageBackend: The configured storage backend.
    """
    backend_path = getattr(
        settings,
        'DOCUMENT_STORAGE_BACKEND',
        'documents.storage.database.DatabaseStorageBackend'
    )
    backend_class = import_string(backend_path)
    return backend_class()
