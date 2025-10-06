# -*- coding: utf-8 -*-


import sys
import os
import json
import re
from collections import defaultdict
from typing import List, Dict, Any

try:
    import cv2
    from PIL import Image
    import pytesseract
except Exception as e:
    raise SystemExit(
        "Необходимо установить зависимости: opencv-python-headless pillow pytesseract. "
        "Ошибка импорта: " + str(e)
    )

IMAGE_PATH_DEFAULT = r"C:\Users\dim4d\Desktop\From git\photomask-cover-letter-generator\app\initial_data\photo_template_table.png"

TESSERACT_CONFIG = r"--oem 3 --psm 6"
TESSERACT_LANG = "rus+eng"


def run_ocr_words(image_path: str) -> List[Dict[str, Any]]:
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        raise FileNotFoundError(f"Не могу открыть изображение: {image_path}")
    pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    data = pytesseract.image_to_data(
        pil,
        output_type=pytesseract.Output.DICT,
        config=TESSERACT_CONFIG,
        lang=TESSERACT_LANG,
    )
    words = []
    n = len(data["level"])
    for i in range(n):
        txt = data["text"][i].strip()
        if not txt:
            continue
        try:
            conf = float(data["conf"][i])
        except Exception:
            conf = -1.0
        left = int(data["left"][i])
        top = int(data["top"][i])
        width = int(data["width"][i])
        height = int(data["height"][i])
        words.append(
            {
                "text": txt,
                "conf": conf,
                "left": left,
                "top": top,
                "width": width,
                "height": height,
                "x_center": left + width // 2,
                "y_center": top + height // 2,
                "block_num": int(data["block_num"][i]),
                "par_num": int(data["par_num"][i]),
                "line_num": int(data["line_num"][i]),
                "word_num": int(data["word_num"][i]),
            }
        )
    return words


def group_by_line(words: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    grouped = defaultdict(list)
    for w in words:
        key = (w["block_num"], w["par_num"], w["line_num"])
        grouped[key].append(w)
    rows = []
    for key, row_words in sorted(
        grouped.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])
    ):
        rows.append(sorted(row_words, key=lambda x: x["x_center"]))
    return rows


RE_LAYER = re.compile(r"\b(\d{3})\b")
RE_VERSION = re.compile(r"\b([1-9]\d*)\b")
RE_BARCODE = re.compile(r"\b([A-Za-z0-9]{6,20})\b")


def normalize_text(s: str) -> str:
    return " ".join(s.split())


def extract_from_row_text(row_text: str):
    res_layer = None
    res_version = None
    res_barcode = None
    m = RE_LAYER.search(row_text)
    if m:
        res_layer = m.group(1)
    for mv in RE_VERSION.finditer(row_text):
        val = mv.group(1)
        if res_layer is None or val != res_layer:
            res_version = val
            break
    for mb in RE_BARCODE.finditer(row_text):
        candidate = mb.group(1)
        if len(candidate) >= 6:
            res_barcode = candidate
            break
    return res_layer, res_version, res_barcode


def main(image_path: str):
    print("Запуск OCR для:", image_path)
    words = run_ocr_words(image_path)
    print(f"Найдено слов: {len(words)}")
    rows = group_by_line(words)
    print(f"Построено строк (grouped by Tesseract lines): {len(rows)}\n")

    raw_rows = []
    extracted_rows = []
    for row_words in rows:
        row_text = " ".join(w["text"] for w in row_words)
        row_text = normalize_text(row_text)
        word_infos = [
            {
                "text": w["text"],
                "conf": w["conf"],
                "left": w["left"],
                "top": w["top"],
                "width": w["width"],
                "height": w["height"],
                "x_center": w["x_center"],
            }
            for w in row_words
        ]
        raw_rows.append({"row_text": row_text, "words": word_infos})
        layer, version, barcode = extract_from_row_text(row_text)
        extracted_rows.append(
            {
                "row_text": row_text,
                "layer": layer,
                "version": version,
                "barcode": barcode,
            }
        )

    layers = [r["layer"] for r in extracted_rows if r["layer"]]
    versions = [r["version"] for r in extracted_rows if r["version"]]
    barcodes = [r["barcode"] for r in extracted_rows if r["barcode"]]

    out = {
        "raw_rows": raw_rows,
        "extracted_rows": extracted_rows,
        "summary": {"№ слоя": layers, "Версия слоя": versions, "Штрихкод": barcodes},
    }

    print(json.dumps(out, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    img = IMAGE_PATH_DEFAULT
    if len(sys.argv) > 1 and sys.argv[1].strip():
        img = sys.argv[1].strip()
    main(img)
