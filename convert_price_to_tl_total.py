#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fiyat Dönüştürme Scripti - Total Products
List Price: Current sütunundaki fiyatları TL'ye çevirir.
"""

import pandas as pd
import re
import sys

def convert_to_tl():
    input_file = "total products merged.csv"
    output_file = "total products merged.csv"
    
    # Döviz kuru
    USD_TO_TL = 43.6
    
    print("CSV dosyası okunuyor...")
    
    try:
        df = pd.read_csv(input_file, low_memory=False)
        print(f"Toplam satır sayısı: {len(df)}")
    except FileNotFoundError:
        print(f"Hata: '{input_file}' dosyası bulunamadı!")
        sys.exit(1)
    except Exception as e:
        print(f"Hata: Dosya okuma hatası - {e}")
        sys.exit(1)
    
    if 'List Price: Current' not in df.columns:
        print("Hata: 'List Price: Current' sütunu bulunamadı!")
        print(f"Mevcut sütunlar: {', '.join(df.columns)}")
        sys.exit(1)
    
    def parse_and_convert_price(price_str):
        """
        Fiyat string'ini parse edip TL'ye çevirir.
        Örnek: "124.95 -409" -> 124.95 * 43.6 = 5447.82
        """
        if pd.isna(price_str) or price_str == '':
            return None
        
        price_str = str(price_str).strip()
        
        # USD kontrolü (-409)
        if '-409' in price_str:
            # Fiyatı çıkar
            match = re.search(r'([\d.]+)\s*-409', price_str)
            if match:
                try:
                    usd_price = float(match.group(1))
                    tl_price = usd_price * USD_TO_TL
                    return round(tl_price, 2)
                except ValueError:
                    return None
        
        # Bilinmeyen format veya boş
        return None
    
    print("\nFiyatlar TL'ye çevriliyor...")
    
    # Yeni TL fiyat sütunu oluştur
    df['TL Fiyatı'] = df['List Price: Current'].apply(parse_and_convert_price)
    
    # İstatistikler
    total_rows = len(df)
    converted_count = df['TL Fiyatı'].notna().sum()
    usd_count = df['List Price: Current'].astype(str).str.contains('-409', na=False).sum()
    empty_count = total_rows - converted_count
    
    print(f"\n=== DÖNÜŞTÜRME İSTATİSTİKLERİ ===")
    print(f"Toplam satır: {total_rows}")
    print(f"USD fiyat sayısı (-409): {usd_count}")
    print(f"Başarıyla dönüştürülen: {converted_count}")
    print(f"Boş/geçersiz fiyat: {empty_count}")
    
    # Örnek sonuçları göster
    print(f"\n=== ÖRNEK DÖNÜŞTÜRMELER ===")
    sample_df = df[df['TL Fiyatı'].notna()].head(5)
    for idx, row in sample_df.iterrows():
        original = row['List Price: Current']
        tl_price = row['TL Fiyatı']
        print(f"{original} -> {tl_price} TL")
    
    # Sonuçları kaydet
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ Sonuçlar '{output_file}' dosyasına kaydedildi.")
    print(f"Yeni 'TL Fiyatı' sütunu eklendi.")
    
    return df

if __name__ == "__main__":
    convert_to_tl()
