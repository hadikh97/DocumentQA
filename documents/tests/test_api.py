from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from documents.models import Document, Question, Tag


class DocumentAPITest(APITestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name='Technology')
        self.document = Document.objects.create(
            title='Test Document',
            content='Test content for the document.'
        )
        self.document.tags.add(self.tag)

    def test_list_documents(self):
        url = reverse('documents:document-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_document_detail(self):
        url = reverse('documents:document-detail', args=[self.document.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Document')


class QuestionAPITest(APITestCase):
    def setUp(self):
        self.question = Question.objects.create(
            text='What is machine learning?'
        )

    def test_list_questions(self):
        url = reverse('documents:question-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_question(self):
        url = reverse('documents:question-list')
        data = {'text': 'What is cloud computing?'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 2)


class RetrievalAPITest(APITestCase):
    def setUp(self):
        self.doc1 = Document.objects.create(
            title='Machine Learning',
            content='Machine learning is a type of artificial intelligence.'
        )
        self.doc2 = Document.objects.create(
            title='Cloud Computing',
            content='Cloud computing provides computing resources over the internet.'
        )

    def test_retrieve_documents(self):
        url = reverse('documents:retrieve')
        data = {'question': 'machine learning'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('question', response.data)

    def test_retrieve_with_top_k(self):
        url = reverse('documents:retrieve')
        data = {'question': 'computing', 'top_k': 1}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['results']), 1)

    def test_retrieve_missing_question(self):
        url = reverse('documents:retrieve')
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AskQuestionAPITest(APITestCase):
    def setUp(self):
        self.document = Document.objects.create(
            title='AI Overview',
            content='Artificial intelligence is the simulation of human intelligence.'
        )

    def test_ask_question(self):
        url = reverse('documents:ask')
        data = {'question': 'What is artificial intelligence?'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('answer', response.data)
        self.assertIn('question_id', response.data)

    def test_ask_creates_question_record(self):
        url = reverse('documents:ask')
        data = {'question': 'What is AI?'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 1)

        question = Question.objects.first()
        self.assertEqual(question.text, 'What is AI?')
        self.assertIsNotNone(question.answer)


class RefreshIndexAPITest(APITestCase):
    def setUp(self):
        Document.objects.create(title='Doc 1', content='Content 1')
        Document.objects.create(title='Doc 2', content='Content 2')

    def test_refresh_index(self):
        url = reverse('documents:refresh-index')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['documents_indexed'], 2)
