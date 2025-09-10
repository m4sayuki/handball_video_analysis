from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os

try:
    from storages.backends.s3boto3 import S3Boto3Storage
    HAS_S3 = True
except ImportError:
    HAS_S3 = False


class PushNotificationIconStorage:
    """プッシュ通知アイコン用のストレージクラス（S3またはローカル）"""
    
    def __new__(cls):
        # AWS認証情報が設定されている場合はS3を使用
        if getattr(settings, 'USE_S3', False) and HAS_S3:
            return S3PushNotificationIconStorage()
        else:
            return LocalPushNotificationIconStorage()


class S3PushNotificationIconStorage(S3Boto3Storage):
    """S3用のプッシュ通知アイコンストレージ"""
    location = 'media/push_notification_icons'
    default_acl = None  # ACLを使用しない
    file_overwrite = False


class LocalPushNotificationIconStorage(FileSystemStorage):
    """ローカル用のプッシュ通知アイコンストレージ"""
    
    def __init__(self):
        location = os.path.join(settings.MEDIA_ROOT, 'push_notification_icons')
        super().__init__(location=location)