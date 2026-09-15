# bash-watch 🏀

主要ブランドの**日本向け公式バスケットボールシューズページ**を定期監視し、
新商品・価格・在庫表示の変化を通知する小さな監視システムです。

## 対応範囲

- 初期設定: Nike、adidas、Under Armour、ASICS、New Balance の公式JPページ
- PUMA: 設定例は同梱（bot対策で403になるため初期状態では無効）
- 通知: Discord / Slack / SMTPメール / 任意のJSON Webhook
- 実行: GitHub Actions（毎日12:00 JST）またはローカルcron
- 重複排除: `data/state.json` に既知商品の状態を保存
- 変更がない実行ではstateを更新せず、botの空コミットを作りません
- 障害分離: 1サイトが失敗しても残りを監視し、失敗サイトの既知状態は保持

「あらゆるサイト」を自動発見して完全監視するものではありません。公式ドメインを
`config/sources.yml` で明示的に許可するため、誤報や非公式リークを抑える設計です。

## 最短セットアップ（GitHub）

1. このリポジトリをGitHubへpushします。
2. `Settings > Secrets and variables > Actions` で通知先を1つ以上登録します。
   Discordなら `DISCORD_WEBHOOK_URL`、Slackなら `SLACK_WEBHOOK_URL` です。
3. `Actions > Watch official basketball shoe releases > Run workflow` を1回実行します。
   初回は現在の商品を基準値として保存し、通知しません。
4. 以降は毎日12:00 JSTごろに自動確認します（GitHub側の都合で遅延する場合があります）。

1日1回なら月約30回です。また、各ジョブは5分で強制終了するため、障害時に
Actionsの実行時間を際限なく消費しません。請求を確実に防ぎたい場合は、GitHubの
Billing設定でActionsの予算を設定し、上限到達時に利用を停止する設定も有効にしてください。

メールの場合は `.env.example` にある `SMTP_*` と `EMAIL_*` をSecretsへ登録してください。

## ローカル実行

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'

# 書き込まず抽出結果だけ確認
bash-watch --dry-run

# 状態を保存して、2回目以降の更新を設定済み通知先へ送信
bash-watch --notify
```

## 監視先の追加

`config/sources.yml` に公式商品一覧ページを追加します。

```yaml
- name: Example Official JP
  url: https://example.jp/basketball/shoes
  include_url_regex: "/products/"
  exclude_title_regex: "画像|お気に入り"
```

ページにschema.orgの `Product` JSON-LDがあれば自動利用します。ない場合は
`include_url_regex` に一致するリンクを商品として扱います。サイトのHTML変更で抽出が
0件になった場合は、Actionsログを確認して正規表現やURLを更新してください。

## 月次コンプライアンス変更チェック

`Monthly compliance source check`ワークフローが毎月1日12:30 JSTごろに実行されます。
e-Govの関連法令ページと各メーカーの`robots.txt`を前回の内容と比較し、変更または
取得失敗をDiscordへ通知します。初回は比較基準を作成します。

これは変更の検出だけを自動化するもので、法的判断を行う機能ではありません。通知を
受けたら規約・法令本文を人が確認してください。自動取得が禁止された場合やアクセス
制限が設けられた場合は、回避せず該当sourceを無効化します。安定した公式利用規約URLが
判明した場合は`config/compliance_urls.yml`へ追加してください。

初期設定と運用手順は[SETUP.md](SETUP.md)、変更内容は
[RELEASE_NOTES.md](RELEASE_NOTES.md)にまとめています。

## 運用上の限界

- ブランド側がページ公開前にSNSだけで告知した情報は、この初期設定では対象外です。
- ログイン必須、bot対策、地域制限、完全なクライアント描画には追加アダプターが必要です。
- 商品抽出が0件なら成功扱いにせず、既知状態を保持して警告します。
- GitHub Actionsのcronは厳密なリアルタイムではなく、混雑時に遅れます。
- 利用規約とrobots.txtを尊重し、監視頻度を過度に上げないでください。

速報性をさらに上げる場合は、各ブランドの公式ニュースルーム/RSS/メールマガジンと、
公式SNS APIを別ソースとして追加するのが現実的です。

## 開発

```bash
pytest
ruff check .
```

## License

MIT
