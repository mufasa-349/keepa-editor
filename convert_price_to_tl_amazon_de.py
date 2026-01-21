#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fiyat Dönüştürme Scripti - Amazon DE Merged
List Price: Current sütunundaki değerleri 50.2 ile çarparak TL Fiyat sütunu oluşturur.
"""

import pandas as pd
import sys

def convert_to_tl():
    input_file = "amazon de merged.csv"
    output_file = "amazon de merged.csv"
    
    # Döviz kuru
    EUR_TO_TL = 50.2
    
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
    
    def convert_price(price_value):
        """
        Fiyat değerini TL'ye çevirir.
        """
        if pd.isna(price_value):
            return None
        
        try:
            # String ise temizle ve float'a çevir
            if isinstance(price_value, str):
                price_value = price_value.strip()
                if price_value == '':
                    return None
                price_value = float(price_value)
            
            # TL'ye çevir
            tl_price = price_value * EUR_TO_TL
            return round(tl_price, 2)
        except (ValueError, TypeError):
            return None
    
    print("\nFiyatlar TL'ye çevriliyor...")
    
    # Yeni TL fiyat sütunu oluştur
    df['TL Fiyat'] = df['List Price: Current'].apply(convert_price)
    
    # İstatistikler
    total_rows = len(df)
    converted_count = df['TL Fiyat'].notna().sum()
    empty_count = total_rows - converted_count
    
    print(f"\n=== DÖNÜŞTÜRME İSTATİSTİKLERİ ===")
    print(f"Toplam satır: {total_rows}")
    print(f"Başarıyla dönüştürülen: {converted_count}")
    print(f"Boş/geçersiz fiyat: {empty_count}")
    
    # Örnek sonuçları göster
    print(f"\n=== ÖRNEK DÖNÜŞTÜRMELER ===")
    sample_df = df[df['TL Fiyat'].notna()].head(5)
    for idx, row in sample_df.iterrows():
        original = row['List Price: Current']
        tl_price = row['TL Fiyat']
        print(f"{original} EUR -> {tl_price} TL")
    
    # Sonuçları kaydet
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ Sonuçlar '{output_file}' dosyasına kaydedildi.")
    print(f"Yeni 'TL Fiyat' sütunu eklendi.")
    
    return df

if __name__ == "__main__":
    convert_to_tl()
