import os
import uuid

from django.db import models
from django.dispatch import receiver


class FileUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    size = models.PositiveIntegerField()  # Better for file sizes which can't be negative
    mime_type = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')  # Renamed from 'path' to 'file' for clarity
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']  # Optional: to order files by upload date

# This will delete the file when the model instance is deleted
@receiver(models.signals.post_delete, sender=FileUpload)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
