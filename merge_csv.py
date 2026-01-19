#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV Birleştirme Scripti
İki CSV dosyasını birleştirir, aynı ASIN'li kayıtlarda Amazon.com olanı tercih eder.
"""

import pandas as pd
import sys
from pathlib import Path

def merge_csv_files():
    # Dosya yolları
    file_com = "Amazon com - Lego -75 -1000 usd.csv"
    file_de = "Amazon de store and brand name lego 75 -1000 .csv"
    output_file = "merged_lego_products.csv"
    
    print("CSV dosyaları okunuyor...")
    
    # CSV dosyalarını oku
    try:
        df_com = pd.read_csv(file_com, low_memory=False)
        df_de = pd.read_csv(file_de, low_memory=False)
        print(f"Amazon.com dosyası: {len(df_com)} ürün")
        print(f"Amazon.de dosyası: {len(df_de)} ürün")
    except FileNotFoundError as e:
        print(f"Hata: Dosya bulunamadı - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Hata: Dosya okuma hatası - {e}")
        sys.exit(1)
    
    # ASIN sütununu kontrol et
    if 'ASIN' not in df_com.columns or 'ASIN' not in df_de.columns:
        print("Hata: ASIN sütunu bulunamadı!")
        print(f"Amazon.com sütunları: {list(df_com.columns)[:10]}...")
        print(f"Amazon.de sütunları: {list(df_de.columns)[:10]}...")
        sys.exit(1)
    
    # Locale sütununu kontrol et ve ekle (yoksa)
    if 'Locale' not in df_com.columns:
        df_com['Locale'] = 'com'
    if 'Locale' not in df_de.columns:
        df_de['Locale'] = 'de'
    
    print("\nASIN'ler kontrol ediliyor...")
    
    # Her iki dosyadaki ASIN'leri al
    asin_com = set(df_com['ASIN'].dropna())
    asin_de = set(df_de['ASIN'].dropna())
    
    # Ortak ASIN'leri bul
    common_asins = asin_com.intersection(asin_de)
    print(f"Ortak ASIN sayısı: {len(common_asins)}")
    print(f"Sadece Amazon.com'da olan: {len(asin_com - asin_de)}")
    print(f"Sadece Amazon.de'de olan: {len(asin_de - asin_com)}")
    
    # Amazon.de'den ortak ASIN'leri çıkar (sadece Amazon.com olanları tutacağız)
    df_de_unique = df_de[~df_de['ASIN'].isin(common_asins)].copy()
    
    # Amazon.com'dan ortak ASIN'leri al
    df_com_common = df_com[df_com['ASIN'].isin(common_asins)].copy()
    
    # Amazon.com'dan sadece kendisinde olan ASIN'leri al
    df_com_unique = df_com[~df_com['ASIN'].isin(asin_de)].copy()
    
    # Birleştir: Amazon.com'dan ortak ve unique, Amazon.de'den sadece unique
    merged_df = pd.concat([
        df_com_common,  # Ortak ASIN'ler (Amazon.com'dan)
        df_com_unique,  # Sadece Amazon.com'da olanlar
        df_de_unique    # Sadece Amazon.de'de olanlar
    ], ignore_index=True)
    
    # ASIN'e göre sırala (opsiyonel)
    merged_df = merged_df.sort_values('ASIN').reset_index(drop=True)
    
    print(f"\nBirleştirilmiş toplam ürün sayısı: {len(merged_df)}")
    
    # Sonuçları kaydet
    merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nSonuçlar '{output_file}' dosyasına kaydedildi.")
    
    # Özet bilgiler
    print("\n=== ÖZET ===")
    print(f"Toplam ürün sayısı: {len(merged_df)}")
    print(f"Amazon.com kaynaklı: {len(df_com_common) + len(df_com_unique)}")
    print(f"Amazon.de kaynaklı: {len(df_de_unique)}")
    print(f"Ortak ASIN'ler (Amazon.com tercih edildi): {len(common_asins)}")
    
    return merged_df

if __name__ == "__main__":
    merge_csv_files()
