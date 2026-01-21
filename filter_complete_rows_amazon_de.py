#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon DE - Tam Dolu Satır Filtreleme

`amazon de merged.csv` dosyasında aşağıdaki sütunların herhangi biri boş/NaN ise satırı siler:
- Image
- Title
- Reviews: Rating
- List Price: Current
- Categories: Tree
- ASIN
- Product Codes: EAN
- Brand
- TL Fiyat
- Türkçe İsim
- Türkçe Kategori Ağacı
"""

import sys
import pandas as pd


REQUIRED_COLUMNS = [
    "Image",
    "Title",
    "Reviews: Rating",
    "List Price: Current",
    "Categories: Tree",
    "ASIN",
    "Product Codes: EAN",
    "Brand",
    "TL Fiyat",
    "Türkçe İsim",
    "Türkçe Kategori Ağacı",
]


def main() -> None:
    input_file = "amazon de merged.csv"
    output_file = "amazon de merged.csv"

    try:
        df = pd.read_csv(input_file, low_memory=False)
    except FileNotFoundError:
        print(f"Hata: '{input_file}' bulunamadı.")
        sys.exit(1)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        print("Hata: Beklenen bazı sütunlar dosyada yok:")
        for c in missing_cols:
            print(f"  - {c}")
        print("\nMevcut sütunlar:")
        print(", ".join(df.columns))
        sys.exit(1)

    before = len(df)
    print(f"Toplam satır (önce): {before}")
    print(f"Kontrol edilecek sütun sayısı: {len(REQUIRED_COLUMNS)}")

    # Boş/NaN analizi
    print("\nEksik değer analizi:")
    for c in REQUIRED_COLUMNS:
        s = df[c]
        missing = s.isna().sum() + (s.astype(str).str.strip() == "").sum()
        print(f"  {c}: {missing} eksik")

    mask = pd.Series(True, index=df.index)
    for c in REQUIRED_COLUMNS:
        mask &= df[c].notna() & (df[c].astype(str).str.strip() != "")

    df2 = df.loc[mask].copy()
    removed = before - len(df2)

    print("\n=== SONUÇ ===")
    print(f"Silinen satır: {removed}")
    print(f"Kalan satır (tümü dolu): {len(df2)}")

    df2.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"\n✓ Kaydedildi: {output_file}")


if __name__ == "__main__":
    main()

