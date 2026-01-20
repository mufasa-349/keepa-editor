#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Offline Türkçe Çeviri (Argos Translate)

- `Locale` = com  -> İngilizce'den Türkçe'ye
- `Locale` = de   -> Almanca'dan Türkçe'ye
- `Title` içinde Renewed / refurbished varsa temizler (TR çıktıda "yenilenmiş" de temizlenir)
- Yeni sütunlar: `Türkçe İsim`, `Türkçe Kategori Ağacı`

Not: Performans için benzersiz Title/Category değerlerini çevirip cache'ler.
"""

from __future__ import annotations

import re
import sys
from typing import Dict, Optional, Tuple

import pandas as pd


USD_MARK = "-409"
EUR_MARK = "-C0A"


def clean_title_before_translation(title: str) -> str:
    # Renewed / refurbished (case-insensitive) kaldır
    s = re.sub(r"\b(renewed|refurbished)\b", "", title, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def clean_translated_text(text: str) -> str:
    # Türkçe sonuçta yenilenmiş vb. kalmasın
    s = re.sub(r"\b(yenilenmiş)\b", "", text, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def ensure_argos_models() -> None:
    """
    EN->TR ve DE->TR modelleri yoksa indirip kurar.
    """
    from argostranslate import package

    installed = package.get_installed_packages()
    installed_lang_pairs = {(p.from_code, p.to_code) for p in installed}

    needed = {("en", "tr"), ("de", "tr")}
    missing = needed - installed_lang_pairs
    if not missing:
        return

    print(f"Argos modelleri eksik: {sorted(list(missing))}. İndiriliyor/kuruluyor...")
    package.update_package_index()
    available = package.get_available_packages()

    for (src, dst) in sorted(list(missing)):
        candidates = [p for p in available if p.from_code == src and p.to_code == dst]
        if not candidates:
            raise RuntimeError(f"Argos modeli bulunamadı: {src}->{dst}")
        pkg = candidates[0]
        path = pkg.download()
        package.install_from_path(path)


def get_translators() -> Tuple[object, object]:
    from argostranslate import translate

    en_tr = translate.get_translation_from_codes("en", "tr")
    de_tr = translate.get_translation_from_codes("de", "tr")
    return en_tr, de_tr


def translate_cached(
    values: pd.Series,
    translator,
    pre_clean=None,
    post_clean=None,
    label: str = "",
) -> Dict[str, Optional[str]]:
    """
    values içindeki benzersiz stringleri çevirip dict döner: original -> translated
    """
    mapping: Dict[str, Optional[str]] = {}

    uniques = (
        values.dropna()
        .astype(str)
        .map(lambda s: s.strip())
        .loc[lambda s: s != ""]
        .unique()
        .tolist()
    )

    total = len(uniques)
    for i, orig in enumerate(uniques, start=1):
        s = orig
        if pre_clean:
            s = pre_clean(s)
        if not s:
            mapping[orig] = None
            continue
        try:
            out = translator.translate(s)
            if post_clean:
                out = post_clean(out)
            mapping[orig] = out
        except Exception as e:
            print(f"  Çeviri hatası ({label}) [{i}/{total}]: {e}")
            mapping[orig] = None

        if i % 200 == 0:
            print(f"  {label} ilerleme: {i}/{total} benzersiz değer çevrildi...")

    return mapping


def main() -> None:
    input_file = "merged_lego_products.csv"
    output_file = "merged_lego_products.csv"

    try:
        df = pd.read_csv(input_file, low_memory=False)
    except FileNotFoundError:
        print(f"Hata: '{input_file}' bulunamadı.")
        sys.exit(1)

    required = ["Locale", "Title", "Categories: Tree"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"Hata: Eksik sütunlar: {missing}")
        sys.exit(1)

    # Modelleri kur + translatorları al
    ensure_argos_models()
    en_tr, de_tr = get_translators()

    # Locale'a göre ayır
    df["Locale"] = df["Locale"].astype(str).str.lower()
    df_com = df[df["Locale"] == "com"].copy()
    df_de = df[df["Locale"] == "de"].copy()

    print(f"Toplam satır: {len(df)} | com: {len(df_com)} | de: {len(df_de)}")

    # Title çevirileri (cache)
    print("\nTitle çevirileri (offline)...")
    com_title_map = translate_cached(
        df_com["Title"],
        en_tr,
        pre_clean=clean_title_before_translation,
        post_clean=clean_translated_text,
        label="Title (EN->TR)",
    )
    de_title_map = translate_cached(
        df_de["Title"],
        de_tr,
        pre_clean=clean_title_before_translation,
        post_clean=clean_translated_text,
        label="Title (DE->TR)",
    )

    # Category çevirileri (cache)
    print("\nKategori ağacı çevirileri (offline)...")
    com_cat_map = translate_cached(
        df_com["Categories: Tree"],
        en_tr,
        label="Category (EN->TR)",
    )
    de_cat_map = translate_cached(
        df_de["Categories: Tree"],
        de_tr,
        label="Category (DE->TR)",
    )

    # Map'leri geri uygula
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

    # Kaydet
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print("\nTamamlandı.")
    print(f"Türkçe İsim dolu: {df['Türkçe İsim'].notna().sum()} / {len(df)}")
    print(f"Türkçe Kategori Ağacı dolu: {df['Türkçe Kategori Ağacı'].notna().sum()} / {len(df)}")


if __name__ == "__main__":
    main()

