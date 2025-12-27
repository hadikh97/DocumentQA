from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter

from .views import (
    AskQuestionView,
    DocumentViewSet,
    QuestionViewSet,
    RetrieveDocumentsView,
    TagViewSet,
    refresh_index_view,
)

app_name = 'documents'

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'questions', QuestionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('retrieve/', csrf_exempt(RetrieveDocumentsView.as_view()), name='retrieve'),
    path('ask/', csrf_exempt(AskQuestionView.as_view()), name='ask'),
    path('refresh-index/', csrf_exempt(refresh_index_view), name='refresh-index'),
]
