from django.contrib import admin, messages
from django.utils.html import format_html

from .models import Document, Question, Tag
from .services.retriever import get_retriever, refresh_index
from .services.qa_chain import get_qa_service


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin configuration for Tag model."""

    list_display = ('name', 'document_count', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin configuration for Document model."""

    list_display = ('title', 'date', 'content_preview_display', 'tag_count', 'created_at')
    list_filter = ('date', 'tags', 'created_at')
    search_fields = ('title', 'content')
    filter_horizontal = ('tags',)
    date_hierarchy = 'date'
    ordering = ('-date', '-created_at')
    actions = ['refresh_search_index']

    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'date')
        }),
        ('Categorization', {
            'fields': ('tags',)
        }),
        ('Metadata', {
            'fields': ('content_reference', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('content_reference', 'created_at', 'updated_at')

    def content_preview_display(self, obj):
        """Display truncated content preview."""
        return obj.content_preview(length=100)
    content_preview_display.short_description = 'Content Preview'

    def tag_count(self, obj):
        """Display the number of tags."""
        count = obj.tags.count()
        return count
    tag_count.short_description = 'Tags'

    @admin.action(description='Refresh search index')
    def refresh_search_index(self, request, queryset):
        """Refresh the TF-IDF search index."""
        count = refresh_index()
        self.message_user(
            request,
            f'Search index refreshed. {count} documents indexed.',
            messages.SUCCESS
        )

    def save_model(self, request, obj, form, change):
        """Refresh index when a document is saved."""
        super().save_model(request, obj, form, change)
        refresh_index()

    def delete_model(self, request, obj):
        """Refresh index when a document is deleted."""
        super().delete_model(request, obj)
        refresh_index()


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin configuration for Question model."""

    list_display = ('question_preview_display', 'has_answer', 'document_count', 'created_at', 'answered_at')
    list_filter = ('answered_at', 'created_at')
    search_fields = ('text', 'answer')
    filter_horizontal = ('related_documents',)
    ordering = ('-created_at',)
    actions = ['find_relevant_documents', 'generate_answers']

    fieldsets = (
        ('Question', {
            'fields': ('text',)
        }),
        ('Answer', {
            'fields': ('answer', 'answered_at'),
        }),
        ('Related Documents', {
            'fields': ('related_documents', 'retrieved_documents_display'),
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('answer', 'answered_at', 'created_at', 'retrieved_documents_display')

    def question_preview_display(self, obj):
        """Display truncated question preview."""
        return obj.question_preview(length=80)
    question_preview_display.short_description = 'Question'

    def document_count(self, obj):
        """Display the number of related documents."""
        count = obj.related_documents.count()
        if count > 0:
            return format_html('<span style="color: green;">{}</span>', count)
        return format_html('<span style="color: gray;">0</span>')
    document_count.short_description = 'Documents'

    def has_answer(self, obj):
        """Display whether the question has been answered."""
        return bool(obj.answer)
    has_answer.boolean = True
    has_answer.short_description = 'Answered'

    def retrieved_documents_display(self, obj):
        """Display retrieved documents with similarity scores."""
        if not obj.pk:
            return "Save the question first to see relevant documents."

        retriever = get_retriever()
        results = retriever.find_relevant(obj.text, top_k=5)

        if not results:
            return "No documents found. Make sure documents are indexed."

        html_parts = ['<table style="width:100%; border-collapse: collapse;">']
        html_parts.append(
            '<tr style="background-color: #f0f0f0;">'
            '<th style="padding: 8px; text-align: left;">Document</th>'
            '<th style="padding: 8px; text-align: left;">Score</th>'
            '<th style="padding: 8px; text-align: left;">Preview</th>'
            '</tr>'
        )

        for result in results:
            score_color = 'green' if result.score > 0.3 else 'orange' if result.score > 0.1 else 'gray'
            html_parts.append(
                f'<tr>'
                f'<td style="padding: 8px; border-bottom: 1px solid #ddd;">'
                f'<a href="/admin/documents/document/{result.document_id}/change/">{result.title}</a>'
                f'</td>'
                f'<td style="padding: 8px; border-bottom: 1px solid #ddd; color: {score_color};">'
                f'{result.score:.3f}'
                f'</td>'
                f'<td style="padding: 8px; border-bottom: 1px solid #ddd; font-size: 0.9em; color: #666;">'
                f'{result.content_preview[:100]}...'
                f'</td>'
                f'</tr>'
            )

        html_parts.append('</table>')
        return format_html(''.join(html_parts))

    retrieved_documents_display.short_description = 'Relevant Documents (TF-IDF)'

    @admin.action(description='Find relevant documents for selected questions')
    def find_relevant_documents(self, request, queryset):
        """Find and associate relevant documents for selected questions."""
        retriever = get_retriever()

        if not retriever.is_indexed:
            refresh_index()

        updated_count = 0
        for question in queryset:
            results = retriever.find_relevant_documents(question.text, top_k=3, min_score=0.05)

            if results:
                question.related_documents.clear()
                for doc, score in results:
                    question.related_documents.add(doc)
                updated_count += 1

        self.message_user(
            request,
            f'Found relevant documents for {updated_count} question(s).',
            messages.SUCCESS
        )

    @admin.action(description='Generate answers for selected questions')
    def generate_answers(self, request, queryset):
        """Generate answers for selected questions using LLM."""
        qa_service = get_qa_service()

        success_count = 0
        error_count = 0

        for question in queryset:
            try:
                qa_service.answer_question(question)
                success_count += 1
            except Exception as e:
                error_count += 1
                self.message_user(
                    request,
                    f'Error generating answer for "{question.text[:30]}...": {str(e)}',
                    messages.ERROR
                )

        if success_count > 0:
            self.message_user(
                request,
                f'Successfully generated answers for {success_count} question(s).',
                messages.SUCCESS
            )

        if error_count > 0:
            self.message_user(
                request,
                f'Failed to generate answers for {error_count} question(s).',
                messages.WARNING
            )
