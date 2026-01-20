#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hızlı TR çeviri (Python 3.11 venv311 ile önerilir)

- Locale=com -> EN->TR
- Locale=de  -> DE->TR
- Title içindeki Renewed/refurbished kaldırılır (TR sonuçta "yenilenmiş" de temizlenir)
- Yeni sütunlar: `Türkçe İsim`, `Türkçe Kategori Ağacı`

Hız optimizasyonu:
- `Title` ve `Categories: Tree` için benzersiz değerleri çıkarır
- Her benzersiz değeri 1 kez çevirir, sonra tüm satırlara map eder (cache/dedup)
"""

from __future__ import annotations

import re
import sys
import time
from typing import Dict, Optional

import pandas as pd
from googletrans import Translator


def clean_title_before_translation(title: str) -> str:
    s = re.sub(r"\b(renewed|refurbished)\b", "", title, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def clean_translated_text(text: str) -> str:
    s = re.sub(r"\b(yenilenmiş)\b", "", text, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def build_unique(series: pd.Series) -> list[str]:
    return (
        series.dropna()
        .astype(str)
        .map(lambda s: s.strip())
        .loc[lambda s: s != ""]
        .unique()
        .tolist()
    )


def translate_uniques(
    translator: Translator,
    uniques: list[str],
    src: str,
    dest: str,
    pre_clean=None,
    post_clean=None,
    label: str = "",
    log_every: int = 25,
) -> Dict[str, Optional[str]]:
    out: Dict[str, Optional[str]] = {}
    total = len(uniques)
    start = time.time()
    ok = 0
    fail = 0
    print(f"[{label}] Başlıyor | src={src} dest={dest} | toplam benzersiz={total}", flush=True)
    for i, orig in enumerate(uniques, start=1):
        s = orig
        if pre_clean:
            s = pre_clean(s)
        if not s:
            out[orig] = None
            fail += 1
            continue
        # googletrans bazen saçma bir internal hataya düşebiliyor
        # ('Translator' object has no attribute 'raise_Exception').
        # Bu durumda translator'ı yeniden oluşturup retry yapıyoruz.
        attempt = 0
        max_attempts = 3
        last_err: Optional[Exception] = None
        while attempt < max_attempts:
            attempt += 1
            try:
                tr = translator.translate(s, src=src, dest=dest).text
                if post_clean:
                    tr = post_clean(tr)
                out[orig] = tr
                ok += 1
                last_err = None
                break
            except Exception as e:
                last_err = e
                msg = str(e)
                print(
                    f"[{label}] Çeviri hatası [{i}/{total}] (deneme {attempt}/{max_attempts}): {msg}",
                    flush=True,
                )
                # Backoff
                time.sleep(1.5 * attempt)
                # Translator'ı yenile (özellikle raise_Exception bug'ında işe yarıyor)
                try:
                    translator = Translator(service_urls=["translate.googleapis.com"])
                except Exception:
                    translator = Translator()
        if last_err is not None:
            out[orig] = None
            fail += 1
        if i % log_every == 0 or i == total:
            elapsed = time.time() - start
            rate = i / elapsed if elapsed > 0 else 0.0
            remaining = (total - i) / rate if rate > 0 else 0.0
            print(
                f"[{label}] İlerleme {i}/{total} | ok={ok} fail={fail} | "
                f"hız={rate:.2f}/sn | kalan~{remaining/60:.1f} dk",
                flush=True,
            )
    return out


def main() -> None:
    input_file = "merged_lego_products.csv"
    output_file = "merged_lego_products.csv"

    try:
        df = pd.read_csv(input_file, low_memory=False)
    except FileNotFoundError:
        print(f"Hata: '{input_file}' bulunamadı.")
        sys.exit(1)

    for col in ["Locale", "Title", "Categories: Tree"]:
        if col not in df.columns:
            print(f"Hata: '{col}' sütunu yok.")
            sys.exit(1)

    df["Locale"] = df["Locale"].astype(str).str.lower()
    df_com = df[df["Locale"] == "com"]
    df_de = df[df["Locale"] == "de"]

    # translate.googleapis.com genelde daha stabil
    translator = Translator(service_urls=["translate.googleapis.com"])

    print(f"[0/6] CSV okundu. Toplam satır: {len(df)} | com: {len(df_com)} | de: {len(df_de)}", flush=True)

    # BENZERSİZLER
    t0 = time.time()
    print("[1/6] Benzersiz değerler çıkarılıyor...", flush=True)
    com_titles = build_unique(df_com["Title"])
    de_titles = build_unique(df_de["Title"])
    com_cats = build_unique(df_com["Categories: Tree"])
    de_cats = build_unique(df_de["Categories: Tree"])

    print(
        f"[1/6] Tamam. Süre: {time.time()-t0:.2f} sn | "
        f"Benzersiz Title (com): {len(com_titles)} | (de): {len(de_titles)} | "
        f"Benzersiz Category (com): {len(com_cats)} | (de): {len(de_cats)}",
        flush=True,
    )

    # ÇEVİRİ
    print("\n[2/6] Title çevirileri başlıyor...", flush=True)
    com_title_map = translate_uniques(
        translator,
        com_titles,
        src="en",
        dest="tr",
        pre_clean=clean_title_before_translation,
        post_clean=clean_translated_text,
        label="Title EN->TR",
        log_every=25,
    )
    de_title_map = translate_uniques(
        translator,
        de_titles,
        src="de",
        dest="tr",
        pre_clean=clean_title_before_translation,
        post_clean=clean_translated_text,
        label="Title DE->TR",
        log_every=25,
    )

    print("\n[3/6] Category çevirileri başlıyor...", flush=True)
    # Category tarafında benzersiz az olacağı için daha sık log
    com_cat_map = translate_uniques(
        translator, com_cats, src="en", dest="tr", label="Cat EN->TR", log_every=10
    )
    de_cat_map = translate_uniques(
        translator, de_cats, src="de", dest="tr", label="Cat DE->TR", log_every=10
    )

    # MAP UYGULA
    print("\n[4/6] Çeviriler satırlara uygulanıyor (map)...", flush=True)
    df["Türkçe İsim"] = None
    df["Türkçe Kategori Ağacı"] = None

    if len(df_com):
        idxs = df_com.index
        df.loc[idxs, "Türkçe İsim"] = df.loc[idxs, "Title"].astype(str).map(com_title_map)
        df.loc[idxs, "Türkçe Kategori Ağacı"] = df.loc[idxs, "Categories: Tree"].astype(str).map(com_cat_map)

    if len(df_de):
        idxs = df_de.index
        df.loc[idxs, "Türkçe İsim"] = df.loc[idxs, "Title"].astype(str).map(de_title_map)
        df.loc[idxs, "Türkçe Kategori Ağacı"] = df.loc[idxs, "Categories: Tree"].astype(str).map(de_cat_map)

    print("[5/6] CSV yazılıyor...", flush=True)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print("\n[6/6] Tamamlandı.", flush=True)
    print(f"Türkçe İsim dolu: {df['Türkçe İsim'].notna().sum()} / {len(df)}")
    print(f"Türkçe Kategori Ağacı dolu: {df['Türkçe Kategori Ağacı'].notna().sum()} / {len(df)}")


if __name__ == "__main__":
    main()

