"""
お知らせ関連のサービスクラス
"""

import boto3
import json
import logging
from datetime import datetime
from django.conf import settings
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


class EventBridgeSchedulerService:
    """Amazon EventBridge Scheduler サービス"""
    
    def __init__(self):
        """EventBridge Scheduler クライアントを初期化"""
        self.client = None
        if self._is_aws_configured():
            self.client = boto3.client(
                'scheduler',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
    
    def _is_aws_configured(self):
        """AWS設定が有効かチェック"""
        return bool(
            settings.AWS_ACCESS_KEY_ID and 
            settings.AWS_SECRET_ACCESS_KEY and
            settings.AWS_EVENTBRIDGE_SCHEDULER_ROLE_ARN and
            settings.AWS_SQS_QUEUE_ARN
        )
    
    def create_push_notification_schedule(self, notice_id, scheduled_datetime):
        """
        プッシュ通知用のEventBridgeスケジュールを作成
        
        Args:
            notice_id (int): お知らせID
            scheduled_datetime (datetime): プッシュ通知予定日時
            
        Returns:
            tuple: (成功フラグ, エラーメッセージ)
        """
        if not self.client:
            logger.warning("EventBridge Scheduler が設定されていません")
            return False, "EventBridge Scheduler が設定されていません"
        
        if not scheduled_datetime:
            logger.warning(f"プッシュ通知予定日時が設定されていません (notice_id: {notice_id})")
            return False, "プッシュ通知予定日時が設定されていません"
        
        try:
            # スケジュール名を生成
            schedule_name = f"notice_{notice_id}"
            
            # スケジュール式を生成（at形式）
            # scheduled_datetimeをUTCに変換してISO形式で表現
            if scheduled_datetime.tzinfo is None:
                # ナイーブなdatetimeの場合、UTCとして扱う
                scheduled_utc = scheduled_datetime
            else:
                scheduled_utc = scheduled_datetime.utctimetuple()
                scheduled_utc = datetime(*scheduled_utc[:6])
            
            schedule_expression = f"at({scheduled_utc.strftime('%Y-%m-%dT%H:%M:%S')})"
            
            # SQSメッセージの内容
            message_body = {
                "notice_id": notice_id
            }
            
            # スケジュールを作成
            response = self.client.create_schedule(
                Name=schedule_name,
                ScheduleExpression=schedule_expression,
                ActionAfterCompletion='DELETE',  # 完了後削除
                Target={
                    'Arn': settings.AWS_SQS_QUEUE_ARN,
                    'RoleArn': settings.AWS_EVENTBRIDGE_SCHEDULER_ROLE_ARN,
                    'SqsParameters': {
                        'MessageGroupId': settings.AWS_SQS_MESSAGE_GROUP_ID
                    },
                    'Input': json.dumps(message_body)
                },
                FlexibleTimeWindow={
                    'Mode': 'OFF'  # 正確な時刻に実行
                }
            )
            
            logger.info(f"EventBridgeスケジュールを作成しました: {schedule_name}")
            logger.info(f"スケジュール式: {schedule_expression}")
            logger.info(f"レスポンス: {response}")
            
            return True, None
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"EventBridgeスケジュール作成エラー (notice_id: {notice_id}): {error_code} - {error_message}")
            return False, f"EventBridgeエラー: {error_message}"
            
        except Exception as e:
            logger.error(f"EventBridgeスケジュール作成で予期しないエラー (notice_id: {notice_id}): {str(e)}")
            return False, f"予期しないエラー: {str(e)}"
    
    def delete_push_notification_schedule(self, notice_id):
        """
        プッシュ通知用のEventBridgeスケジュールを削除
        
        Args:
            notice_id (int): お知らせID
            
        Returns:
            tuple: (成功フラグ, エラーメッセージ)
        """
        if not self.client:
            logger.warning("EventBridge Scheduler が設定されていません")
            return False, "EventBridge Scheduler が設定されていません"
        
        try:
            schedule_name = f"notice_{notice_id}"
            
            # スケジュールを削除
            self.client.delete_schedule(Name=schedule_name)
            
            logger.info(f"EventBridgeスケジュールを削除しました: {schedule_name}")
            return True, None
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'ResourceNotFoundException':
                # スケジュールが存在しない場合は成功とみなす
                logger.info(f"削除対象のスケジュールが存在しません: notice_{notice_id}")
                return True, None
            
            logger.error(f"EventBridgeスケジュール削除エラー (notice_id: {notice_id}): {error_code} - {error_message}")
            return False, f"EventBridgeエラー: {error_message}"
            
        except Exception as e:
            logger.error(f"EventBridgeスケジュール削除で予期しないエラー (notice_id: {notice_id}): {str(e)}")
            return False, f"予期しないエラー: {str(e)}"
    
    def get_schedule_info(self, notice_id):
        """
        スケジュール情報を取得
        
        Args:
            notice_id (int): お知らせID
            
        Returns:
            dict: スケジュール情報（存在しない場合はNone）
        """
        if not self.client:
            return None
        
        try:
            schedule_name = f"notice_{notice_id}"
            response = self.client.get_schedule(Name=schedule_name)
            return response
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return None
            logger.error(f"スケジュール情報取得エラー (notice_id: {notice_id}): {e}")
            return None
            
        except Exception as e:
            logger.error(f"スケジュール情報取得で予期しないエラー (notice_id: {notice_id}): {str(e)}")
            return None