#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sütun Filtreleme Scripti
Sadece belirtilen sütunları tutar, diğerlerini siler.
"""

import pandas as pd
import sys

def filter_columns():
    input_file = "merged_lego_products.csv"
    output_file = "merged_lego_products.csv"  # Aynı dosyaya kaydet
    
    # Tutulacak sütunlar
    columns_to_keep = [
        "Locale",
        "Image",
        "Title",
        "List Price: Current",
        "Categories: Tree",
        "ASIN",
        "Brand"
    ]
    
    print("CSV dosyası okunuyor...")
    
    try:
        df = pd.read_csv(input_file, low_memory=False)
        print(f"Toplam sütun sayısı: {len(df.columns)}")
        print(f"Toplam satır sayısı: {len(df)}")
    except FileNotFoundError:
        print(f"Hata: '{input_file}' dosyası bulunamadı!")
        sys.exit(1)
    except Exception as e:
        print(f"Hata: Dosya okuma hatası - {e}")
        sys.exit(1)
    
    # Mevcut sütunları kontrol et
    missing_columns = [col for col in columns_to_keep if col not in df.columns]
    if missing_columns:
        print(f"\nUyarı: Aşağıdaki sütunlar bulunamadı:")
        for col in missing_columns:
            print(f"  - {col}")
        print("\nMevcut sütunlar:")
        for col in df.columns[:20]:
            print(f"  - {col}")
        if len(df.columns) > 20:
            print(f"  ... ve {len(df.columns) - 20} sütun daha")
    
    # Sadece mevcut sütunları filtrele
    available_columns = [col for col in columns_to_keep if col in df.columns]
    
    if not available_columns:
        print("\nHata: Hiçbir istenen sütun bulunamadı!")
        sys.exit(1)
    
    # Sadece belirtilen sütunları seç
    df_filtered = df[available_columns].copy()
    
    print(f"\nFiltrelenmiş sütun sayısı: {len(df_filtered.columns)}")
    print(f"Tutulan sütunlar: {', '.join(df_filtered.columns)}")
    
    # Sonuçları kaydet
    df_filtered.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nFiltrelenmiş veriler '{output_file}' dosyasına kaydedildi.")
    print(f"Toplam ürün sayısı: {len(df_filtered)}")
    
    return df_filtered

if __name__ == "__main__":
    filter_columns()
