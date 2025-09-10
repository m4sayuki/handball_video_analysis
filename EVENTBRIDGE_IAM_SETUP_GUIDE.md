# EventBridge Scheduler IAM ロール設定ガイド

EventBridge SchedulerがSQSにメッセージを送信するために必要なIAMロールの作成手順を詳しく説明します。

## 🎯 なぜIAMロールが必要なのか？

EventBridge Schedulerは、スケジュール実行時に他のAWSサービス（SQS）にアクセスする必要があります。
そのために、EventBridge Schedulerが「引き受ける（Assume）」ことができるIAMロールを作成する必要があります。

---

## 📋 手順1: IAMロールの作成

### 1.1 AWS Management Consoleでの作成

1. **IAM コンソール**にアクセス
   ```
   https://console.aws.amazon.com/iam/
   ```

2. **左メニューから「ロール」をクリック**

3. **「ロールを作成」ボタンをクリック**

4. **信頼されたエンティティのタイプを選択**
   - ✅ **「AWSサービス」を選択**

5. **サービスの選択**
   - 検索ボックスに「EventBridge」と入力
   - ✅ **「EventBridge Scheduler」を選択**
   
   ※ 「EventBridge Scheduler」が見つからない場合は、「その他のAWSサービス」から「EventBridge」を選択

6. **「次へ」をクリック**

### 1.2 権限ポリシーの設定

7. **権限ポリシーの作成**
   - 「ポリシーを作成」をクリック（新しいタブが開きます）

8. **JSONタブを選択して以下を入力：**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sqs:SendMessage"
            ],
            "Resource": "arn:aws:sqs:ap-northeast-1:YOUR_ACCOUNT_ID:handball-push-notifications.fifo"
        }
    ]
}
```

⚠️ **重要**: `YOUR_ACCOUNT_ID` を実際のAWSアカウントIDに置き換えてください

9. **ポリシー名を入力**
   - 名前: `EventBridgeSchedulerSQSPolicy`
   - 説明: `EventBridge SchedulerがSQSにメッセージを送信するための権限`

10. **「ポリシーを作成」をクリック**

### 1.3 ロールの完成

11. **元のタブに戻り、権限ポリシーを選択**
    - 検索ボックスに「EventBridgeSchedulerSQSPolicy」と入力
    - ✅ 作成したポリシーを選択
    - 「次へ」をクリック

12. **ロール名と説明を入力**
    - ロール名: `EventBridgeSchedulerRole`
    - 説明: `EventBridge SchedulerがSQSにメッセージを送信するためのロール`

13. **「ロールを作成」をクリック**

---

## 🔍 手順2: AWSアカウントIDの確認方法

### 2.1 AWS CLIを使用する場合
```bash
aws sts get-caller-identity --query Account --output text
```

### 2.2 AWS Management Consoleを使用する場合
1. 右上のユーザー名をクリック
2. アカウントIDが表示されます（12桁の数字）

### 2.3 IAMコンソールから確認
1. IAMコンソール → ダッシュボード
2. 「アカウント情報」セクションにアカウントIDが表示

---

## 📝 手順3: 正しいARNの確認

### 3.1 作成したロールのARN確認

1. **IAMコンソール → ロール**
2. **「EventBridgeSchedulerRole」をクリック**
3. **「概要」タブでARNを確認**

正しいARNの形式：
```
arn:aws:iam::123456789012:role/EventBridgeSchedulerRole
```

### 3.2 SQSキューのARN確認

1. **SQSコンソール**にアクセス
2. **「handball-push-notifications.fifo」をクリック**
3. **「詳細」タブでARNを確認**

正しいARNの形式：
```
arn:aws:sqs:ap-northeast-1:123456789012:handball-push-notifications.fifo
```

---

## 🔧 手順4: AWS CLI を使用した作成（上級者向け）

### 4.1 信頼ポリシーファイルの作成

`trust-policy.json` を作成：
```json
{
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
```

### 4.2 権限ポリシーファイルの作成

`sqs-policy.json` を作成：
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sqs:SendMessage"
            ],
            "Resource": "arn:aws:sqs:ap-northeast-1:YOUR_ACCOUNT_ID:handball-push-notifications.fifo"
        }
    ]
}
```

### 4.3 AWS CLIコマンド実行

```bash
# アカウントIDを取得
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# SQSポリシーファイルを更新
sed -i "s/YOUR_ACCOUNT_ID/$ACCOUNT_ID/g" sqs-policy.json

# IAMロールを作成
aws iam create-role \
    --role-name EventBridgeSchedulerRole \
    --assume-role-policy-document file://trust-policy.json

# 権限ポリシーを作成
aws iam create-policy \
    --policy-name EventBridgeSchedulerSQSPolicy \
    --policy-document file://sqs-policy.json

# ポリシーをロールにアタッチ
aws iam attach-role-policy \
    --role-name EventBridgeSchedulerRole \
    --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/EventBridgeSchedulerSQSPolicy
```

---

## 🧪 手順5: 設定の確認

### 5.1 環境変数の設定

`.env` ファイルを更新：
```env
# 実際の値に置き換えてください
AWS_EVENTBRIDGE_SCHEDULER_ROLE_ARN=arn:aws:iam::123456789012:role/EventBridgeSchedulerRole
AWS_SQS_QUEUE_ARN=arn:aws:sqs:ap-northeast-1:123456789012:handball-push-notifications.fifo
```

### 5.2 テスト実行

```bash
python3 test_eventbridge_scheduler.py
```

期待される結果：
```
✅ 必要な設定がすべて揃っています
✅ EventBridge Scheduler クライアントが初期化されました
✅ テストスケジュールの作成に成功しました
✅ スケジュール情報の取得に成功しました
✅ テストスケジュールの削除に成功しました
🎉 EventBridge Scheduler の動作確認が完了しました！
```

---

## ❌ よくあるエラーと対処法

### エラー1: ValidationException (ARN形式エラー)
```
Value 'arn:aws:iam::account:role/EventBridgeSchedulerRole' at 'target.roleArn' 
failed to satisfy constraint
```

**原因**: ARNの `account` 部分が実際のアカウントIDになっていない

**解決**: 
1. AWSアカウントIDを確認
2. 環境変数を正しいARNに更新

### エラー2: AccessDenied
```
User: arn:aws:iam::123456789012:user/myuser is not authorized to perform: 
iam:PassRole on resource: arn:aws:iam::123456789012:role/EventBridgeSchedulerRole
```

**原因**: アプリケーション用IAMユーザーに `iam:PassRole` 権限がない

**解決**: アプリケーション用IAMユーザーに以下の権限を追加
```json
{
    "Effect": "Allow",
    "Action": "iam:PassRole",
    "Resource": "arn:aws:iam::123456789012:role/EventBridgeSchedulerRole"
}
```

### エラー3: ResourceNotFoundException
```
Role EventBridgeSchedulerRole does not exist
```

**原因**: IAMロールが作成されていない、または名前が間違っている

**解決**: 
1. IAMコンソールでロールの存在を確認
2. ロール名が正確であることを確認

---

## 🔐 セキュリティのベストプラクティス

### 1. 最小権限の原則
- 必要最小限の権限のみを付与
- 特定のSQSキューのみにアクセス許可

### 2. リソース制限
```json
{
    "Resource": [
        "arn:aws:sqs:ap-northeast-1:123456789012:handball-push-notifications.fifo"
    ]
}
```

### 3. 条件の追加（推奨）
```json
{
    "Effect": "Allow",
    "Action": "sqs:SendMessage",
    "Resource": "arn:aws:sqs:ap-northeast-1:123456789012:handball-push-notifications.fifo",
    "Condition": {
        "StringEquals": {
            "aws:SourceService": "scheduler.amazonaws.com"
        }
    }
}
```

---

## 📋 チェックリスト

- [ ] AWSアカウントIDを確認済み
- [ ] SQS FIFOキュー作成済み
- [ ] EventBridge Scheduler用IAMロール作成済み
- [ ] 信頼関係設定済み（scheduler.amazonaws.com）
- [ ] 権限ポリシー設定済み（sqs:SendMessage）
- [ ] 正しいARNを環境変数に設定済み
- [ ] アプリケーション用IAMユーザーにPassRole権限付与済み
- [ ] テストスクリプトで動作確認済み

すべてのチェック項目が完了したら、EventBridge Schedulerが正常に動作するはずです！