#!/usr/bin/env python3
"""
S3への画像アップロードテストスクリプト
実際に画像ファイルを作成してS3にアップロードし、確認します
"""

import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import sys
from PIL import Image, ImageDraw, ImageFont
import tempfile
from datetime import datetime


def load_env_file(env_path='.env'):
    """
    .envファイルを読み込んで環境変数に設定する
    """
    if not os.path.exists(env_path):
        print(f"⚠️  {env_path} ファイルが見つかりません")
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
        
        print(f"✅ {env_path} ファイルを読み込みました")
        return True
        
    except Exception as e:
        print(f"❌ {env_path} ファイルの読み込みに失敗: {e}")
        return False


def create_test_image(width=512, height=512):
    """
    テスト用の画像を作成する
    """
    print("📸 テスト画像を作成中...")
    
    # 新しい画像を作成（RGB、白背景）
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 背景にグラデーションを追加
    for y in range(height):
        color_value = int(255 * (1 - y / height))
        color = (color_value, color_value + 50, 255)
        draw.line([(0, y), (width, y)], fill=color)
    
    # テキストを追加
    try:
        # デフォルトフォントを使用
        font_size = 40
        # システムフォントを試す
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # 現在時刻を追加
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text_lines = [
        "S3 Upload Test",
        "Handball Video Analysis",
        timestamp
    ]
    
    y_offset = height // 4
    for line in text_lines:
        # テキストのサイズを取得
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 中央に配置
        x = (width - text_width) // 2
        
        # 影を追加
        draw.text((x + 2, y_offset + 2), line, font=font, fill='gray')
        # メインテキスト
        draw.text((x, y_offset), line, font=font, fill='black')
        
        y_offset += text_height + 20
    
    # 枠線を追加
    draw.rectangle([10, 10, width-10, height-10], outline='black', width=3)
    
    print(f"✅ テスト画像を作成しました ({width}x{height})")
    return image


def upload_image_to_s3(image, filename):
    """
    画像をS3にアップロードする
    """
    print(f"☁️  S3に画像をアップロード中: {filename}")
    
    # 環境変数を取得
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    region_name = os.environ.get('AWS_S3_REGION_NAME', 'ap-northeast-1')
    
    if not aws_access_key_id or not aws_secret_access_key:
        print("❌ AWS認証情報が設定されていません")
        return False, None
    
    try:
        # S3クライアントを作成
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        
        # 一時ファイルに画像を保存
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            image.save(temp_file.name, 'PNG')
            temp_file_path = temp_file.name
        
        # S3にアップロード
        s3_key = f'test_uploads/{filename}'
        s3_client.upload_file(
            temp_file_path, 
            bucket_name, 
            s3_key,
            ExtraArgs={
                'ContentType': 'image/png'
                # ACLは使用しない（バケットポリシーで制御）
            }
        )
        
        # 一時ファイルを削除
        os.unlink(temp_file_path)
        
        # アップロードされたファイルのURLを生成
        file_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{s3_key}"
        
        print(f"✅ アップロード成功!")
        print(f"   S3キー: {s3_key}")
        print(f"   URL: {file_url}")
        
        return True, file_url
        
    except ClientError as e:
        print(f"❌ S3アップロードエラー: {e}")
        return False, None
    except Exception as e:
        print(f"❌ アップロードに失敗: {e}")
        return False, None


def verify_upload(s3_key):
    """
    アップロードされたファイルを確認する
    """
    print(f"🔍 アップロードされたファイルを確認中: {s3_key}")
    
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    region_name = os.environ.get('AWS_S3_REGION_NAME', 'ap-northeast-1')
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        
        # ファイル情報を取得
        response = s3_client.head_object(Bucket=bucket_name, Key=s3_key)
        
        print("✅ ファイル確認成功!")
        print(f"   サイズ: {response['ContentLength']:,} bytes")
        print(f"   Content-Type: {response.get('ContentType', 'unknown')}")
        print(f"   最終更新: {response['LastModified']}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print("❌ ファイルが見つかりません")
        else:
            print(f"❌ ファイル確認エラー: {e}")
        return False
    except Exception as e:
        print(f"❌ ファイル確認に失敗: {e}")
        return False


def list_uploaded_files():
    """
    test_uploads/フォルダ内のファイル一覧を表示
    """
    print("📂 test_uploads/ フォルダの内容:")
    
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    region_name = os.environ.get('AWS_S3_REGION_NAME', 'ap-northeast-1')
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix='test_uploads/'
        )
        
        if 'Contents' in response:
            print(f"   {len(response['Contents'])}個のファイルが見つかりました:")
            for obj in response['Contents']:
                size_kb = obj['Size'] / 1024
                print(f"   - {obj['Key']} ({size_kb:.1f} KB, {obj['LastModified']})")
        else:
            print("   フォルダは空です")
            
    except Exception as e:
        print(f"❌ フォルダ内容の取得に失敗: {e}")


def main():
    """
    メイン関数
    """
    print("=== S3画像アップロードテスト ===\n")
    
    # .envファイルを読み込み
    if not load_env_file():
        return False
    
    # テスト画像を作成
    test_image = create_test_image()
    
    # ファイル名を生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_image_{timestamp}.png"
    
    # S3にアップロード
    success, file_url = upload_image_to_s3(test_image, filename)
    
    if success:
        # アップロードされたファイルを確認
        s3_key = f'test_uploads/{filename}'
        verify_upload(s3_key)
        
        print(f"\n🌐 ブラウザでアクセス可能なURL:")
        print(f"   {file_url}")
        
        # フォルダ内容を表示
        print()
        list_uploaded_files()
        
        print(f"\n🎉 画像アップロードテスト完了!")
        print(f"   ファイル名: {filename}")
        print(f"   S3キー: {s3_key}")
        
        return True
    else:
        print("❌ 画像アップロードテストに失敗しました")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)