# 商業登記電子証明書 発行申請書（下書き）

| ファイル | 内容 |
|---|---|
| `電子証明書発行申請書_下書き.docx` | 電子証明書発行申請書（1ページ目）、委任状（2ページ目）、記入要領・チェックリスト・手数料表・出典（3ページ目） |
| `build_application_form.js` | 上記 docx の生成スクリプト（docx npm パッケージ v9 を使用） |

## 位置づけ

法務省の案内では、電子証明書発行申請書は「商業登記電子認証ソフト」が
鍵ペアファイル・証明書発行申請ファイルと同時に PDF で出力します。
また法務局サイトには公式様式・記載例の PDF があります
（https://houmukyoku.moj.go.jp/homu/ELECTRON_13-1.html）。

本ドラフトは公式 PDF を取得できない環境で作成した**社内確認用**です。
窓口提出前に公式様式と照合してください。

## 再生成

```bash
npm install docx@9.7.1
node docs/commercial-registration-cert/build_application_form.js
```
