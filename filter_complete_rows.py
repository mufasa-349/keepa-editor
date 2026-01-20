#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tam Dolu Satır Filtreleme Scripti
6 sütunun hepsinin dolu olduğu satırları tutar, eksik olanları siler.
"""

import pandas as pd
import sys

def filter_complete_rows():
    input_file = "merged_lego_products.csv"
    output_file = "merged_lego_products.csv"
    
    # Kontrol edilecek sütunlar (6 sütun)
    required_columns = [
        "Image",
        "ASIN",
        "Brand",
        "TL Fiyat",
        "Türkçe İsim",
        "Türkçe Kategori Ağacı"
    ]
    
    print("CSV dosyası okunuyor...")
    
    try:
        df = pd.read_csv(input_file, low_memory=False)
        print(f"Toplam satır sayısı (önce): {len(df)}")
    except FileNotFoundError:
        print(f"Hata: '{input_file}' dosyası bulunamadı!")
        sys.exit(1)
    except Exception as e:
        print(f"Hata: Dosya okuma hatası - {e}")
        sys.exit(1)
    
    # Eksik sütunları kontrol et
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"\nHata: Aşağıdaki sütunlar bulunamadı:")
        for col in missing_columns:
            print(f"  - {col}")
        print(f"\nMevcut sütunlar: {', '.join(df.columns)}")
        sys.exit(1)
    
    print(f"\nKontrol edilecek sütunlar ({len(required_columns)} adet):")
    for col in required_columns:
        print(f"  - {col}")
    
    # Her sütun için eksik değer sayısını göster
    print(f"\nEksik değer analizi:")
    for col in required_columns:
        missing_count = df[col].isna().sum() + (df[col].astype(str).str.strip() == '').sum()
        print(f"  {col}: {missing_count} eksik")
    
    # Tüm sütunların dolu olduğu satırları filtrele
    # NaN ve boş string'leri kontrol et
    mask = pd.Series([True] * len(df))
    
    for col in required_columns:
        # NaN veya boş string kontrolü
        mask = mask & df[col].notna() & (df[col].astype(str).str.strip() != '')
    
    df_filtered = df[mask].copy()
    
    removed_count = len(df) - len(df_filtered)
    
    print(f"\n=== SONUÇ ===")
    print(f"Önceki satır sayısı: {len(df)}")
    print(f"Silinen satır sayısı: {removed_count}")
    print(f"Kalan satır sayısı (tüm sütunlar dolu): {len(df_filtered)}")
    
    # Sonuçları kaydet
    df_filtered.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nFiltrelenmiş veriler '{output_file}' dosyasına kaydedildi.")
    
    return df_filtered

if __name__ == "__main__":
    filter_complete_rows()
