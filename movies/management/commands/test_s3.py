"""
Test S3 connection
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
from botocore.exceptions import ClientError


class Command(BaseCommand):
    help = 'Test AWS S3 connection'

    def handle(self, *args, **options):
        if not settings.USE_S3:
            self.stdout.write(self.style.ERROR('USE_S3 is False in settings'))
            return
        
        self.stdout.write(f'USE_S3: {settings.USE_S3}')
        self.stdout.write(f'Bucket: {settings.AWS_STORAGE_BUCKET_NAME}')
        self.stdout.write(f'Region: {settings.AWS_S3_REGION_NAME}')
        
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Test bucket access
            response = s3.list_objects_v2(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                MaxKeys=1
            )
            
            self.stdout.write(self.style.SUCCESS('✓ S3 connection successful!'))
            self.stdout.write(f'Bucket exists and is accessible')
            
        except ClientError as e:
            self.stdout.write(self.style.ERROR(f'✗ S3 Error: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error: {e}'))
