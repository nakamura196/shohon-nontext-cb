---
title: Criteria & About
permalink: /about.html
lang: en
heading: Labelling Criteria and Dataset Overview
sub-heading: Text-Presence and Imaging-Target Labels for 714 Classical Japanese Book Witnesses
---

## 1. Purpose and Scope of This Collection

Comparing witnesses of classical texts or evaluating OCR requires removing page images that do not carry the text of the work—such as covers, endpapers, blank leaves, imaging slips, and authentication slips. Detecting rulers and colour charts photographed alongside the book is equally necessary for automated cropping, scale estimation, and colour calibration.

Our dataset labels all 76,381 page images (IIIF canvases) across 714 witnesses of five Japanese classical works (*Ise monogatari*, *Kokin wakashū*, *Makura no sōshi*, *Taketori monogatari*, and *Tsurezuregusa*) from the [NIJL Union Catalogue Database of Japanese Texts (Kokusho Database)](https://kokusho.nijl.ac.jp/?ln=en) using a three-stage pipeline (logistic regression classifier → Gemini 4 Argon vision-language model → human verification).

Because 95.3% (72,761 canvases) of the full dataset are ordinary pages with text, this companion website focuses on the **4,131 canvases** that require visual inspection or serve as verification benchmarks:

- **All 3,620 non-text canvases (`has_text = false`)**: covers without titles, endpapers, blank pages, imaging slips, and pages showing only photographer's tags, seals, or library ownership labels.
- **Stage 3: All 318 canvases checked by the author**: Set A1 (118 likely errors), Set B (100 random canvases where classifier and VLM agreed), and Set C (100 canvases stratified by ruler and colour chart).
- **Stage 4: All 300 canvases judged independently by the second annotator**: 200 drawn at random from all 76,381 canvases and 100 drawn from the first-pass no-text pool.
- **Legend examples (21 canvases)**: 11 positive (`Text present`) and 10 negative (`No text`) reference examples used in the annotation guidelines.

{% include feature/button.html text="Browse Legend Examples (21)" link="/en/browse.html#verification:Legend example" color="primary" %}
{% include feature/button.html text="Browse Stage 3 Author Corrections (12)" link="/en/browse.html#verification:Stage 3: Corrected by author" color="outline-dark" %}

---

## 2. Labelling Criteria

### (a) Text presence (`has_text`)

**Question: Is at least one character written or printed on the book shown in the image?**
This judgement does not require reading cursive script or knowing the work. If either page of a two-page opening has writing, the canvas is labelled `Text present`.

- **Text present (`true`)**:
  - Ordinary pages of body text (cursive or regular script, kanji or kana, manuscript or printed)
  - Titles written directly on the cover or on a title slip (*daisen*) pasted on the cover
  - Authentication slips (*kiwamefuda*) and writing on paper pasted or inserted into the book
  - Marginalia, ownership notes, and leaf numbers on endpapers or margins, however small or faint, provided they have the shape of characters
  - Writing inside or at the edge of an illustration
- **No text (`false`)**:
  - Blank pages, decorative cover patterns, or illustrations without writing
  - Show-through from the reverse side only (seen mirrored)
  - Seals (*hanko*) alone
  - Writing on objects placed by the photographer: black number tags, rulers, colour charts, and white imaging slips (*satsuei-hyō*)
  - Watermark text overlaid on the digital image (e.g. "禁無断転載")
  - Ownership or shelf-mark labels pasted later by a library

{% include feature/card.html header="Boundary Example (Text present): Small marginal note (c_100063689_0087)" text="Although the opening appears blank at first glance, a small handwritten note in the upper left corner counts as writing on the book (corrected from false to true by the author in Stage 3, Set B). The image is not shown on this site because of the holding institution's terms of use. [View it in the Kokusho Database](https://kokusho.nijl.ac.jp/biblio/100063689/87)" %}

{% include feature/card.html header="Boundary Example (No text): Library ownership label only (c_100421525_0002)" text="The cover carries only a modern printed library label with a call number, which was added after the book's production and is excluded under our criteria." objectid="c_100421525_0002" %}

### (b) Ruler (`ruler`), colour chart (`colorchart`), and illustration (`illustration`)

Assigned to the 21,571 canvases inspected by the vision-language model in Stage 2. Scales printed along the edge of a colour chart are counted as part of the colour chart rather than as a separate ruler (in Stage 3 Set C, 4 canvases where the model mistook a colour-chart scale for a ruler were corrected by the author). In addition, 24 books in which the model marked a colour chart on only a few images were checked; on 3 black-and-white microfilm images the model had read a two-tone back cover or the scale of a ruler as a chart, and these were set to `false`.

---

## 3. Built with CollectionBuilder-CSV, IIIF, and `cjk_index`

This site demonstrates the interoperability and reusability (FAIR principles) of the Zenodo TSV dataset by feeding it directly into [CollectionBuilder-CSV](https://github.com/CollectionBuilder/collectionbuilder-csv):

1. **Non-custodial IIIF integration**: No image files are duplicated; thumbnails and zoomable images are requested on the fly from the Kokusho Database IIIF Image API. Images are shown only for books released into the public domain or under a Creative Commons licence or with free reuse terms (466 books); for the other 248 books, each canvas shows its labels and a link to the Kokusho Database.
2. **CJK full-text search and faceted filtering ([cjk_index](https://github.com/nakamura196/cjk_index))**: Stock `lunr.js` strips CJK characters by default. We use the `cjk_index` Ruby gem (`preset: collectionbuilder`) to provide fast character-bigram search, kanji variant normalization, and instant multi-facet counts across all 4,131 canvases.
3. **Bilingual static builds**: Both Japanese and English interfaces are generated from the same repository.

{% include feature/button.html text="Download Collection Metadata (CSV)" link="/en/assets/data/metadata.csv" color="outline-dark" %}

---

## 4. Credits and Licences

- **Dataset author**: Satoru Nakamura (Historiographical Institute, The University of Tokyo). The labels and metadata are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- **Images and bibliographic records**: National Institute of Japanese Literature ([Kokusho Database](https://kokusho.nijl.ac.jp/?ln=en)) and the respective holding institutions. Licence terms vary by book and are linked on each item page.
