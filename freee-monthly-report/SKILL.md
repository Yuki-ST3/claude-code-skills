---
name: freee-monthly-report
description: freee会計の月次経費レポートを生成するスキル。合同会社近江エクスポートのfreeeから指定月の支出取引を取得し、勘定科目別集計と明細一覧をテキストファイルで出力する。ユーザーが「月次レポート」「経費レポート」などを要求したときに使用する。
---

# freee月次経費レポート生成スキル

## 環境
- `.env`: `/Users/ykmba/freee-receipt/.env`
- 会社: 合同会社近江エクスポート（company_id: 12500913）
- レシートデータ: `/tmp/receipts.pkl`（当月分の読み取りデータ、取引先名含む）
- 出力先: `~/Desktop/YYYY年M月_経費月次レポート.txt`

## 手順

### 1. 対象月を確認
ユーザーが月を指定していない場合は直前の月を対象とする。

### 2. スクリプトを実行
`scripts/generate_report.py` を実行する：
```bash
cd /Users/ykmba/freee-receipt
python3 ~/.claude/skills/freee-monthly-report/scripts/generate_report.py YYYY-MM
```

### 3. 結果を報告
- 勘定科目別集計（金額降順）
- 件数と合計金額
- 保存先パス

## 注意事項
- freeeのdeals APIは未登録取引先の`partner_name`を返さない。`/tmp/receipts.pkl`に当月の読み取りデータがある場合はそれを使用する。ない場合は取引先名を「不明」とする。
- アクセストークンが期限切れの場合は `python3 /Users/ykmba/freee-receipt/setup_token.py` を案内する。
