#!/usr/bin/env python3
"""
freee 月次経費レポート生成スクリプト
使い方: python3 generate_report.py YYYY-MM
"""

import os
import sys
import pickle
import requests
import calendar
from pathlib import Path
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv('/Users/ykmba/freee-receipt/.env')
FREEE_ACCESS_TOKEN = os.getenv('FREEE_ACCESS_TOKEN')
FREEE_COMPANY_ID = os.getenv('FREEE_COMPANY_ID')

def main():
    if len(sys.argv) < 2:
        # デフォルト: 先月
        from datetime import date, timedelta
        today = date.today()
        first = today.replace(day=1)
        last_month = first - timedelta(days=1)
        ym = last_month.strftime('%Y-%m')
    else:
        ym = sys.argv[1]

    year, month = int(ym.split('-')[0]), int(ym.split('-')[1])
    last_day = calendar.monthrange(year, month)[1]
    start_date = f'{year:04d}-{month:02d}-01'
    end_date = f'{year:04d}-{month:02d}-{last_day:02d}'
    label = f'{year}年{month}月'

    print(f'{label} 経費レポートを生成中...')

    headers = {'Authorization': f'Bearer {FREEE_ACCESS_TOKEN}', 'Content-Type': 'application/json'}

    # 勘定科目マップ
    r = requests.get('https://api.freee.co.jp/api/1/account_items', headers=headers,
                     params={'company_id': FREEE_COMPANY_ID})
    r.raise_for_status()
    account_map = {i['id']: i['name'] for i in r.json().get('account_items', [])}

    # freeeから取引取得
    r = requests.get('https://api.freee.co.jp/api/1/deals', headers=headers, params={
        'company_id': FREEE_COMPANY_ID, 'type': 'expense',
        'start_issue_date': start_date, 'end_issue_date': end_date, 'limit': 100,
    })
    r.raise_for_status()
    deals = r.json().get('deals', [])

    # freeeのdeals APIは未登録取引先名を返さないため、pickleデータで補完
    pkl_path = Path('/tmp/receipts.pkl')
    pkl_map = {}
    if pkl_path.exists():
        with open(pkl_path, 'rb') as f:
            receipts = pickle.load(f)
        for rec in receipts:
            pkl_map[rec['amount']] = rec.get('partner_name', '')

    rows = []
    for d in deals:
        partner = d.get('partner_name') or ''
        for det in d.get('details', []):
            amount = det.get('amount', 0)
            if not partner:
                partner = pkl_map.get(amount, '不明')
            rows.append({
                'date': d['issue_date'],
                'partner': partner,
                'desc': det.get('description', ''),
                'amount': amount,
                'category': account_map.get(det.get('account_item_id'), '不明'),
            })

    rows.sort(key=lambda x: x['date'])
    total = sum(r['amount'] for r in rows)

    by_cat = defaultdict(int)
    for r in rows:
        by_cat[r['category']] += r['amount']

    lines = []
    lines.append('=' * 56)
    lines.append(f'    {label} 経費月次レポート')
    lines.append('    合同会社近江エクスポート')
    lines.append('=' * 56)
    lines.append('')
    lines.append('【勘定科目別集計】')
    for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
        bar = '■' * (amt // 5000)
        lines.append(f'  {cat:<12} {amt:>10,}円  {bar}')
    lines.append('  ' + '-' * 34)
    lines.append(f'  合計         {total:>10,}円')
    lines.append('')
    lines.append('【明細一覧】')
    lines.append(f'{"日付":<12}{"取引先":<22}{"勘定科目":<12}{"金額":>9}')
    lines.append('-' * 58)
    for r in rows:
        lines.append(f'{r["date"]:<12}{r["partner"][:20]:<22}{r["category"]:<12}{r["amount"]:>7,}円')
    lines.append('')
    lines.append(f'  件数: {len(rows)}件   合計: {total:,}円')
    lines.append('=' * 56)

    text = '\n'.join(lines)
    print(text)

    out_path = Path.home() / 'Desktop' / f'{label}_経費月次レポート.txt'
    out_path.write_text(text, encoding='utf-8')
    print(f'\nデスクトップに保存しました: {out_path.name}')

if __name__ == '__main__':
    main()
