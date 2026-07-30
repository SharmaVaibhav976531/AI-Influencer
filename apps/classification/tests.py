import json
from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from apps.uploads.models import Upload
from apps.influencers.models import Influencer
from apps.classification.models import Classification, SearchCriteria

User = get_user_model()

class AIClassificationProgressStreamTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='ai_tester',
            email='ai_tester@example.com',
            password='Password123!'
        )
        self.client = Client()
        self.client.login(username='ai_tester', password='Password123!')

        # Create active search criteria
        self.criteria = SearchCriteria.objects.create(
            user=self.user,
            name='Default Criteria',
            status='ACTIVE'
        )

        # Create Upload
        self.upload = Upload.objects.create(
            user=self.user,
            original_filename='influencers.csv',
            file_type=Upload.FileType.CSV,
            file_size=1024,
            processing_status=Upload.ProcessingStatus.COMPLETED
        )

        # Create 2 test Influencers with NLP data
        self.inf1 = Influencer.objects.create(
            upload=self.upload,
            name='Stream Rahul Tech',
            handle='stream_rahul_tech_test',
            platform='YOUTUBE',
            followers=150000,
            bio='Tech enthusiast discussing Digital India',
            nlp_processed_at=timezone.now()
        )
        self.inf2 = Influencer.objects.create(
            upload=self.upload,
            name='Stream Priya Digital',
            handle='stream_priya_digital_test',
            platform='INSTAGRAM',
            followers=50000,
            bio='Startup India updates',
            nlp_processed_at=timezone.now()
        )


    @patch('apps.influencers.services.openrouter_service.OpenRouterService.classify_influencer')
    def test_ai_classification_stream_view(self, mock_classify):

        """Test streaming AI classification endpoint returns SSE content type and yields events."""
        mock_classify.return_value = {
            'overall_score': 85,
            'confidence_score': 90,
            'language': 'English',
            'orientation': 'Supportive',
            'content_niche': 'Technology',
            'matched_keywords': ['Digital India'],
            'recommendation': 'Recommend',
            'reason': 'Highly relevant content.',
            'summary': 'Tech creator.',
            'ai_model_name': 'test-model',
            'processing_time_seconds': 1.5
        }

        url = reverse('influencers:ai_classification_stream')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/event-stream')

        # Read streaming content
        content = b''.join(response.streaming_content).decode('utf-8')
        self.assertIn('data: {"type": "start"', content)
        self.assertIn('data: {"type": "item_complete"', content)
        self.assertIn('data: {"type": "complete"', content)

        # Verify DB records created
        classifications = Classification.objects.filter(influencer__upload__user=self.user)
        self.assertEqual(classifications.count(), 2)
        self.assertEqual(classifications.filter(status='COMPLETED').count(), 2)

    def test_ai_classification_stream_no_pending(self):
        """Test streaming endpoint when all influencers are already classified."""
        # Mark all classified
        Classification.objects.create(influencer=self.inf1, status='COMPLETED')
        Classification.objects.create(influencer=self.inf2, status='COMPLETED')

        url = reverse('influencers:ai_classification_stream')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        content = b''.join(response.streaming_content).decode('utf-8')
        self.assertIn('"type": "complete"', content)
        self.assertIn('"processed": 0', content)
