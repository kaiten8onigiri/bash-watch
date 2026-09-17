# bash-watch 🏀

主要ブランドの日本向け公式バスケットボールシューズページを週1回確認し、公式ページに初掲載された商品だけを通知します。

## 通知条件

- Nike、adidas、Under Armour、ASICS、New Balanceの公式JPページを対象にします。
- URL内の商品コード（例: `IM4136-405`）を安定した商品識別子として使います。
- 過去に確認したことのない商品コードが公式ページへ掲載されたときだけ、商品名と公式リンクを1回通知します。
- 商品名、URLの表示名、価格、在庫、画像の変更では通知しません。
- 商品が一覧から一時的に消えて再掲載されても再通知しません。
- 初回実行では既存商品を基準として記録し、大量通知を防ぎます。

商品コードを公開しないサイトでは、追跡パラメータを除いた商品URLを識別子として使います。「正式公開」は設定済みの公式商品一覧で初めて確認できた時点を意味し、実店舗での発売開始や公式SNSだけの告知を判定するものではありません。

## 実行と状態保存

- GitHub Actionsで毎週月曜12:00 JSTごろに実行します（混雑時は遅延する場合があります）。
- 確認済み商品は専用の`state`ブランチへ追記保存します。商品が一覧から消えても履歴から削除しません。
- `main`ブランチは定期実行によって自動更新されません。
- 通知先: Discord / Slack / SMTPメール / 任意のJSON Webhook
- 1サイトが失敗しても残りを監視します。全サイトが失敗した場合のみ実行を失敗扱いにします。

## GitHubセットアップ

1. `Settings > Secrets and variables > Actions`へ通知先を登録します。Discordは`DISCORD_WEBHOOK_URL`です。
2. `Actions > Watch official basketball shoe releases > Run workflow`を開き、`main`、`notify_initial: false`で実行します。
3. 初回は現在の商品を記録するだけで、商品通知は送りません。

## ローカル実行

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
bash-watch --dry-run
bash-watch --notify
```

## 監視先とコンプライアンス

監視先は`config/sources.yml`に登録した公式ページだけです。ログイン、CAPTCHA、403、bot対策などのアクセス制限は回避しません。月次の`Monthly compliance source check`は法令ページとメーカーの`robots.txt`の変更を知らせますが、法的判断は行いません。禁止や制限が確認された場合は該当sourceを停止し、人が内容を確認してください。

PUMAはアクセス制限のため初期状態では無効です。New Balanceなど取得を拒否するサイトについても制限を回避しません。

## 開発

```bash
pytest
ruff check .
```

## License

MIT
