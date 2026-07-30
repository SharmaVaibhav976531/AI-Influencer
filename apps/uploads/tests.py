import os
import tempfile
import numpy as np
import pandas as pd
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.uploads.models import Upload
from apps.uploads.utils import (
    clean_text, parse_followers, normalize_platform, clean_json, clean_list, normalize_influencer_dict
)
from apps.uploads.services import process_upload_file
from apps.influencers.models import Influencer

User = get_user_model()

class NormalizationUtilsTest(TestCase):
    def test_clean_text_normalization(self):
        """Test clean_text handles None, NaNs, empty, whitespace, and unicode correctly."""
        self.assertEqual(clean_text(None), "")
        self.assertEqual(clean_text(np.nan), "")
        self.assertEqual(clean_text(float('nan')), "")
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text("   "), "")
        self.assertEqual(clean_text("  hello   world  "), "hello world")
        self.assertEqual(clean_text("🚀 Tech Guru 🇮🇳"), "🚀 Tech Guru 🇮🇳")
        self.assertEqual(clean_text("<script>alert('XSS')</script>"), "<script>alert('XSS')</script>")

    def test_parse_followers(self):
        """Test parse_followers converts formats, strings, and handles NaNs safely."""
        self.assertEqual(parse_followers(None), 0)
        self.assertEqual(parse_followers(np.nan), 0)
        self.assertEqual(parse_followers(""), 0)
        self.assertEqual(parse_followers("   "), 0)
        self.assertEqual(parse_followers("N/A"), 0)
        self.assertEqual(parse_followers("Unknown"), 0)
        self.assertEqual(parse_followers("-500"), 0)
        self.assertEqual(parse_followers("Ten Thousand"), 0)
        self.assertEqual(parse_followers("500"), 500)
        self.assertEqual(parse_followers("15K"), 15000)
        self.assertEqual(parse_followers("2.5M"), 2500000)
        self.assertEqual(parse_followers("1B"), 1000000000)

    def test_normalize_influencer_dict(self):
        """Test normalize_influencer_dict guarantees no None for non-nullable fields."""
        dirty_row = {
            'name': '  Priya Sharma  ',
            'handle': '  priyasharma_12  ',
            'platform': np.nan,
            'followers': '12.5K',
            'following': None,
            'posts': 'N/A',
            'bio': np.nan,
            'description': '   ',
            'language': None,
            'location': '  Mumbai  ',
            'profile_url': None,
            'email': np.nan,
            'website': '  '
        }
        normalized = normalize_influencer_dict(dirty_row)
        self.assertEqual(normalized['name'], "Priya Sharma")
        self.assertEqual(normalized['handle'], "priyasharma_12")
        self.assertEqual(normalized['platform'], "OTHER")
        self.assertEqual(normalized['followers'], 12500)
        self.assertEqual(normalized['following'], 0)
        self.assertEqual(normalized['total_posts'], 0)
        self.assertEqual(normalized['bio'], "")
        self.assertEqual(normalized['description'], "")
        self.assertEqual(normalized['language'], "")
        self.assertEqual(normalized['location'], "Mumbai")
        self.assertEqual(normalized['profile_url'], "")
        self.assertEqual(normalized['email'], "")
        self.assertEqual(normalized['website'], "")

class UploadProcessingETLTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='uploader',
            email='uploader@example.com',
            password='Password123!'
        )

    def test_upload_processing_with_empty_bio_and_nans(self):
        """Test process_upload_file with empty bio, NaNs, unicode, emojis, and whitespace."""
        csv_data = (
            "Name,Handle,Platform,Followers,Following,Posts,Bio,Description,Language,Location,Profile URL,Email,Website\n"
            "Rahul Tech,rahul_tech,Instagram,10K,500,100,,,\"  \",New Delhi,https://instagram.com/rahul,,\n"
            "🚀 Priya Digital 🇮🇳,priya_digital,YouTube,50K,1000,200,हिंदी में टेक!,Explore Tech,Hindi,Mumbai,https://yt.com/priya,priya@example.com,https://priya.com\n"
            "Amit Innovates,amit_innovates,Twitter,N/A,Unknown,-50,   ,   ,   ,   ,   ,   ,   \n"
        )

        with tempfile.NamedTemporaryFile(suffix='.csv', mode='w+', encoding='utf-8', delete=False) as tmp:
            tmp.write(csv_data)
            tmp_path = tmp.name

        try:
            with open(tmp_path, 'rb') as f:
                uploaded_file = SimpleUploadedFile(
                    name='edge_cases.csv',
                    content=f.read(),
                    content_type='text/csv'
                )

            upload = Upload.objects.create(
                user=self.user,
                original_filename='edge_cases.csv',
                file_type=Upload.FileType.CSV,
                file=uploaded_file,
                file_size=uploaded_file.size
            )


            # Execute processing engine
            process_upload_file(upload.id)
            upload.refresh_from_db()

            self.assertEqual(upload.processing_status, Upload.ProcessingStatus.COMPLETED)
            self.assertEqual(upload.total_rows, 3)

            # Check created Influencers in database
            influencers = Influencer.objects.filter(upload=upload).order_by('id')
            self.assertEqual(influencers.count(), 3)

            # Row 1: empty bio was passed in CSV -> must be saved as "" (never None)
            inf1 = influencers[0]
            self.assertEqual(inf1.handle, "rahul_tech")
            self.assertEqual(inf1.bio, "")
            self.assertEqual(inf1.description, "")
            self.assertIsNotNone(inf1.bio)
            self.assertIsNotNone(inf1.description)

            # Row 2: Unicode & Emojis preserved
            inf2 = influencers[1]
            self.assertEqual(inf2.name, "🚀 Priya Digital 🇮🇳")
            self.assertEqual(inf2.bio, "हिंदी में टेक!")

            # Row 3: Blank whitespace fields -> saved as "" (never None)
            inf3 = influencers[2]
            self.assertEqual(inf3.handle, "amit_innovates")
            self.assertEqual(inf3.bio, "")
            self.assertEqual(inf3.followers, 0)

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
