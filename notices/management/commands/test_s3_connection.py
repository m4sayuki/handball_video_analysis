from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
import tempfile
from datetime import datetime


class Command(BaseCommand):
    help = 'Amazon S3への接続をテストします'

    def add_arguments(self, parser):
        parser.add_argument(
            '--upload-test',
            action='store_true',
            help='実際にテストファイルをアップロードしてテストします',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== S3接続テスト開始 ==='))
        
        # 環境変数の確認
        self.check_environment_variables()
        
        # S3クライアントの作成テスト
        s3_client = self.test_s3_client_creation()
        if not s3_client:
            return
            
        # バケットの存在確認
        if not self.test_bucket_access(s3_client):
            return
            
        # アップロードテスト（オプション）
        if options['upload_test']:
            self.test_file_upload(s3_client)
            
        self.stdout.write(self.style.SUCCESS('=== S3接続テスト完了 ==='))

    def check_environment_variables(self):
        self.stdout.write('1. 環境変数の確認...')
        
        required_vars = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'AWS_STORAGE_BUCKET_NAME',
            'AWS_S3_REGION_NAME'
        ]
        
        for var in required_vars:
            value = os.environ.get(var)
            if value:
                if 'SECRET' in var:
                    display_value = '*' * len(value)
                else:
                    display_value = value
                self.stdout.write(f'  ✓ {var}: {display_value}')
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ {var}: 設定されていません')
                )
        
        use_s3 = getattr(settings, 'USE_S3', False)
        self.stdout.write(f'  USE_S3: {use_s3}')

    def test_s3_client_creation(self):
        self.stdout.write('\n2. S3クライアントの作成テスト...')
        
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            self.stdout.write('  ✓ S3クライアントの作成に成功しました')
            return s3_client
        except NoCredentialsError:
            self.stdout.write(
                self.style.ERROR('  ✗ AWS認証情報が見つかりません')
            )
            return None
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ✗ S3クライアントの作成に失敗しました: {e}')
            )
            return None

    def test_bucket_access(self, s3_client):
        self.stdout.write('\n3. バケットアクセステスト...')
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        
        try:
            # バケットの存在確認
            s3_client.head_bucket(Bucket=bucket_name)
            self.stdout.write(f'  ✓ バケット "{bucket_name}" にアクセスできました')
            
            # バケット内のオブジェクト一覧を取得（最大5件）
            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                MaxKeys=5
            )
            
            if 'Contents' in response:
                self.stdout.write(f'  ✓ バケット内のオブジェクト数: {len(response["Contents"])}件（最大5件まで表示）')
                for obj in response['Contents']:
                    self.stdout.write(f'    - {obj["Key"]} ({obj["Size"]} bytes)')
            else:
                self.stdout.write('  ✓ バケットは空です')
                
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                self.stdout.write(
                    self.style.ERROR(f'  ✗ バケット "{bucket_name}" が見つかりません')
                )
            elif error_code == '403':
                self.stdout.write(
                    self.style.ERROR(f'  ✗ バケット "{bucket_name}" へのアクセス権限がありません')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ バケットアクセスエラー: {e}')
                )
            return False
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ✗ バケットアクセステストに失敗しました: {e}')
            )
            return False

    def test_file_upload(self, s3_client):
        self.stdout.write('\n4. ファイルアップロードテスト...')
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        test_key = f'test/connection_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        test_content = f'S3接続テスト - {datetime.now()}'
        
        try:
            # テンポラリファイルを作成
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
                temp_file.write(test_content)
                temp_file_path = temp_file.name
            
            # S3にアップロード
            s3_client.upload_file(temp_file_path, bucket_name, test_key)
            self.stdout.write(f'  ✓ テストファイルをアップロードしました: {test_key}')
            
            # アップロードしたファイルの確認
            response = s3_client.head_object(Bucket=bucket_name, Key=test_key)
            self.stdout.write(f'  ✓ アップロードファイルを確認しました（サイズ: {response["ContentLength"]} bytes）')
            
            # ファイルを削除（クリーンアップ）
            s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            self.stdout.write('  ✓ テストファイルを削除しました')
            
            # テンポラリファイルを削除
            os.unlink(temp_file_path)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ✗ ファイルアップロードテストに失敗しました: {e}')
            )
            # テンポラリファイルのクリーンアップ
            try:
                os.unlink(temp_file_path)
            except:
                pass