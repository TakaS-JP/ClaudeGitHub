# Email Management AI Agent

Gmail受信トレイを自律的に処理するAIエージェント。
**Claude claude-opus-4-6** (Anthropic) と **Gmail API** を使用し、メールの分類・整理・返信下書き作成を自動化します。

## 機能

| 機能 | 詳細 |
|------|------|
| **メール分類** | 仕事/個人/重要/削除/返信必要など8カテゴリに自動分類 |
| **ラベル整理** | `Work` / `Personal` / `Important` / `Needs Reply` ラベルを自動付与 |
| **添付ファイル保存** | カテゴリ別ディレクトリに自動ダウンロード・保存 |
| **返信下書き作成** | 返信が必要なメールに対してAIが下書きを自動生成 |
| **削除** | 不要メールをゴミ箱へ移動（スパムは完全削除も可） |

## セットアップ

### 1. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 2. Google Cloud Console での設定

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. **Gmail API** を有効化
3. **OAuth 2.0 クライアント ID** を作成（アプリケーションの種類: デスクトップ）
4. `credentials.json` をダウンロードしてプロジェクトルートに配置

### 3. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集して以下を設定:

```env
ANTHROPIC_API_KEY=sk-ant-...        # Anthropic APIキー
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
MAX_EMAILS_PER_RUN=30
MAX_AGENT_TURNS=60
ATTACHMENT_BASE_DIR=attachments
LOG_LEVEL=INFO
```

### 4. 初回認証

初回実行時にブラウザが開きGoogleアカウントの認証を求められます。
認証後、`token.json` が自動生成され、次回以降はブラウザ不要です。

## 実行

```bash
# 未読メールを最大30件処理
python main.py

# 処理件数を指定
python main.py --max-emails 10

# カスタムクエリで絞り込み
python main.py --query "is:unread from:important@example.com"

# ドライラン（変更なし・リスト確認のみ）
python main.py --dry-run
```

## プロジェクト構成

```
ClaudeGitHub/
├── main.py                    # エントリーポイント
├── requirements.txt
├── .env.example
├── config/
│   └── settings.py            # 設定・カテゴリ定義
├── auth/
│   └── gmail_auth.py          # OAuth2認証
├── gmail/
│   ├── client.py              # Gmail APIラッパー
│   └── models.py              # データクラス
├── agent/
│   ├── tools.py               # Claudeに渡すツール定義（10種）
│   ├── tool_handlers.py       # ツール実装・セッション状態管理
│   └── loop.py                # メインエージェントループ
├── storage/
│   └── attachment_store.py    # 添付ファイル保存
└── utils/
    └── logger.py              # ログ設定
```

## メール分類カテゴリ

| カテゴリ | 説明 | アクション |
|----------|------|-----------|
| `delete` | 自動通知・期限切れプロモ | ゴミ箱へ移動 |
| `spam` | フィッシング・迷惑メール | 完全削除 |
| `save-work` | 業務・請求書・クライアント | `Work` ラベル + 添付保存 |
| `save-personal` | 友人・家族 | `Personal` ラベル + 添付保存 |
| `save-important` | 法的・金融・行政 | `Important` ラベル + 添付保存 |
| `needs-reply` | 返信が必要なもの | `Needs Reply` ラベル + 返信下書き作成 |
| `newsletter-unsubscribe` | ニュースレター | 削除 + 記録 |
| `skip` | 判断不能 | 人間確認用フラグ |

## 添付ファイルの保存先

```
attachments/
├── work/         {email_id}/{filename}
├── personal/     {email_id}/{filename}
├── important/    {email_id}/{filename}
└── other/        {email_id}/{filename}
```

## 注意事項

- `credentials.json` と `token.json` は **`.gitignore` に含まれています**。絶対にコミットしないでください。
- エージェントはメールを**ゴミ箱へ移動**します（デフォルト）。完全削除はスパム確認済みのメールのみです。
- 初回実行前に `--dry-run` で動作確認を推奨します。
