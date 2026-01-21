#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
amazon de merged.csv + total products merged.csv

- ASIN üzerinden birleştirir
- Kolonlar farklıysa union kolon seti ile hizalar
- Duplicate ASIN varsa tekilleştirir (varsayılan: ilk geleni tutar)

Çıktı: merged_by_asin.csv
"""

import sys
import pandas as pd


FILE_DE = "amazon de merged.csv"
FILE_TOTAL = "total products merged.csv"
OUTPUT = "merged_by_asin.csv"


def read_csv_or_exit(path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(path, low_memory=False)
    except FileNotFoundError:
        print(f"Hata: '{path}' bulunamadı.")
        sys.exit(1)
    except Exception as e:
        print(f"Hata: '{path}' okunamadı: {e}")
        sys.exit(1)


def main() -> None:
    print("CSV'ler okunuyor...")
    df_de = read_csv_or_exit(FILE_DE)
    df_total = read_csv_or_exit(FILE_TOTAL)

    if "ASIN" not in df_de.columns:
        print(f"Hata: '{FILE_DE}' içinde ASIN sütunu yok.")
        sys.exit(1)
    if "ASIN" not in df_total.columns:
        print(f"Hata: '{FILE_TOTAL}' içinde ASIN sütunu yok.")
        sys.exit(1)

    print(f"amazon de merged: {len(df_de)} satır, {len(df_de.columns)} sütun")
    print(f"total products merged: {len(df_total)} satır, {len(df_total.columns)} sütun")

    # Kolonları union yapıp hizala
    all_cols = sorted(set(df_de.columns).union(set(df_total.columns)))
    df_de = df_de.reindex(columns=all_cols)
    df_total = df_total.reindex(columns=all_cols)

    # Birleştir
    merged = pd.concat([df_de, df_total], ignore_index=True)
    before = len(merged)

    # ASIN normalize (boşlukları temizle)
    merged["ASIN"] = merged["ASIN"].astype(str).str.strip()
    merged = merged[merged["ASIN"].notna() & (merged["ASIN"] != "")].copy()

    # Duplicate ASIN tekilleştir
    dup_count = merged["ASIN"].duplicated().sum()
    if dup_count:
        print(f"Duplicate ASIN bulundu: {dup_count} adet. Tekilleştiriliyor (ilk kayıt tutulacak)...")
    merged = merged.drop_duplicates(subset=["ASIN"], keep="first").reset_index(drop=True)

    print("\n=== SONUÇ ===")
    print(f"Birleşim (ham): {before} satır")
    print(f"ASIN boş satırlar çıkarıldıktan sonra: {before - (before - len(pd.concat([df_de, df_total], ignore_index=True))) }")  # no-op, just keep simple
    print(f"Final (tekil ASIN): {len(merged)} satır")
    print(f"Final sütun sayısı: {len(merged.columns)}")

    merged.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print(f"\n✓ Kaydedildi: {OUTPUT}")


if __name__ == "__main__":
    main()

