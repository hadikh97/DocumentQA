from django.test import TestCase

from documents.models import Document, Tag
from documents.services.retriever import DocumentRetriever, get_retriever, refresh_index


class DocumentRetrieverTest(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name='Technology')

        self.doc1 = Document.objects.create(
            title='Machine Learning Basics',
            content='Machine learning is a subset of artificial intelligence. '
                    'It involves training algorithms on data to make predictions.'
        )
        self.doc1.tags.add(self.tag)

        self.doc2 = Document.objects.create(
            title='Cloud Computing Guide',
            content='Cloud computing provides on-demand computing resources. '
                    'Services include IaaS, PaaS, and SaaS.'
        )

        self.doc3 = Document.objects.create(
            title='Data Science Overview',
            content='Data science combines statistics, mathematics, and programming. '
                    'Machine learning is a key component of data science.'
        )

    def test_index_documents(self):
        retriever = DocumentRetriever()
        count = retriever.index_documents()
        self.assertEqual(count, 3)
        self.assertTrue(retriever.is_indexed)

    def test_find_relevant_ml_query(self):
        retriever = DocumentRetriever()
        retriever.index_documents()

        results = retriever.find_relevant('machine learning algorithms', top_k=2)

        self.assertEqual(len(results), 2)
        titles = [r.title for r in results]
        self.assertIn('Machine Learning Basics', titles)

    def test_find_relevant_cloud_query(self):
        retriever = DocumentRetriever()
        retriever.index_documents()

        results = retriever.find_relevant('cloud computing services', top_k=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, 'Cloud Computing Guide')

    def test_find_relevant_with_min_score(self):
        retriever = DocumentRetriever()
        retriever.index_documents()

        results = retriever.find_relevant('xyz random query', top_k=3, min_score=0.5)
        self.assertEqual(len(results), 0)

    def test_find_relevant_documents_returns_model_instances(self):
        retriever = DocumentRetriever()
        retriever.index_documents()

        results = retriever.find_relevant_documents('machine learning', top_k=2)

        self.assertTrue(len(results) > 0)
        doc, score = results[0]
        self.assertIsInstance(doc, Document)
        self.assertIsInstance(score, float)

    def test_clear_index(self):
        retriever = DocumentRetriever()
        retriever.index_documents()
        self.assertTrue(retriever.is_indexed)

        retriever.clear_index()
        self.assertFalse(retriever.is_indexed)
        self.assertEqual(retriever.document_count, 0)

    def test_get_retriever_singleton(self):
        retriever1 = get_retriever()
        retriever2 = get_retriever()
        self.assertIs(retriever1, retriever2)

    def test_refresh_index(self):
        count = refresh_index()
        self.assertEqual(count, 3)

    def test_empty_database(self):
        Document.objects.all().delete()

        retriever = DocumentRetriever()
        count = retriever.index_documents()

        self.assertEqual(count, 0)
        self.assertFalse(retriever.is_indexed)

        results = retriever.find_relevant('any query')
        self.assertEqual(len(results), 0)
