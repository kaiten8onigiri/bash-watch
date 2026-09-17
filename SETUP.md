# セットアップと運用

## Discord通知

Discordの「#バッシュ情報」でWebhookを作成し、GitHubの`Settings > Secrets and variables > Actions`へRepository secretとして登録します。

- Name: `DISCORD_WEBHOOK_URL`
- Secret: DiscordでコピーしたWebhook URL

Webhook URLはチャット、Issue、ログ、ソースコードへ貼らないでください。

## 初回実行

`Actions > Watch official basketball shoe releases > Run workflow`を開き、ブランチを`main`、`notify_initial`をオフにして実行します。現在の商品コードが`state`ブランチへ比較基準として保存され、商品通知は送られません。

次に`Monthly compliance source check`も手動実行し、法令・robots.txtの比較基準を作成します。

## 定期実行

- 商品監視: 毎週月曜12:00 JSTごろ
- コンプライアンス変更確認: 毎月1日12:30 JSTごろ

GitHub Actionsの混雑により遅延する場合があります。

## 通知の意味

商品通知は、公式商品一覧で過去に確認したことのない商品コードを検出したことを表します。価格・在庫・画像・商品名の変更では通知しません。厳密な発売日や実店舗の販売開始を保証するものではありません。

月次通知で変更・取得失敗が報告された場合はリンク先を人が確認します。自動取得が禁止された場合や403・CAPTCHA・ログイン要求が発生した場合はアクセス制限を回避せず、`config/sources.yml`の該当sourceを無効化します。法的判断が難しい場合は法務担当者または弁護士へ確認してください。
