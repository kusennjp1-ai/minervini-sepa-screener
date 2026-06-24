# 📈 Mark Minervini SEPA Screener

Mark Minervini の SEPA 戦略に基づく**完全無料**の株式スクリーナー。
データは Yahoo Finance（`yfinance`）から取得し、API キー不要で動作します。

## 機能

- **Market 360** — S&P500 の移動平均整列・VIX・52週高値距離から市場環境を 0–100 でスコア化
- **Trend Template** — Minervini の 8 条件（SMA50/150/200 整列、52週レンジ位置など）
- **VCP 検出** — 収縮回数・出来高ドライアップ・タイトネス・ピボット距離から VCP スコアを算出
- **業種別 RS** — 同業種内での相対強度パーセンタイル
- **ファンダ** — 直近四半期の EPS / 売上 YoY 成長

## ローカル実行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud へのデプロイ

1. このリポジトリを GitHub に push
2. [share.streamlit.io](https://share.streamlit.io) → **New app**
3. リポジトリ / ブランチ `main` / メインファイル `app.py` を指定して **Deploy**

## 免責事項

本ツールは教育・研究目的です。投資判断は自己責任で行ってください。
