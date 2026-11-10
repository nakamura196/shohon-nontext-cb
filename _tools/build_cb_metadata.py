"""Zenodo 公開用データ（release/canvases.tsv・books.tsv・review-human.tsv 等）から
CollectionBuilder-CSV 用のメタデータ（_data/shohon-nontext.csv および _data/shohon-nontext-en.csv）を生成する。

収録対象（A-2：計 4,131 コマ）:
  1. 最終ラベルが「字なし（has_text = false）」の全コマ（3,620 コマ）
  2. 段 3 で著者が確認した全コマ（318 コマ：A1=118, B=100, C=100）
  3. 段 4 で第 2 判定者が独立判定した全コマ（300 コマ：無作為 200 + 字なし側 100）
  4. 判定基準の凡例（legend）に掲げた見本コマ（21 コマ：字あり 11 + 字なし 10）

使い方:
  python3 papers/shohon-nontext-data/build_cb_metadata.py
"""
import csv
import glob
import json
import os

O = os.path.expanduser("~/git/archivebase/archivebase-data.worktrees/shohon/shohon/nontext/out/")
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_data")

WORK_JA = {
    "ise": "伊勢物語",
    "kokin": "古今和歌集",
    "makura": "枕草子",
    "taketori": "竹取物語",
    "tsurezure": "徒然草",
}
WORK_EN = {
    "ise": "Ise monogatari",
    "kokin": "Kokin wakashū",
    "makura": "Makura no sōshi",
    "taketori": "Taketori monogatari",
    "tsurezure": "Tsurezuregusa",
}

KANSHA_JA = {"manuscript": "写本", "printed": "版本"}
KANSHA_EN = {"manuscript": "Manuscript", "printed": "Printed"}

PAGE_TYPE_JA = {
    "body_text": "本文",
    "cover": "表紙",
    "illustration": "挿絵",
    "endpaper": "見返し",
    "blank": "白紙",
    "preface_postface": "序跋",
    "colophon": "奥書",
    "imaging_slip": "撮影票",
    "authentication_slip": "極札",
    "table_of_contents": "目録",
    "other": "その他",
    "": "未付与（分類器のみ）",
}
PAGE_TYPE_EN = {
    "body_text": "Body text",
    "cover": "Cover",
    "illustration": "Illustration",
    "endpaper": "Endpaper",
    "blank": "Blank page",
    "preface_postface": "Preface or postface",
    "colophon": "Colophon",
    "imaging_slip": "Imaging slip",
    "authentication_slip": "Authentication slip",
    "table_of_contents": "Table of contents",
    "other": "Other",
    "": "Not assessed (classifier only)",
}

SOURCE_JA = {
    "human": "著者確認（human）",
    "model": "VLM（model）",
    "rule": "規則（rule）",
    "classifier": "分類器（classifier）",
    "": "未判定",
}
SOURCE_EN = {
    "human": "Author check (human)",
    "model": "VLM (model)",
    "rule": "Rule (rule)",
    "classifier": "Classifier (classifier)",
    "": "Not assessed",
}

LEGEND_NOTES = {
    ("100370087", 23): ("字あり見本：ふつうの本文（くずし字・楷書、漢字・かな、手書き・印刷を問わず字あり）", "Legend (Text): Ordinary page of text"),
    ("300110302", 2): ("字あり見本：題簽（表紙に貼った題名の紙。表紙の字は1か所だけでも字あり）", "Legend (Text): Title slip (daisen) pasted on the cover"),
    ("100074903", 2): ("字あり見本：題簽（白黒の撮影。黒い表紙に貼った白い紙の題名）", "Legend (Text): Title slip on a monochrome scan"),
    ("100002230", 2): ("字あり見本：表紙に貼られた題名（独立判定画面の見本）", "Legend (Text): Title on a slip pasted on the cover"),
    ("100232330", 4): ("字あり見本：極札（鑑定の札。本に添えられた細長い札）", "Legend (Text): Authentication slip (kiwamefuda)"),
    ("300128540", 11): ("字あり見本：極札（カラーの撮影。横の色見本は数えない）", "Legend (Text): Authentication slip photographed with a colour chart"),
    ("100063964", 200): ("字あり見本：書き入れ（見返しの端。白紙に見えても端に字があれば字あり）", "Legend (Text): Small marginal note on an endpaper"),
    ("100063689", 87): ("字あり見本：書き入れ（左上の小さな書き込み。独立判定画面の見本）", "Legend (Text): Small note in the upper left corner"),
    ("100272084", 9): ("字あり見本：貼り紙・挟み込まれた紙の字", "Legend (Text): Writing on paper pasted or inserted into the book"),
    ("100063957", 167): ("字あり見本：薄い墨（かすれて読めなくても字あり。独立判定画面の見本）", "Legend (Text): Faint ink"),
    ("100038906", 81): ("字あり見本：絵の端の字（絵の左端に1行の字。独立判定画面の見本）", "Legend (Text): One line of text at the left edge of a picture"),
    ("100063962", 229): ("字なし見本：白紙と番号札（下の黒い番号札は撮影用なので数えない）", "Legend (No text): Blank page with a photographer's black number tag"),
    ("100074901", 1): ("字なし見本：撮影票（白い記録カード。本の一部ではない）", "Legend (No text): Imaging slip (white record card)"),
    ("100010636", 3): ("字なし見本：撮影のときに置いた数字の札", "Legend (No text): Photographer's number tag only"),
    ("300120319", 3): ("字なし見本：定規・色見本・印（撮影用の札・定規・色見本と赤い印のみ）", "Legend (No text): Ruler, colour chart, seal and photographer's tag only"),
    ("200003050", 137): ("字なし見本：印（はんこ）だけのページ", "Legend (No text): Seals only"),
    ("100421525", 2): ("字なし見本：図書館が後から貼った蔵書ラベルのみ", "Legend (No text): Library ownership label only"),
    ("100038873", 49): ("字なし見本：画像に重ねた透かしの字（「禁無断転載」）のみ", "Legend (No text): Overlaid watermark text only"),
    ("100232500", 74): ("字なし見本：裏写り（裏の字が左右逆に透けて見えるだけ）", "Legend (No text): Show-through from the reverse side only"),
    ("200001893", 45): ("字なし見本：絵だけ（番号札は数えない）", "Legend (No text): Picture only"),
    ("100306425", 124): ("字なし見本：表紙の模様だけ（色見本は数えない）", "Legend (No text): Cover pattern and colour chart only"),
}


def read_tsv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


# creativecommons.org 以外で、自由に利用できると確かめた利用条件（2026-11-10、本人と確認）
FREE_LICENSE_PREFIXES = (
    "https://rmda.kulib.kyoto-u.ac.jp/license_icon/free-license",  # 京都大学貴重資料デジタルアーカイブ「自由利用」
    "https://dl.ndl.go.jp/ja/help_iiif",  # 国立国会図書館デジタルコレクション（IIIF の利用について）
)


def is_open_license(url):
    """パブリックドメイン（PDM・CC0）か CC ライセンス、または FREE_LICENSE_PREFIXES なら True。
    それ以外（所蔵機関ごとの利用条件のページなど）は False とし、画像を出さない。"""
    from urllib.parse import urlparse
    u = url.strip()
    host = urlparse(u).netloc.lower()
    if host == "creativecommons.org" or host.endswith(".creativecommons.org"):
        return True
    return u.startswith(FREE_LICENSE_PREFIXES)


NO_IMAGE_NOTE = (
    "画像は所蔵機関の利用条件により、このサイトでは表示していません。国書データベースでご覧ください。",
    "The image is not shown on this site because of the holding institution's terms of use. See it in the Kokusho Database.",
)


def tb(v):
    return str(v).lower() == "true"


def main():
    canvases = read_tsv(O + "release/canvases.tsv")
    books = {r["bid"]: r for r in read_tsv(O + "release/books.tsv")}
    human_rows = {
        (r["bid"], int(r["canvas"])): r
        for r in read_tsv(O + "review-human.tsv")
        if tb(r["checked"])
    }
    recheck = (
        {(r["bid"], int(r["canvas"])): r["text"] for r in read_tsv(O + "recheck-text.tsv") if r["text"]}
        if os.path.exists(O + "recheck-text.tsv")
        else {}
    )
    indep_rows = {
        (r["bid"], int(r["canvas"])): r
        for r in read_tsv(O + "independent/sample.tsv")
    }
    cc_fix = {
        (r["bid"], int(r["canvas"])): r
        for r in read_tsv(O + "objects-corrections.tsv")
    }
    t2 = {}
    for g in sorted(glob.glob(O + "agy-text2/batch-*.json")):
        for x in json.load(open(g, encoding="utf-8")):
            t2[(x["bid"], int(x["canvas"]))] = bool(x["has_text"])

    cols = [
        "objectid",
        "title",
        "work",
        "book_title",
        "bid",
        "canvas_index",
        "kansha",
        "has_text",
        "page_type",
        "imaging_targets",
        "ruler",
        "colorchart",
        "illustration",
        "verification",
        "correction_detail",
        "has_text_source",
        "p_text",
        "ocr_chars",
        "dimensions",
        "fingerprints",
        "description",
        "rights",
        "rightsstatement",
        "source",
        "canvas_uri",
        "manifest",
        "image_small",
        "image_thumb",
        "object_location",
        "image_alt_text",
        "format",
        "display_template",
    ]

    rows_ja = []
    rows_en = []
    n_hidden = 0

    for c in canvases:
        bid = c["bid"]
        idx = int(c["canvas_index"])
        key = (bid, idx)

        is_notext = c["has_text"] == "false"
        in_human = key in human_rows
        in_indep = key in indep_rows
        in_legend = key in LEGEND_NOTES

        if not (is_notext or in_human or in_indep or in_legend):
            continue

        b = books.get(bid, {})
        n_canv = b.get("n_canvases", "")
        w_code = c["work"]
        w_ja = WORK_JA.get(w_code, w_code)
        w_en = WORK_EN.get(w_code, w_code)
        b_title = b.get("title", "")

        objectid = f"c_{bid}_{idx:04d}"
        title_ja = f"{w_ja}（{bid}）第{idx}コマ／全{n_canv}コマ"
        title_en = f"{w_en} ({bid}), image {idx} of {n_canv}"

        kansha_ja = KANSHA_JA.get(b.get("kansha", ""), b.get("kansha", ""))
        kansha_en = KANSHA_EN.get(b.get("kansha", ""), b.get("kansha", ""))

        has_text_ja = "字あり" if tb(c["has_text"]) else "字なし"
        has_text_en = "Text present" if tb(c["has_text"]) else "No text"

        pt = c["page_type"]
        pt_ja = PAGE_TYPE_JA.get(pt, pt)
        pt_en = PAGE_TYPE_EN.get(pt, pt)

        # Imaging targets & illustration
        targets_ja = []
        targets_en = []
        if c["ruler"] == "":
            ruler_ja, ruler_en = "未判定（分類器のみ）", "Not assessed"
            cc_ja, cc_en = "未判定（分類器のみ）", "Not assessed"
            ill_ja, ill_en = "未判定（分類器のみ）", "Not assessed"
            targets_ja.append("未判定（分類器のみ）")
            targets_en.append("Not assessed")
        else:
            ruler_ja = "あり" if tb(c["ruler"]) else "なし"
            ruler_en = "Present" if tb(c["ruler"]) else "Absent"
            cc_ja = "あり" if tb(c["colorchart"]) else "なし"
            cc_en = "Present" if tb(c["colorchart"]) else "Absent"
            ill_ja = "あり" if tb(c["illustration"]) else "なし"
            ill_en = "Present" if tb(c["illustration"]) else "Absent"
            if tb(c["ruler"]):
                targets_ja.append("定規あり")
                targets_en.append("Ruler")
            if tb(c["colorchart"]):
                targets_ja.append("カラーチャートあり")
                targets_en.append("Colour chart")
            if tb(c["illustration"]):
                targets_ja.append("挿絵あり")
                targets_en.append("Illustration")
            if not targets_ja:
                targets_ja.append("撮影用具・挿絵なし")
                targets_en.append("None")

        # Verification tags and correction details
        ver_ja = []
        ver_en = []
        corr_ja = []
        corr_en = []

        if in_legend:
            ver_ja.append("凡例（判定基準の見本）")
            ver_en.append("Legend example")

        if in_human:
            hr = human_rows[key]
            sec = hr["sec"]
            sec_map_ja = {
                "A1": "段3：著者確認（A1：優先確認118）",
                "B": "段3：著者確認（B：無作為100）",
                "C": "段3：著者確認（C：層別100）",
            }
            sec_map_en = {
                "A1": "Stage 3: Author check (A1: likely errors 118)",
                "B": "Stage 3: Author check (B: random 100)",
                "C": "Stage 3: Author check (C: stratified 100)",
            }
            ver_ja.append(sec_map_ja.get(sec, f"段3：著者確認（{sec}）"))
            ver_en.append(sec_map_en.get(sec, f"Stage 3: Author check ({sec})"))

            # Compare author's final value with model's final value (after pass 2)
            fin_h_text = recheck.get(key, hr["text"]).lower()
            fin_m_text = "true" if (tb(hr["agy_text"]) or t2.get(key) is True) else "false"
            if fin_h_text != fin_m_text:
                corr_ja.append(f"字の有無を修正（VLM最終:{fin_m_text} → 著者:{fin_h_text}）")
                corr_en.append(f"Text presence corrected (VLM:{fin_m_text} -> Author:{fin_h_text})")
            if hr["agy_ruler"].lower() != hr["ruler"].lower():
                corr_ja.append(f"定規を修正（VLM:{hr['agy_ruler'].lower()} → 著者:{hr['ruler'].lower()}）")
                corr_en.append(f"Ruler corrected (VLM:{hr['agy_ruler'].lower()} -> Author:{hr['ruler'].lower()})")
            if hr["agy_colorchart"].lower() != hr["colorchart"].lower():
                corr_ja.append(f"カラーチャートを修正（VLM:{hr['agy_colorchart'].lower()} → 著者:{hr['colorchart'].lower()}）")
                corr_en.append(f"Colour chart corrected (VLM:{hr['agy_colorchart'].lower()} -> Author:{hr['colorchart'].lower()})")
            if tb(hr["illust_checked"]) and hr["agy_illust"].lower() != hr["illust"].lower():
                corr_ja.append(f"挿絵を修正（VLM:{hr['agy_illust'].lower()} → 著者:{hr['illust'].lower()}）")
                corr_en.append(f"Illustration corrected (VLM:{hr['agy_illust'].lower()} -> Author:{hr['illust'].lower()})")

            if corr_ja:
                ver_ja.append("段3：著者による修正あり")
                ver_en.append("Stage 3: Corrected by author")
            else:
                ver_ja.append("段3：VLM判定と一致（修正なし）")
                ver_en.append("Stage 3: Agreed with VLM (no correction)")

        if in_indep:
            ir = indep_rows[key]
            st = ir["stratum"]
            if st == "random":
                ver_ja.append("段4：第2判定者（無作為200）")
                ver_en.append("Stage 4: Second annotator (random 200)")
            else:
                ver_ja.append("段4：第2判定者（字なし側100）")
                ver_en.append("Stage 4: Second annotator (no-text 100)")

        if key in cc_fix:
            ver_ja.append("カラーチャートの一貫性確認で著者が修正")
            ver_en.append("Colour chart corrected by author (consistency check)")
            corr_ja.append(f"カラーチャートを修正（VLM:true → 著者:{cc_fix[key]['colorchart']}。{cc_fix[key]['note']}）")
            corr_en.append(f"Colour chart corrected (VLM:true -> Author:{cc_fix[key]['colorchart']})")

        if t2.get(key) is True:
            ver_ja.append("段2：VLM第2パスで字ありに変更")
            ver_en.append("Stage 2: Changed to text in 2nd VLM pass")

        if not (in_human or in_indep or in_legend):
            ver_ja.append("段2：VLM判定（字なしコマ）")
            ver_en.append("Stage 2: VLM judgement (no-text)")

        corr_str_ja = "；".join(corr_ja) if corr_ja else "修正なし（または未確認）"
        corr_str_en = "; ".join(corr_en) if corr_en else "No correction (or not in Stage 3)"

        desc_parts_ja = []
        desc_parts_en = []
        if in_legend:
            desc_parts_ja.append(LEGEND_NOTES[key][0])
            desc_parts_en.append(LEGEND_NOTES[key][1])
        if corr_ja:
            desc_parts_ja.append("著者確認での修正：" + "、".join(corr_ja))
            desc_parts_en.append("Author check correction: " + "; ".join(corr_en))

        img_url = c["image_url"]
        img_small = img_url.replace("/full/2000,/0/default.jpg", "/full/1000,/0/default.jpg")
        img_thumb = img_url.replace("/full/2000,/0/default.jpg", "/full/400,/0/default.jpg")

        dim_str = f"{c['width']} × {c['height']} px (retrieved: {c['image_width']} × {c['image_height']} px on {c['retrieved']})"
        fp_str = f"SHA-256: {c['sha256'][:16]}… / dHash: {c['dhash']}"
        kokusho_viewer = f"https://kokusho.nijl.ac.jp/biblio/{bid}/{idx}"
        lic = b.get("license", "")
        show_image = is_open_license(lic)
        if not show_image:
            desc_parts_ja.append(NO_IMAGE_NOTE[0])
            desc_parts_en.append(NO_IMAGE_NOTE[1])
            n_hidden += 1

        common = {
            "objectid": objectid,
            "book_title": b_title,
            "bid": bid,
            "canvas_index": str(idx),
            "p_text": c["p_text"],
            "ocr_chars": c["ocr_chars"],
            "dimensions": dim_str,
            "fingerprints": fp_str,
            "rights": lic,
            "rightsstatement": lic,
            "source": kokusho_viewer,
            "canvas_uri": c["canvas_uri"],
            "manifest": b.get("manifest_uri", f"https://kokusho.nijl.ac.jp/biblio/{bid}/manifest"),
            "image_small": img_small if show_image else "",
            "image_thumb": img_thumb if show_image else "",
            "object_location": img_url if show_image else "",
            "format": "image/jpeg" if show_image else "",
            "display_template": "image" if show_image else "record",
        }

        row_ja = dict(
            common,
            title=title_ja,
            work=w_ja,
            kansha=kansha_ja,
            has_text=has_text_ja,
            page_type=pt_ja,
            imaging_targets=";".join(targets_ja),
            ruler=ruler_ja,
            colorchart=cc_ja,
            illustration=ill_ja,
            verification=";".join(ver_ja),
            correction_detail=corr_str_ja,
            has_text_source=SOURCE_JA[c["has_text_source"]],
            description=" ".join(desc_parts_ja),
            image_alt_text=f"{title_ja}（{has_text_ja}・{pt_ja}）",
        )

        row_en = dict(
            common,
            title=title_en,
            work=w_en,
            kansha=kansha_en,
            has_text=has_text_en,
            page_type=pt_en,
            imaging_targets=";".join(targets_en),
            ruler=ruler_en,
            colorchart=cc_en,
            illustration=ill_en,
            verification=";".join(ver_en),
            correction_detail=corr_str_en,
            has_text_source=SOURCE_EN[c["has_text_source"]],
            description=" ".join(desc_parts_en),
            image_alt_text=f"{title_en} ({has_text_en}, {pt_en})",
        )

        rows_ja.append(row_ja)
        rows_en.append(row_en)

    os.makedirs(OUT_DIR, exist_ok=True)
    for fn, rows in [("shohon-nontext.csv", rows_ja), ("shohon-nontext-en.csv", rows_en)]:
        out_path = os.path.join(OUT_DIR, fn)
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
        print(f"Wrote {len(rows)} rows to {out_path}")
    print(f"Image hidden (license not PD/CC/free): {n_hidden} of {len(rows_ja)} rows")


if __name__ == "__main__":
    main()
