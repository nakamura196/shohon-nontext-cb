# shohon-nontext-cb — 古典籍諸本714冊の非本文コマ・検証サンプル検索（CollectionBuilder × IIIF × cjk_index）

[国文学研究資料館「国書データベース」](https://kokusho.nijl.ac.jp/)で公開されている日本の古典籍 5 作品（伊勢物語・古今和歌集・枕草子・竹取物語・徒然草）の諸本 714 冊・全 76,381 コマに「字の有無」「作品の本文か」「定規・カラーチャート・挿絵の有無」を付与したデータセット（Zenodo 公開版）の視覚的検証・探索用デジタルコレクションです。

---

## 特徴（CollectionBuilder 構築事例としての位置付け）

1. **IIIF Image API 直結（画像非保持・ノンカストディアル構成）**
   - リポジトリ内に画像ファイルを一切保持せず、データセット（`canvases.tsv`）に記録された国書データベースの IIIF Image API URL からサムネイル（`image_thumb`：幅 400px）および拡大画像（`image_small`：幅 1000px、`object_location`：幅 2000px）を直接参照して表示します。
2. **非本文コマ全件＋人間による検証サンプルの網羅（4,131 コマ）**
   - 全 76,381 コマのうち 95.3%（72,761 コマ）は通常の字ありページであるため、視覚的な検証・探索に有用な以下の **4,131 コマ**（重複を除く）を収録しています：
     - 最終ラベルが **「字なし（`has_text = false`）」の全 3,620 コマ**
     - **段 3：著者が目視確認した全 318 コマ**（優先確認 A1：118 コマ、無作為 B：100 コマ、層別 C：100 コマ。著者が修正した 13 コマを含む）
     - **段 4：第 2 判定者が独立判定した全 300 コマ**（無作為 200 コマ＋字なし側 100 コマ）
     - **判定基準の凡例 21 コマ**（字あり 11 例＋字なし 10 例）
3. **[cjk_index](https://github.com/nakamura196/cjk_index) による日本語検索と多軸ファセット集計**
   - CollectionBuilder 標準の `lunr.js` では日本語クエリが機能しないため、文字バイグラム・異体字正規化・ファセット集計を備えた Ruby gem `cjk_index`（`preset: collectionbuilder`）を組み込んでいます。
4. **日英バイリンガル出力**
   - 同一リポジトリから日本語版（`/`）と英語版（`/en/`）を静的ビルドします。

---

## データの再生成とビルド方法

### 1. メタデータ CSV の再生成

Zenodo 公開用データ（`canvases.tsv`・`books.tsv`・`review-human.tsv` 等）から `_data/shohon-nontext.csv`（日本語版）および `_data/shohon-nontext-en.csv`（英語版）を生成します。

```bash
python3 _tools/build_cb_metadata.py
```

### 2. サイトのビルド（Jekyll）

```bash
# 日本語版（_site/）
bundle exec jekyll build

# 英語版（_site/en/）
bundle exec jekyll build --config _config.yml,_config.en.yml -d _site/en
```

---

## ライセンス

- **コード・テンプレート**：MIT License（[CollectionBuilder-CSV](https://github.com/CollectionBuilder/collectionbuilder-csv) および [cb-ja-demo](https://github.com/nakamura196/cb-ja-demo) に基づく）
- **ラベル・メタデータ**：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)（中村 覚）
- **画像および書誌**：国文学研究資料館「[国書データベース](https://kokusho.nijl.ac.jp/)」および各所蔵機関（利用条件は各コマの `rights` 欄および `books.tsv` に記載）
