from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Document, Question, Tag
from .serializers import (
    AskQuestionRequestSerializer,
    DocumentSerializer,
    DocumentSummarySerializer,
    QuestionCreateSerializer,
    QuestionSerializer,
    RetrievalRequestSerializer,
    RetrievalResponseSerializer,
    TagSerializer,
)
from .services.retriever import get_retriever, refresh_index
from .services.qa_chain import get_qa_service


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing documents."""

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    """API endpoint for managing questions."""

    queryset = Question.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return QuestionCreateSerializer
        return QuestionSerializer


class RetrieveDocumentsView(APIView):
    """
    API endpoint to retrieve relevant documents for a question.

    POST /api/retrieve/
    {
        "question": "What is machine learning?",
        "top_k": 3,
        "min_score": 0.0
    }
    """

    def post(self, request):
        serializer = RetrievalRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question = serializer.validated_data['question']
        top_k = serializer.validated_data.get('top_k', 3)
        min_score = serializer.validated_data.get('min_score', 0.0)

        retriever = get_retriever()

        if not retriever.is_indexed:
            refresh_index()

        results = retriever.find_relevant(question, top_k=top_k, min_score=min_score)

        response_data = {
            'question': question,
            'results': [
                {
                    'document_id': r.document_id,
                    'title': r.title,
                    'score': r.score,
                    'content_preview': r.content_preview
                }
                for r in results
            ],
            'total_documents': retriever.document_count
        }

        response_serializer = RetrievalResponseSerializer(data=response_data)
        response_serializer.is_valid()

        return Response(response_serializer.data)


@api_view(['POST'])
def refresh_index_view(request):
    """
    API endpoint to refresh the document search index.

    POST /api/refresh-index/
    """
    count = refresh_index()
    return Response({
        'message': 'Index refreshed successfully',
        'documents_indexed': count
    })


class AskQuestionView(APIView):
    """
    API endpoint to ask a question and get an answer.

    POST /api/ask/
    {
        "question": "What is machine learning?"
    }

    This endpoint:
    1. Creates a new Question record
    2. Retrieves relevant documents
    3. Generates an answer using the LLM
    4. Returns the answer with related documents
    """

    def post(self, request):
        serializer = AskQuestionRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question_text = serializer.validated_data['question']

        question = Question.objects.create(text=question_text)

        qa_service = get_qa_service()

        try:
            qa_service.answer_question(question)
        except Exception as e:
            return Response(
                {'error': f'Failed to generate answer: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        question.refresh_from_db()

        response_data = {
            'question_id': question.id,
            'question': question.text,
            'answer': question.answer,
            'related_documents': DocumentSummarySerializer(
                question.related_documents.all(),
                many=True
            ).data,
            'answered_at': question.answered_at
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
