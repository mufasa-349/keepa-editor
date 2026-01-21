#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sütun Silme Scripti - Merged by ASIN
Belirtilen sütunları merged_by_asin.csv dosyasından siler.
"""

import pandas as pd
import sys

def remove_columns():
    input_file = "merged_by_asin.csv"
    output_file = "merged_by_asin.csv"
    
    # Silinecek sütunlar
    columns_to_remove = [
        "Categories: Tree",
        "List Price: Current",
        "Reviews: Rating Count",
        "Title"
    ]
    
    print("CSV dosyası okunuyor...")
    
    try:
        df = pd.read_csv(input_file, low_memory=False)
        print(f"Toplam satır sayısı: {len(df)}")
        print(f"Önceki sütun sayısı: {len(df.columns)}")
        print(f"Önceki sütunlar: {', '.join(df.columns)}")
    except FileNotFoundError:
        print(f"Hata: '{input_file}' dosyası bulunamadı!")
        sys.exit(1)
    except Exception as e:
        print(f"Hata: Dosya okuma hatası - {e}")
        sys.exit(1)
    
    # Mevcut sütunları kontrol et
    existing_columns = [col for col in columns_to_remove if col in df.columns]
    missing_columns = [col for col in columns_to_remove if col not in df.columns]
    
    if missing_columns:
        print(f"\nUyarı: Aşağıdaki sütunlar bulunamadı (zaten silinmiş olabilir):")
        for col in missing_columns:
            print(f"  - {col}")
    
    if not existing_columns:
        print("\nUyarı: Silinecek hiçbir sütun bulunamadı!")
        print("Tüm sütunlar zaten silinmiş olabilir.")
        return df
    
    # Sütunları sil
    df = df.drop(columns=existing_columns)
    
    print(f"\nSilinen sütunlar ({len(existing_columns)} adet):")
    for col in existing_columns:
        print(f"  ✓ {col}")
    
    print(f"\nYeni sütun sayısı: {len(df.columns)}")
    print(f"Kalan sütunlar: {', '.join(df.columns)}")
    
    # Sonuçları kaydet
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ Sonuçlar '{output_file}' dosyasına kaydedildi.")
    print(f"Toplam ürün sayısı: {len(df)}")
    
    return df

if __name__ == "__main__":
    remove_columns()
