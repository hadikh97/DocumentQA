from django.core.management import call_command
from django.core.management.base import BaseCommand

from documents.models import Document, Question, Tag
from documents.services.retriever import refresh_index


class Command(BaseCommand):
    help = 'Load sample data for testing the Document QA system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading samples',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Question.objects.all().delete()
            Document.objects.all().delete()
            Tag.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        self.stdout.write('Loading sample data...')

        call_command('loaddata', 'sample_data.json', verbosity=0)

        doc_count = Document.objects.count()
        tag_count = Tag.objects.count()
        question_count = Question.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f'Loaded {doc_count} documents, {tag_count} tags, '
                f'{question_count} questions.'
            )
        )

        self.stdout.write('Refreshing search index...')
        indexed = refresh_index()
        self.stdout.write(
            self.style.SUCCESS(f'Indexed {indexed} documents.')
        )

        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))
