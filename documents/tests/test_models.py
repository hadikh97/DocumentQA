from django.test import TestCase
from django.utils import timezone

from documents.models import Document, Question, Tag


class TagModelTest(TestCase):
    def test_create_tag(self):
        tag = Tag.objects.create(name='Technology')
        self.assertEqual(str(tag), 'Technology')
        self.assertEqual(tag.document_count(), 0)

    def test_tag_document_count(self):
        tag = Tag.objects.create(name='Science')
        doc = Document.objects.create(
            title='Test Doc',
            content='Test content'
        )
        doc.tags.add(tag)
        self.assertEqual(tag.document_count(), 1)


class DocumentModelTest(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name='Test Tag')
        self.document = Document.objects.create(
            title='Test Document',
            content='This is test content for the document.',
            date=timezone.now().date()
        )
        self.document.tags.add(self.tag)

    def test_document_str(self):
        self.assertEqual(str(self.document), 'Test Document')

    def test_content_preview_short(self):
        doc = Document.objects.create(
            title='Short',
            content='Short content'
        )
        self.assertEqual(doc.content_preview(), 'Short content')

    def test_content_preview_long(self):
        long_content = 'A' * 200
        doc = Document.objects.create(
            title='Long',
            content=long_content
        )
        preview = doc.content_preview(length=100)
        self.assertEqual(len(preview), 103)  # 100 + '...'
        self.assertTrue(preview.endswith('...'))

    def test_tag_list(self):
        self.assertEqual(self.document.tag_list(), 'Test Tag')

    def test_default_content_reference(self):
        self.assertEqual(self.document.content_reference, 'db')


class QuestionModelTest(TestCase):
    def setUp(self):
        self.question = Question.objects.create(
            text='What is machine learning?'
        )

    def test_question_str(self):
        self.assertEqual(str(self.question), 'What is machine learning?')

    def test_question_str_truncation(self):
        long_question = Question.objects.create(
            text='A' * 100
        )
        self.assertEqual(len(str(long_question)), 53)  # 50 + '...'

    def test_has_answer_false(self):
        self.assertFalse(self.question.has_answer())

    def test_has_answer_true(self):
        self.question.answer = 'Machine learning is...'
        self.question.save()
        self.assertTrue(self.question.has_answer())

    def test_question_preview(self):
        preview = self.question.question_preview(length=10)
        self.assertEqual(preview, 'What is ma...')
