import os
from datetime import timedelta  # Added this import

from django.core.management.base import BaseCommand
from django.utils import timezone

from FileUpload.models import FileUpload


class Command(BaseCommand):
    help = 'Deletes files older than 24 hours (both database records and physical files)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate the deletion without actually deleting anything',
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Number of hours after which files should be deleted (default: 24)',
        )
        parser.add_argument(
            '--minutes',
            type=int,
            default=0,
            help='Additional minutes threshold (combined with hours)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        hours = options['hours']
        minutes = options['minutes']

        # Calculate the threshold time
        threshold = timezone.now() - timedelta(hours=hours, minutes=minutes)

        old_files = FileUpload.objects.filter(created_at__lt=threshold)
        total_count = old_files.count()
        deleted_count = 0
        errors = 0

        self.stdout.write(f"Found {total_count} files older than {hours} hours and {minutes} minutes")

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run mode - no files will be deleted"))
            return

        for file_obj in old_files:
            try:
                # Delete physical file if it exists
                if file_obj.file:
                    file_path = file_obj.file.path  # More reliable way to get path
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        self.stdout.write(f"Deleted file: {file_path}")
                    else:
                        self.stdout.write(f"File not found: {file_path}")

                # Delete database record
                file_obj.delete()
                deleted_count += 1

            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f"Error deleting {file_obj.name}: {str(e)}"))
                continue

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted {deleted_count}/{total_count} files. Errors: {errors}"
            )
        )
