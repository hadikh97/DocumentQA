from django.db import models
from django.utils import timezone


class Tag(models.Model):
    """Tag model for categorizing documents."""

    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name

    def document_count(self):
        """Return the number of documents with this tag."""
        return self.documents.count()
    document_count.short_description = 'Documents'


class Document(models.Model):
    """Document model for storing textual documents."""

    title = models.CharField(max_length=255)
    content = models.TextField(help_text='Full text content of the document')
    content_reference = models.CharField(
        max_length=255,
        default='db',
        help_text='Storage reference for future backends (db, s3://bucket/key, etc.)'
    )
    date = models.DateField(default=timezone.now)
    tags = models.ManyToManyField(Tag, related_name='documents', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

    def __str__(self):
        return self.title

    def content_preview(self, length=100):
        """Return a truncated preview of the content."""
        if len(self.content) <= length:
            return self.content
        return self.content[:length] + '...'
    content_preview.short_description = 'Content Preview'

    def tag_list(self):
        """Return comma-separated list of tag names."""
        return ', '.join(tag.name for tag in self.tags.all())
    tag_list.short_description = 'Tags'


class Question(models.Model):
    """Question model for storing user questions and generated answers."""

    text = models.TextField(help_text='The question text')
    answer = models.TextField(
        blank=True,
        null=True,
        help_text='Generated answer based on document content'
    )
    related_documents = models.ManyToManyField(
        Document,
        related_name='questions',
        blank=True,
        help_text='Documents used to generate the answer'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='When the answer was generated'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return self.text[:50] + ('...' if len(self.text) > 50 else '')

    def has_answer(self):
        """Check if the question has been answered."""
        return bool(self.answer)
    has_answer.boolean = True
    has_answer.short_description = 'Answered'

    def question_preview(self, length=100):
        """Return a truncated preview of the question."""
        if len(self.text) <= length:
            return self.text
        return self.text[:length] + '...'
    question_preview.short_description = 'Question'
