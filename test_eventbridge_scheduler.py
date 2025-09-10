#!/usr/bin/env python3
"""
EventBridge Scheduler機能のテストスクリプト
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Django設定をセットアップ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'handball_video_analysis.settings')
django.setup()

from notices.services import EventBridgeSchedulerService
from django.conf import settings


def load_env_file(env_path='.env'):
    """
    .envファイルを読み込んで環境変数に設定する
    """
    if not os.path.exists(env_path):
        return False
    
    try:
        with open(env_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    if key not in os.environ:
                        os.environ[key] = value
        return True
        
    except Exception as e:
        print(f"❌ {env_path} ファイルの読み込みに失敗: {e}")
        return False


def check_eventbridge_settings():
    """
    EventBridge関連の設定を確認
    """
    print("🔧 EventBridge設定確認:")
    
    required_settings = [
        ('AWS_ACCESS_KEY_ID', getattr(settings, 'AWS_ACCESS_KEY_ID', None)),
        ('AWS_SECRET_ACCESS_KEY', getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)),
        ('AWS_S3_REGION_NAME', getattr(settings, 'AWS_S3_REGION_NAME', None)),
        ('AWS_EVENTBRIDGE_SCHEDULER_ROLE_ARN', getattr(settings, 'AWS_EVENTBRIDGE_SCHEDULER_ROLE_ARN', None)),
        ('AWS_SQS_QUEUE_ARN', getattr(settings, 'AWS_SQS_QUEUE_ARN', None)),
        ('AWS_SQS_MESSAGE_GROUP_ID', getattr(settings, 'AWS_SQS_MESSAGE_GROUP_ID', None)),
    ]
    
    all_configured = True
    
    for setting_name, setting_value in required_settings:
        if setting_value:
            if 'SECRET' in setting_name:
                display_value = '*' * min(len(str(setting_value)), 20)
            else:
                display_value = str(setting_value)
            print(f"   ✅ {setting_name}: {display_value}")
        else:
            print(f"   ❌ {setting_name}: 未設定")
            all_configured = False
    
    return all_configured


def test_eventbridge_service():
    """
    EventBridgeSchedulerServiceをテスト
    """
    print("\n🧪 EventBridgeSchedulerService テスト:")
    
    service = EventBridgeSchedulerService()
    
    if not service.client:
        print("   ⚠️ EventBridge Scheduler クライアントが初期化されていません")
        print("   環境変数が正しく設定されているか確認してください")
        return False
    
    print("   ✅ EventBridge Scheduler クライアントが初期化されました")
    
    # テスト用のスケジュール作成
    test_notice_id = 999999  # テスト用ID
    test_scheduled_time = datetime.now() + timedelta(minutes=5)  # 5分後
    
    print(f"\n📅 テストスケジュール作成:")
    print(f"   Notice ID: {test_notice_id}")
    print(f"   予定時刻: {test_scheduled_time}")
    
    # スケジュール作成テスト
    success, error_message = service.create_push_notification_schedule(
        test_notice_id, 
        test_scheduled_time
    )
    
    if success:
        print("   ✅ テストスケジュールの作成に成功しました")
        
        # スケジュール情報取得テスト
        schedule_info = service.get_schedule_info(test_notice_id)
        if schedule_info:
            print("   ✅ スケジュール情報の取得に成功しました")
            print(f"      スケジュール名: {schedule_info.get('Name')}")
            print(f"      スケジュール式: {schedule_info.get('ScheduleExpression')}")
            print(f"      状態: {schedule_info.get('State')}")
        else:
            print("   ⚠️ スケジュール情報の取得に失敗しました")
        
        # スケジュール削除テスト
        print(f"\n🗑️ テストスケジュール削除:")
        delete_success, delete_error = service.delete_push_notification_schedule(test_notice_id)
        
        if delete_success:
            print("   ✅ テストスケジュールの削除に成功しました")
        else:
            print(f"   ❌ テストスケジュールの削除に失敗しました: {delete_error}")
            
        return True
    else:
        print(f"   ❌ テストスケジュールの作成に失敗しました: {error_message}")
        return False


def show_usage_instructions():
    """
    使用方法の説明を表示
    """
    print(f"\n📋 EventBridge Scheduler 使用方法:")
    print(f"")
    print(f"1. AWS設定の準備:")
    print(f"   - EventBridge Scheduler用のIAMロールを作成")
    print(f"   - SQS FIFOキューを作成")
    print(f"   - 環境変数を設定")
    print(f"")
    print(f"2. 管理画面での使用:")
    print(f"   - お知らせ作成時にプッシュ通知予定日時を設定")
    print(f"   - 保存すると自動的にEventBridgeスケジュールが作成される")
    print(f"")
    print(f"3. スケジュール仕様:")
    print(f"   - スケジュール名: notice_[お知らせID]")
    print(f"   - 実行後自動削除")
    print(f"   - SQSにJSON形式でメッセージ送信")
    print(f"")
    print(f"4. 必要な権限:")
    print(f"   - scheduler:CreateSchedule")
    print(f"   - scheduler:DeleteSchedule")
    print(f"   - scheduler:GetSchedule")
    print(f"   - sqs:SendMessage")


def main():
    """
    メイン関数
    """
    print("=== EventBridge Scheduler テスト ===\n")
    
    # .envファイルを読み込み
    if load_env_file():
        print("✅ .envファイルを読み込みました\n")
    
    # 設定確認
    settings_ok = check_eventbridge_settings()
    
    if settings_ok:
        print("\n✅ 必要な設定がすべて揃っています")
        
        # EventBridgeサービステスト
        test_success = test_eventbridge_service()
        
        if test_success:
            print(f"\n🎉 EventBridge Scheduler の動作確認が完了しました！")
        else:
            print(f"\n⚠️ EventBridge Scheduler のテストで問題が発生しました")
            print(f"AWS設定やアクセス権限を確認してください")
    else:
        print(f"\n❌ 必要な設定が不足しています")
        print(f"env_example.txt を参考に環境変数を設定してください")
    
    # 使用方法の説明
    show_usage_instructions()


if __name__ == "__main__":
    main()