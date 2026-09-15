# セットアップと運用

## 1. Discord通知先を登録

Discordの「#バッシュ情報」でWebhookを作成し、GitHubの
`Settings > Secrets and variables > Actions` にRepository secretとして登録します。

- Name: `DISCORD_WEBHOOK_URL`
- Secret: DiscordでコピーしたWebhook URL

Webhook URLはチャット、Issue、ログ、ソースコードへ貼らないでください。

## 2. 初回実行

`Actions > Watch official basketball shoe releases > Run workflow` を開き、
ブランチを`main`、`notify_initial`をオフにして実行します。初回は現在の商品を
比較基準として保存するため、商品通知は送りません。

次に`Actions > Monthly compliance source check > Run workflow`を実行します。
初回の法令・robots.txt比較基準が作成され、Discordへ完了通知が届きます。

## 3. 定期実行

- 商品監視: 毎日12:00 JSTごろ
- コンプライアンス変更確認: 毎月1日12:30 JSTごろ

GitHub Actionsの混雑により遅延する場合があります。

## 4. コンプライアンス通知への対応

月次通知で変更または取得失敗が報告された場合、リンク先を人が確認します。
自動取得が禁止された場合や403・CAPTCHA・ログイン要求が発生した場合は、
アクセス制限を回避せず、`config/sources.yml`の該当sourceを無効化します。
法的判断が難しい場合は法務担当者または弁護士へ確認してください。
