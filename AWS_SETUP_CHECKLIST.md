# AWS設定チェックリスト

## 📋 設定完了チェックリスト

このチェックリストを使用して、AWS環境の設定が完了していることを確認してください。

---

## ✅ 1. Amazon S3

### 1.1 S3バケット作成
- [ ] バケット名: `handball-video-analysis-bucket`
- [ ] リージョン: `ap-northeast-1` (東京)
- [ ] パブリックアクセスブロック: 有効
- [ ] バージョニング: 設定済み（推奨）
- [ ] 暗号化: 有効

### 1.2 バケット構造確認
- [ ] `media/push_notification_icons/` フォルダ
- [ ] `test_uploads/` フォルダ（テスト用）

### 1.3 動作確認
```bash
# テスト実行
python3 test_s3_simple.py
```
- [ ] ✅ S3接続テスト成功
- [ ] ✅ ファイルアップロード成功
- [ ] ✅ ファイル一覧取得成功

---

## ✅ 2. Amazon SQS

### 2.1 FIFO キュー作成
- [ ] キュー名: `handball-push-notifications.fifo`
- [ ] タイプ: FIFO
- [ ] 可視性タイムアウト: 30秒
- [ ] メッセージ保持期間: 4日
- [ ] コンテンツベース重複排除: 有効

### 2.2 アクセスポリシー設定
- [ ] EventBridge Scheduler からのアクセス許可
- [ ] `sqs:SendMessage` 権限設定

### 2.3 動作確認
```bash
# AWS CLI での確認
aws sqs list-queues --queue-name-prefix handball-push-notifications
```
- [ ] ✅ キューが表示される
- [ ] ✅ ARNが正しい

---

## ✅ 3. Amazon EventBridge Scheduler

### 3.1 IAM サービスロール作成
- [ ] ロール名: `EventBridgeSchedulerRole`
- [ ] 信頼されたエンティティ: `scheduler.amazonaws.com`
- [ ] 権限: SQSへの `SendMessage`

### 3.2 権限確認
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Resource": "arn:aws:sqs:ap-northeast-1:YOUR_ACCOUNT_ID:handball-push-notifications.fifo"
    }
  ]
}
```
- [ ] ✅ 権限ポリシー設定済み
- [ ] ✅ 信頼関係設定済み

### 3.3 動作確認
```bash
# テスト実行
python3 test_eventbridge_scheduler.py
```
- [ ] ✅ EventBridge設定確認成功
- [ ] ✅ スケジュール作成テスト成功
- [ ] ✅ スケジュール削除テスト成功

---

## ✅ 4. IAM ユーザー・権限

### 4.1 アプリケーション用IAMユーザー
- [ ] IAMユーザー作成済み
- [ ] アクセスキー作成済み
- [ ] シークレットキー安全に保管済み

### 4.2 必要な権限
- [ ] S3 権限: `GetObject`, `PutObject`, `DeleteObject`, `ListBucket`
- [ ] EventBridge Scheduler 権限: `CreateSchedule`, `DeleteSchedule`, `GetSchedule`
- [ ] IAM 権限: `PassRole` (EventBridgeSchedulerRoleに対して)

### 4.3 権限テスト
```bash
# 権限確認
aws sts get-caller-identity
```
- [ ] ✅ 認証情報が正しい
- [ ] ✅ 必要な権限が付与されている

---

## ✅ 5. 環境変数設定

### 5.1 必要な環境変数
```env
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_STORAGE_BUCKET_NAME=handball-video-analysis-bucket
AWS_S3_REGION_NAME=ap-northeast-1
AWS_EVENTBRIDGE_SCHEDULER_ROLE_ARN=arn:aws:iam::YOUR_ACCOUNT_ID:role/EventBridgeSchedulerRole
AWS_SQS_QUEUE_ARN=arn:aws:sqs:ap-northeast-1:YOUR_ACCOUNT_ID:handball-push-notifications.fifo
AWS_SQS_MESSAGE_GROUP_ID=notice-push-notifications
```

### 5.2 設定確認
```bash
# 環境変数確認
python3 check_aws_env.py
```
- [ ] ✅ すべての環境変数が設定済み
- [ ] ✅ 値が正しい

---

## ✅ 6. アプリケーション動作確認

### 6.1 基本機能テスト
```bash
# S3接続テスト
python3 test_s3_simple.py
```
- [ ] ✅ S3接続成功

```bash
# EventBridge テスト
python3 test_eventbridge_scheduler.py
```
- [ ] ✅ EventBridge設定確認成功

### 6.2 統合テスト
```bash
# 管理画面でのテスト
python3 quick_admin_test.py
```
- [ ] ✅ Django管理画面アクセス可能
- [ ] ✅ お知らせ作成機能動作
- [ ] ✅ 画像アップロード機能動作

### 6.3 プッシュ通知スケジュール機能
- [ ] ✅ お知らせ作成時にプッシュ通知予定日時設定可能
- [ ] ✅ 保存時にEventBridgeスケジュール作成成功
- [ ] ✅ エラー時にトランザクションロールバック動作

---

## ✅ 7. セキュリティチェック

### 7.1 アクセス制御
- [ ] 最小権限の原則に従った権限設定
- [ ] 不要な権限は付与していない
- [ ] アクセスキーは安全に管理

### 7.2 データ保護
- [ ] S3バケットの暗号化有効
- [ ] パブリックアクセスブロック有効
- [ ] HTTPS通信の使用

### 7.3 監視設定（推奨）
- [ ] CloudWatch でメトリクス監視
- [ ] コスト異常検知設定
- [ ] CloudTrail でAPI呼び出しログ記録

---

## ✅ 8. 本番環境準備

### 8.1 環境分離
- [ ] 開発環境と本番環境の分離
- [ ] 環境別の設定ファイル準備
- [ ] 環境変数の適切な管理

### 8.2 バックアップ・災害復旧
- [ ] S3バケットのバージョニング有効
- [ ] 重要データの定期バックアップ設定
- [ ] 災害復旧手順の文書化

### 8.3 運用準備
- [ ] 監視・アラート設定
- [ ] ログ収集・分析設定
- [ ] 運用手順書作成

---

## 🚨 トラブルシューティング

### よくある問題と解決方法

| 問題 | チェック項目 | 解決方法 |
|------|-------------|----------|
| S3接続エラー | ✅ バケット名<br>✅ リージョン<br>✅ 認証情報 | 設定値を再確認 |
| EventBridge作成失敗 | ✅ IAMロールARN<br>✅ SQSキューARN<br>✅ 権限設定 | ARNと権限を再確認 |
| 権限エラー | ✅ IAMポリシー<br>✅ 信頼関係<br>✅ リソースARN | 権限設定を見直し |
| 環境変数エラー | ✅ .envファイル<br>✅ 変数名<br>✅ 値の形式 | 環境変数を再設定 |

---

## 📞 サポート

### ヘルプが必要な場合

1. **ドキュメント確認**: `AWS_INFRASTRUCTURE_SETUP.md`
2. **テストスクリプト実行**: 各種テストスクリプトで問題箇所を特定
3. **AWS公式ドキュメント**: 各サービスの詳細設定方法を確認
4. **CloudWatch Logs**: エラーの詳細情報を確認

### 緊急時の連絡先

- AWS サポート（有料プラン加入時）
- 社内インフラチーム
- プロジェクト管理者

---

## ✅ 最終確認

すべてのチェック項目が完了したら、以下の統合テストを実行してください：

```bash
# 全体テスト実行
python3 check_aws_env.py && \
python3 test_s3_simple.py && \
python3 test_eventbridge_scheduler.py && \
echo "🎉 AWS環境設定完了！"
```

**期待される結果:**
- ✅ すべてのテストが成功
- ✅ エラーメッセージなし
- ✅ 「🎉 AWS環境設定完了！」が表示される

これですべての設定が完了です！