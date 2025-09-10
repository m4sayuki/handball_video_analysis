from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.conf import settings
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os


@staff_member_required
def test_s3_connection(request):
    """管理画面用S3接続テスト"""
    if request.method == 'POST':
        # Ajax リクエストでS3接続をテスト
        result = perform_s3_test()
        return JsonResponse(result)
    
    # GET リクエストではテストページを表示
    context = {
        'title': 'S3接続テスト',
        'use_s3': getattr(settings, 'USE_S3', False),
        'aws_bucket': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', ''),
        'aws_region': getattr(settings, 'AWS_S3_REGION_NAME', ''),
    }
    return render(request, 'admin/notices/s3_test.html', context)


def perform_s3_test():
    """実際のS3接続テストを実行"""
    results = []
    success = True
    
    # 1. 環境変数チェック
    results.append({
        'step': '環境変数の確認',
        'status': 'info',
        'message': f"USE_S3: {getattr(settings, 'USE_S3', False)}"
    })
    
    aws_vars = [
        ('AWS_ACCESS_KEY_ID', getattr(settings, 'AWS_ACCESS_KEY_ID', None)),
        ('AWS_SECRET_ACCESS_KEY', getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)),
        ('AWS_STORAGE_BUCKET_NAME', getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')),
        ('AWS_S3_REGION_NAME', getattr(settings, 'AWS_S3_REGION_NAME', '')),
    ]
    
    for var_name, var_value in aws_vars:
        if var_value:
            if 'SECRET' in var_name:
                display_value = '*' * min(len(str(var_value)), 20)
            else:
                display_value = str(var_value)
            results.append({
                'step': var_name,
                'status': 'success',
                'message': f"設定済み: {display_value}"
            })
        else:
            results.append({
                'step': var_name,
                'status': 'warning',
                'message': '未設定'
            })
            if var_name in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']:
                success = False
    
    if not success:
        results.append({
            'step': '結果',
            'status': 'error',
            'message': 'AWS認証情報が不足しています'
        })
        return {'success': False, 'results': results}
    
    # 2. S3クライアント作成テスト
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        results.append({
            'step': 'S3クライアント作成',
            'status': 'success',
            'message': 'S3クライアントの作成に成功しました'
        })
    except Exception as e:
        results.append({
            'step': 'S3クライアント作成',
            'status': 'error',
            'message': f'S3クライアントの作成に失敗: {str(e)}'
        })
        return {'success': False, 'results': results}
    
    # 3. バケットアクセステスト
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        results.append({
            'step': 'バケットアクセス',
            'status': 'success',
            'message': f'バケット "{bucket_name}" にアクセスできました'
        })
        
        # バケット内容の確認
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
        if 'Contents' in response:
            file_count = len(response['Contents'])
            results.append({
                'step': 'バケット内容確認',
                'status': 'info',
                'message': f'バケット内のファイル数: {file_count}件'
            })
        else:
            results.append({
                'step': 'バケット内容確認',
                'status': 'info',
                'message': 'バケットは空です'
            })
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            message = f'バケット "{bucket_name}" が見つかりません'
        elif error_code == '403':
            message = f'バケット "{bucket_name}" へのアクセス権限がありません'
        else:
            message = f'バケットアクセスエラー: {str(e)}'
        
        results.append({
            'step': 'バケットアクセス',
            'status': 'error',
            'message': message
        })
        return {'success': False, 'results': results}
    
    results.append({
        'step': '結果',
        'status': 'success',
        'message': 'S3接続テストが正常に完了しました'
    })
    
    return {'success': True, 'results': results}