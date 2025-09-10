#!/usr/bin/env python3
"""
AWS環境変数の設定状況を確認するスクリプト
"""

import os
import sys


def check_aws_environment():
    """AWS環境変数の設定状況をチェック"""
    print("=== AWS環境変数チェック ===\n")
    
    # 必要な環境変数のリスト
    required_vars = [
        ('AWS_ACCESS_KEY_ID', 'AWSアクセスキーID'),
        ('AWS_SECRET_ACCESS_KEY', 'AWSシークレットアクセスキー'),
        ('AWS_STORAGE_BUCKET_NAME', 'S3バケット名'),
        ('AWS_S3_REGION_NAME', 'AWSリージョン'),
    ]
    
    all_set = True
    
    for var_name, description in required_vars:
        value = os.environ.get(var_name)
        
        if value:
            if 'SECRET' in var_name:
                # シークレットキーは一部のみ表示
                if len(value) > 8:
                    display_value = value[:4] + '***' + value[-4:]
                else:
                    display_value = '***'
            else:
                display_value = value
            
            print(f"✅ {var_name}")
            print(f"   {description}: {display_value}")
        else:
            print(f"❌ {var_name}")
            print(f"   {description}: 未設定")
            all_set = False
        
        print()
    
    # 現在の設定状況の要約
    if all_set:
        print("🎉 すべての環境変数が設定されています！")
        
        # Django設定の確認
        try:
            import django
            from django.conf import settings
            
            # Djangoの設定を確認
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'handball_video_analysis.settings')
            django.setup()
            
            use_s3 = getattr(settings, 'USE_S3', False)
            print(f"📊 Django USE_S3設定: {use_s3}")
            
            if use_s3:
                print("   → S3ストレージが有効になります")
            else:
                print("   → ローカルファイルストレージが使用されます")
                
        except ImportError:
            print("ℹ️  Django環境が利用できません（通常のPythonスクリプトとして実行中）")
        except Exception as e:
            print(f"⚠️  Django設定の確認中にエラーが発生: {e}")
            
    else:
        print("⚠️  一部の環境変数が未設定です")
        print("\n📋 設定方法:")
        print("1. 対話的設定:")
        print("   source setup_aws_env.sh  (macOS/Linux)")
        print("   setup_aws_env.bat        (Windows)")
        print("\n2. 手動設定:")
        print("   export AWS_ACCESS_KEY_ID='your_key'")
        print("   export AWS_SECRET_ACCESS_KEY='your_secret'")
        print("   export AWS_STORAGE_BUCKET_NAME='your_bucket'")
        print("   export AWS_S3_REGION_NAME='ap-northeast-1'")
        
    return all_set


def check_aws_cli():
    """AWS CLIの設定もチェック"""
    print("\n=== AWS CLI設定チェック ===")
    
    try:
        import subprocess
        result = subprocess.run(['aws', 'configure', 'list'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ AWS CLIが設定されています")
            print("設定内容:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print("❌ AWS CLIが設定されていません")
            
    except FileNotFoundError:
        print("❌ AWS CLIがインストールされていません")
    except subprocess.TimeoutExpired:
        print("⚠️  AWS CLI設定の確認がタイムアウトしました")
    except Exception as e:
        print(f"⚠️  AWS CLI設定の確認中にエラー: {e}")


def main():
    """メイン関数"""
    env_ok = check_aws_environment()
    check_aws_cli()
    
    print("\n" + "="*50)
    
    if env_ok:
        print("🚀 S3接続テストを実行できます:")
        print("   python3 test_s3_simple.py")
        print("   python manage.py test_s3_connection")
        sys.exit(0)
    else:
        print("⚠️  まず環境変数を設定してください")
        sys.exit(1)


if __name__ == "__main__":
    main()