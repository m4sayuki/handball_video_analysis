@echo off
setlocal enabledelayedexpansion

echo === AWS S3 環境変数設定 ===
echo.

REM 現在の設定を表示
echo 現在の設定:
if defined AWS_ACCESS_KEY_ID (
    echo AWS_ACCESS_KEY_ID: %AWS_ACCESS_KEY_ID%
) else (
    echo AWS_ACCESS_KEY_ID: 未設定
)
if defined AWS_SECRET_ACCESS_KEY (
    echo AWS_SECRET_ACCESS_KEY: 設定済み
) else (
    echo AWS_SECRET_ACCESS_KEY: 未設定
)
if defined AWS_STORAGE_BUCKET_NAME (
    echo AWS_STORAGE_BUCKET_NAME: %AWS_STORAGE_BUCKET_NAME%
) else (
    echo AWS_STORAGE_BUCKET_NAME: 未設定
)
if defined AWS_S3_REGION_NAME (
    echo AWS_S3_REGION_NAME: %AWS_S3_REGION_NAME%
) else (
    echo AWS_S3_REGION_NAME: 未設定
)
echo.

REM 対話的に環境変数を設定
set /p AWS_ACCESS_KEY_ID="AWS Access Key ID を入力してください: "

REM パスワード入力（表示されない）
echo AWS Secret Access Key を入力してください:
powershell -Command "$secureString = Read-Host -AsSecureString; $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureString); $plainText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR); [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR); Write-Output $plainText" > temp_secret.txt
set /p AWS_SECRET_ACCESS_KEY=<temp_secret.txt
del temp_secret.txt

set /p AWS_STORAGE_BUCKET_NAME="S3 バケット名を入力してください [handball-video-analysis-bucket]: "
if "!AWS_STORAGE_BUCKET_NAME!"=="" set AWS_STORAGE_BUCKET_NAME=handball-video-analysis-bucket

set /p AWS_S3_REGION_NAME="AWS リージョンを入力してください [ap-northeast-1]: "
if "!AWS_S3_REGION_NAME!"=="" set AWS_S3_REGION_NAME=ap-northeast-1

echo.
echo === 設定完了 ===
echo AWS_ACCESS_KEY_ID: %AWS_ACCESS_KEY_ID%
echo AWS_SECRET_ACCESS_KEY: ***
echo AWS_STORAGE_BUCKET_NAME: %AWS_STORAGE_BUCKET_NAME%
echo AWS_S3_REGION_NAME: %AWS_S3_REGION_NAME%
echo.

REM .envファイルの作成を提案
set /p SAVE_TO_ENV=".envファイルに設定を保存しますか？ (y/n) [n]: "
if /i "!SAVE_TO_ENV!"=="y" (
    echo # AWS S3 Settings > .env
    echo AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID% >> .env
    echo AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY% >> .env
    echo AWS_STORAGE_BUCKET_NAME=%AWS_STORAGE_BUCKET_NAME% >> .env
    echo AWS_S3_REGION_NAME=%AWS_S3_REGION_NAME% >> .env
    echo .envファイルに設定を保存しました
    
    REM .gitignoreに.envを追加
    if not exist .gitignore (
        echo .env > .gitignore
        echo .gitignoreを作成し、.envを追加しました
    ) else (
        findstr /c:".env" .gitignore >nul
        if errorlevel 1 (
            echo .env >> .gitignore
            echo .gitignoreに.envを追加しました
        )
    )
)

echo.
echo === 接続テスト ===
set /p RUN_TEST="S3接続テストを実行しますか？ (y/n) [y]: "
if "!RUN_TEST!"=="" set RUN_TEST=y
if /i "!RUN_TEST!"=="y" (
    if exist test_s3_simple.py (
        echo 簡単なS3接続テストを実行します...
        python test_s3_simple.py
    ) else (
        echo test_s3_simple.py が見つかりません
    )
)

echo.
echo 設定が完了しました！
echo この設定は現在のコマンドプロンプトセッションでのみ有効です。
echo 永続的に設定するには、システムの環境変数に追加してください。
pause