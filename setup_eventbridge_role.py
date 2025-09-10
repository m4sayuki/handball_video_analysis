#!/usr/bin/env python3
"""
EventBridge Scheduler用IAMロール設定支援スクリプト
"""

import boto3
import json
import sys
import os
from pathlib import Path
from botocore.exceptions import ClientError

# .envファイルを読み込み
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / '.env')
    print("✅ .envファイルを読み込みました")
except ImportError:
    print("⚠️ python-dotenvがインストールされていません。環境変数から直接読み込みます")
except Exception as e:
    print(f"⚠️ .envファイルの読み込みでエラー: {e}")

# 環境変数の確認
print("\n🔧 AWS認証情報確認:")
aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
aws_region = os.environ.get('AWS_S3_REGION_NAME', 'ap-northeast-1')

if aws_access_key:
    print(f"   ✅ AWS_ACCESS_KEY_ID: {aws_access_key}")
else:
    print("   ❌ AWS_ACCESS_KEY_ID: 未設定")

if aws_secret_key:
    print(f"   ✅ AWS_SECRET_ACCESS_KEY: {'*' * len(aws_secret_key)}")
else:
    print("   ❌ AWS_SECRET_ACCESS_KEY: 未設定")

print(f"   ✅ AWS_S3_REGION_NAME: {aws_region}")

if not aws_access_key or not aws_secret_key:
    print("\n❌ AWS認証情報が設定されていません")
    print("`.env`ファイルを作成して以下を設定してください:")
    print("AWS_ACCESS_KEY_ID=your_access_key_here")
    print("AWS_SECRET_ACCESS_KEY=your_secret_key_here")
    print("AWS_S3_REGION_NAME=ap-northeast-1")
    print("\nまたは、環境変数として設定してください")
    sys.exit(1)


def get_aws_account_id():
    """AWSアカウントIDを取得"""
    try:
        sts_client = boto3.client('sts')
        response = sts_client.get_caller_identity()
        return response['Account']
    except Exception as e:
        print(f"❌ AWSアカウントIDの取得に失敗: {e}")
        return None


def create_trust_policy():
    """EventBridge Scheduler用の信頼ポリシーを作成"""
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "scheduler.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }


def create_sqs_policy(account_id, queue_name="handball-push-notifications.fifo", region="ap-northeast-1"):
    """SQSアクセス用の権限ポリシーを作成"""
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "sqs:SendMessage"
                ],
                "Resource": f"arn:aws:sqs:{region}:{account_id}:{queue_name}"
            }
        ]
    }


def check_role_exists(iam_client, role_name):
    """IAMロールが存在するかチェック"""
    try:
        iam_client.get_role(RoleName=role_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            return False
        raise


def check_policy_exists(iam_client, policy_name, account_id):
    """IAMポリシーが存在するかチェック"""
    try:
        policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
        iam_client.get_policy(PolicyArn=policy_arn)
        return True, policy_arn
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            return False, policy_arn
        raise


def create_eventbridge_role():
    """EventBridge Scheduler用のIAMロールとポリシーを作成"""
    print("🔧 EventBridge Scheduler用IAMロール作成を開始します...\n")
    
    # AWSアカウントIDを取得
    account_id = get_aws_account_id()
    if not account_id:
        return False
    
    print(f"📋 AWSアカウントID: {account_id}")
    
    try:
        iam_client = boto3.client('iam')
        
        role_name = "EventBridgeSchedulerRole"
        policy_name = "EventBridgeSchedulerSQSPolicy"
        
        # 1. IAMロールの作成または確認
        print(f"\n1. IAMロール '{role_name}' の確認...")
        
        if check_role_exists(iam_client, role_name):
            print(f"   ✅ IAMロール '{role_name}' は既に存在します")
        else:
            print(f"   📝 IAMロール '{role_name}' を作成中...")
            trust_policy = create_trust_policy()
            
            response = iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='EventBridge SchedulerがSQSにメッセージを送信するためのロール'
            )
            print(f"   ✅ IAMロール '{role_name}' を作成しました")
        
        # 2. IAMポリシーの作成または確認
        print(f"\n2. IAMポリシー '{policy_name}' の確認...")
        
        policy_exists, policy_arn = check_policy_exists(iam_client, policy_name, account_id)
        
        if policy_exists:
            print(f"   ✅ IAMポリシー '{policy_name}' は既に存在します")
        else:
            print(f"   📝 IAMポリシー '{policy_name}' を作成中...")
            sqs_policy = create_sqs_policy(account_id)
            
            response = iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(sqs_policy),
                Description='EventBridge SchedulerがSQSにメッセージを送信するための権限'
            )
            policy_arn = response['Policy']['Arn']
            print(f"   ✅ IAMポリシー '{policy_name}' を作成しました")
        
        # 3. ポリシーをロールにアタッチ
        print(f"\n3. ポリシーのアタッチ確認...")
        
        try:
            # 既にアタッチされているポリシーを確認
            attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)
            policy_attached = any(
                policy['PolicyArn'] == policy_arn 
                for policy in attached_policies['AttachedPolicies']
            )
            
            if policy_attached:
                print(f"   ✅ ポリシーは既にロールにアタッチされています")
            else:
                iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
                print(f"   ✅ ポリシーをロールにアタッチしました")
        
        except Exception as e:
            print(f"   ⚠️ ポリシーアタッチの確認でエラー: {e}")
        
        # 4. 作成されたリソースの情報を表示
        role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
        sqs_queue_arn = f"arn:aws:sqs:ap-northeast-1:{account_id}:handball-push-notifications.fifo"
        
        print(f"\n🎉 EventBridge Scheduler用IAMロールの設定が完了しました！")
        print(f"\n📋 設定情報:")
        print(f"   IAMロール名: {role_name}")
        print(f"   IAMロールARN: {role_arn}")
        print(f"   IAMポリシー名: {policy_name}")
        print(f"   IAMポリシーARN: {policy_arn}")
        print(f"   SQSキューARN: {sqs_queue_arn}")
        
        print(f"\n🔧 環境変数設定:")
        print(f"   AWS_EVENTBRIDGE_SCHEDULER_ROLE_ARN={role_arn}")
        print(f"   AWS_SQS_QUEUE_ARN={sqs_queue_arn}")
        
        # .envファイルの更新を提案
        print(f"\n💡 .envファイルの更新:")
        print(f"   以下の行を .env ファイルに追加または更新してください:")
        print(f"   AWS_EVENTBRIDGE_SCHEDULER_ROLE_ARN={role_arn}")
        print(f"   AWS_SQS_QUEUE_ARN={sqs_queue_arn}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ AWS APIエラー ({error_code}): {error_message}")
        
        if error_code == 'AccessDenied':
            print(f"\n💡 解決方法:")
            print(f"   以下の権限が必要です:")
            print(f"   - iam:CreateRole")
            print(f"   - iam:CreatePolicy") 
            print(f"   - iam:AttachRolePolicy")
            print(f"   - iam:GetRole")
            print(f"   - iam:GetPolicy")
            print(f"   - iam:ListAttachedRolePolicies")
        
        return False
        
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {e}")
        return False


def check_existing_setup():
    """既存の設定をチェック"""
    print("🔍 既存のEventBridge設定をチェックします...\n")
    
    account_id = get_aws_account_id()
    if not account_id:
        return
    
    try:
        iam_client = boto3.client('iam')
        sqs_client = boto3.client('sqs')
        
        role_name = "EventBridgeSchedulerRole"
        policy_name = "EventBridgeSchedulerSQSPolicy"
        queue_name = "handball-push-notifications.fifo"
        
        # IAMロールの確認
        if check_role_exists(iam_client, role_name):
            role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
            print(f"✅ IAMロール: {role_arn}")
        else:
            print(f"❌ IAMロール '{role_name}' が見つかりません")
        
        # IAMポリシーの確認
        policy_exists, policy_arn = check_policy_exists(iam_client, policy_name, account_id)
        if policy_exists:
            print(f"✅ IAMポリシー: {policy_arn}")
        else:
            print(f"❌ IAMポリシー '{policy_name}' が見つかりません")
        
        # SQSキューの確認
        try:
            queues = sqs_client.list_queues(QueueNamePrefix=queue_name.replace('.fifo', ''))
            if 'QueueUrls' in queues and queues['QueueUrls']:
                queue_url = queues['QueueUrls'][0]
                queue_arn = f"arn:aws:sqs:ap-northeast-1:{account_id}:{queue_name}"
                print(f"✅ SQSキュー: {queue_arn}")
            else:
                print(f"❌ SQSキュー '{queue_name}' が見つかりません")
        except Exception as e:
            print(f"❌ SQSキューの確認でエラー: {e}")
        
    except Exception as e:
        print(f"❌ 設定チェックでエラー: {e}")


def main():
    """メイン関数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            success = create_eventbridge_role()
            sys.exit(0 if success else 1)
        elif command == "check":
            check_existing_setup()
        else:
            print("❌ 不明なコマンドです")
            print("使用方法:")
            print("  python3 setup_eventbridge_role.py create  # IAMロール・ポリシーを作成")
            print("  python3 setup_eventbridge_role.py check   # 既存設定を確認")
            sys.exit(1)
    else:
        print("🔧 EventBridge Scheduler IAMロール設定支援ツール")
        print("\n使用方法:")
        print("  python3 setup_eventbridge_role.py create  # IAMロール・ポリシーを作成")
        print("  python3 setup_eventbridge_role.py check   # 既存設定を確認")
        print("\n⚠️  注意:")
        print("  - AWS認証情報が設定されている必要があります")
        print("  - IAMの作成・変更権限が必要です")
        print("  - 作成前にSQS FIFOキューが存在している必要があります")


if __name__ == "__main__":
    main()