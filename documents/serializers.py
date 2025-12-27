from rest_framework import serializers

from .models import Document, Question, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""

    class Meta:
        model = Tag
        fields = ['id', 'name']


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model."""

    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = ['id', 'title', 'content', 'date', 'tags', 'created_at', 'updated_at']


class DocumentSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for Document list views."""

    class Meta:
        model = Document
        fields = ['id', 'title', 'date']


class RetrievalResultSerializer(serializers.Serializer):
    """Serializer for document retrieval results."""

    document_id = serializers.IntegerField()
    title = serializers.CharField()
    score = serializers.FloatField()
    content_preview = serializers.CharField()


class RetrievalRequestSerializer(serializers.Serializer):
    """Serializer for retrieval request."""

    question = serializers.CharField(required=True, min_length=1)
    top_k = serializers.IntegerField(required=False, default=3, min_value=1, max_value=10)
    min_score = serializers.FloatField(required=False, default=0.0, min_value=0.0, max_value=1.0)


class RetrievalResponseSerializer(serializers.Serializer):
    """Serializer for retrieval response."""

    question = serializers.CharField()
    results = RetrievalResultSerializer(many=True)
    total_documents = serializers.IntegerField()


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model."""

    related_documents = DocumentSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'answer', 'related_documents', 'created_at', 'answered_at']
        read_only_fields = ['answer', 'related_documents', 'answered_at']


class QuestionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating questions."""

    class Meta:
        model = Question
        fields = ['id', 'text', 'created_at']
        read_only_fields = ['created_at']


class AskQuestionRequestSerializer(serializers.Serializer):
    """Serializer for ask question request."""

    question = serializers.CharField(required=True, min_length=1)


class AskQuestionResponseSerializer(serializers.Serializer):
    """Serializer for ask question response."""

    question_id = serializers.IntegerField()
    question = serializers.CharField()
    answer = serializers.CharField()
    related_documents = DocumentSummarySerializer(many=True)
    answered_at = serializers.DateTimeField()
