---
name: youtube-summary
description: YouTubeリンクからトランスクリプトを取得し、動画の内容をわかりやすく日本語で要約する。ユーザーがYouTube URLを提供したときに使用。
argument-hint: "[youtube-url]"
---

# YouTube動画 トランスクリプト取得・要約スキル

対象URL: $ARGUMENTS

## ステップ1: 動画IDを抽出してトランスクリプトを取得

URLから動画IDを特定する:
- `https://www.youtube.com/watch?v=XXXX` → ID は `XXXX`
- `https://youtu.be/XXXX` → ID は `XXXX`
- `https://www.youtube.com/shorts/XXXX` → ID は `XXXX`

以下のPythonスクリプトの `VIDEO_ID_HERE` を実際の動画IDに置き換えて `Bash` ツールで実行する:

```
python -c "
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from youtube_transcript_api import YouTubeTranscriptApi

api = YouTubeTranscriptApi()
video_id = 'VIDEO_ID_HERE'

try:
    transcript_list = api.list(video_id)
    transcript = None
    try:
        transcript = transcript_list.find_transcript(['ja'])
    except:
        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            try:
                transcript = transcript_list.find_generated_transcript(['ja', 'en'])
            except:
                # 最初に見つかるものを使用
                for t in transcript_list:
                    transcript = t
                    break

    entries = transcript.fetch()
    full_text = ' '.join([e.text for e in entries])

    # 長すぎる場合は最初の20000文字に制限
    if len(full_text) > 20000:
        full_text = full_text[:20000] + '...(以下省略)'

    print('LANGUAGE:', transcript.language)
    print('CHARS:', len(full_text))
    print('---TRANSCRIPT START---')
    print(full_text)
    print('---TRANSCRIPT END---')

except Exception as e:
    print('ERROR:', type(e).__name__, str(e))
"
```

## ステップ2: 取得失敗時のフォールバック

`youtube_transcript_api` でエラーになった場合（字幕なし動画など）:
1. `WebFetch` で `https://www.youtube.com/watch?v=VIDEO_ID` を取得
2. ページ内のタイトル・説明文・概要欄から内容を把握して要約する

## ステップ3: 取得した内容を要約する

取得したトランスクリプト（または説明文）をもとに、**必ず日本語**で以下の構成でわかりやすく要約する:

---

## 📺 動画タイトル
（動画タイトルをここに記載）

## 🎯 概要（ひとことまとめ）
（1〜2文で動画全体の内容を端的に表す）

## 📌 主なポイント
（箇条書きで5〜8個、重要なポイントを列挙）

## 🔍 詳細まとめ
（話題の流れに沿って内容を詳しく説明。400〜700字程度）

## 💡 重要な学び・まとめ
（視聴者が持ち帰るべき最重要メッセージを2〜3点）

---

### 注意事項
- トランスクリプトが英語などの場合も、要約は **日本語** で作成する
- 専門用語が出てきた場合は簡単な補足を添える
- 動画の長さ・内容の密度に応じて要約の詳しさを調整する
