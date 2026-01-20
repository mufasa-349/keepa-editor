#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Total Products Birleştirme Scripti
Total Products.csv ve KeepaExport dosyasını birleştirir.
"""

import pandas as pd
import sys

def merge_total_products():
    file1 = "Total Products.csv"
    file2 = "KeepaExport-2026-01-20-ProductFinder (1).csv"
    output_file = "total products merged.csv"
    
    print("CSV dosyaları okunuyor...")
    
    try:
        df1 = pd.read_csv(file1, low_memory=False)
        print(f"✓ {file1}: {len(df1)} satır, {len(df1.columns)} sütun")
    except FileNotFoundError:
        print(f"Hata: '{file1}' dosyası bulunamadı!")
        sys.exit(1)
    except Exception as e:
        print(f"Hata: {file1} okuma hatası - {e}")
        sys.exit(1)
    
    try:
        df2 = pd.read_csv(file2, low_memory=False)
        print(f"✓ {file2}: {len(df2)} satır, {len(df2.columns)} sütun")
    except FileNotFoundError:
        print(f"Hata: '{file2}' dosyası bulunamadı!")
        sys.exit(1)
    except Exception as e:
        print(f"Hata: {file2} okuma hatası - {e}")
        sys.exit(1)
    
    # Sütun yapılarını kontrol et
    cols1 = set(df1.columns)
    cols2 = set(df2.columns)
    
    if cols1 != cols2:
        print(f"\nUyarı: Sütun yapıları farklı!")
        print(f"  {file1} sütunları: {len(cols1)} adet")
        print(f"  {file2} sütunları: {len(cols2)} adet")
        
        # Ortak sütunları bul
        common_cols = cols1.intersection(cols2)
        only_in_1 = cols1 - cols2
        only_in_2 = cols2 - cols1
        
        if only_in_1:
            print(f"\n  Sadece {file1}'de: {', '.join(only_in_1)}")
        if only_in_2:
            print(f"\n  Sadece {file2}'de: {', '.join(only_in_2)}")
        
        # Ortak sütunlarla birleştir
        print(f"\nOrtak sütunlarla birleştiriliyor ({len(common_cols)} sütun)...")
        df1 = df1[list(common_cols)]
        df2 = df2[list(common_cols)]
    
    # Birleştir
    print(f"\nDosyalar birleştiriliyor...")
    df_merged = pd.concat([df1, df2], ignore_index=True)
    
    print(f"\n=== SONUÇ ===")
    print(f"İlk dosya: {len(df1)} satır")
    print(f"İkinci dosya: {len(df2)} satır")
    print(f"Birleştirilmiş toplam: {len(df_merged)} satır")
    print(f"Sütun sayısı: {len(df_merged.columns)}")
    
    # Duplicate kontrolü ve temizleme (ASIN varsa)
    if 'ASIN' in df_merged.columns:
        duplicates_before = df_merged['ASIN'].duplicated().sum()
        if duplicates_before > 0:
            print(f"\nDuplicate ASIN bulundu: {duplicates_before} adet")
            print(f"Temizleniyor... (ilk olanlar tutulacak)")
            
            # Duplicate'leri sil (keep='first' ile ilk olanı tut)
            df_merged = df_merged.drop_duplicates(subset=['ASIN'], keep='first')
            
            duplicates_after = df_merged['ASIN'].duplicated().sum()
            print(f"✓ Temizlendi: {duplicates_before} duplicate satır silindi")
            print(f"  Önceki satır sayısı: {len(df_merged) + duplicates_before}")
            print(f"  Yeni satır sayısı: {len(df_merged)}")
        else:
            print(f"\n✓ Duplicate ASIN yok (tüm ürünler benzersiz)")
    
    # Sonuçları kaydet
    df_merged.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ Birleştirilmiş dosya kaydedildi: {output_file}")
    
    return df_merged

if __name__ == "__main__":
    merge_total_products()
