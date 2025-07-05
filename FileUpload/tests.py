import os
import uuid
from datetime import timedelta
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.conf import settings
from FileUpload.models import FileUpload

# Create a temporary media directory for tests
TEST_DIR = os.path.join(settings.BASE_DIR, 'test_media')


@override_settings(MEDIA_ROOT=TEST_DIR)
class FileUploadDatabaseTests(TestCase):
    def setUp(self):
        # Create test files
        self.test_content = b"Test file content"
        self.test_file = SimpleUploadedFile(
            "test_file.txt",
            self.test_content,
            content_type="text/plain"
        )

        # Create model instance
        self.file_obj = FileUpload.objects.create(
            name="test_file.txt",
            size=len(self.test_content),
            mime_type="text/plain",
            file=self.test_file
        )

    def tearDown(self):
        # Clean up test files
        try:
            if os.path.exists(self.file_obj.file.path):
                os.remove(self.file_obj.file.path)
            if os.path.exists(TEST_DIR):
                os.rmdir(TEST_DIR)
        except:
            pass

    # --- Model Field Tests ---
    def test_model_creation(self):
        """Test that model instance is created with correct fields"""
        self.assertEqual(FileUpload.objects.count(), 1)
        db_obj = FileUpload.objects.first()

        self.assertEqual(db_obj.name, "test_file.txt")
        self.assertEqual(db_obj.size, len(self.test_content))
        self.assertEqual(db_obj.mime_type, "text/plain")
        self.assertTrue(db_obj.file.name.startswith('uploads/'))
        self.assertTrue(os.path.exists(db_obj.file.path))

    def test_uuid_primary_key(self):
        """Test that ID is a valid UUID"""
        self.assertIsInstance(self.file_obj.id, uuid.UUID)
        try:
            uuid.UUID(str(self.file_obj.id))
        except ValueError:
            self.fail("ID is not a valid UUID")

    def test_timestamps(self):
        """Test auto-created and auto-updated timestamps"""
        self.assertIsNotNone(self.file_obj.created_at)
        self.assertIsNotNone(self.file_obj.updated_at)
        self.assertTrue(self.file_obj.created_at <= timezone.now())
        self.assertTrue(self.file_obj.updated_at <= timezone.now())

    # --- File Handling Tests ---
    def test_file_storage_location(self):
        """Test file is stored in correct location"""
        expected_path = os.path.join(TEST_DIR, self.file_obj.file.name)
        self.assertEqual(self.file_obj.file.path, expected_path)
        self.assertTrue(os.path.exists(expected_path))

    def test_file_deletion_signal(self):
        """Test file is deleted from filesystem when model is deleted"""
        file_path = self.file_obj.file.path
        self.file_obj.delete()

        # Check both database and filesystem
        self.assertEqual(FileUpload.objects.count(), 0)
        self.assertFalse(os.path.exists(file_path))

    # --- String Representation ---
    def test_str_method(self):
        """Test the string representation of the model"""
        self.assertEqual(str(self.file_obj), "test_file.txt")
