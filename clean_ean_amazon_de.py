#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EAN Sütunu Temizleme Scripti - Amazon DE Merged
- EAN boş olan satırları siler
- Birden fazla EAN içeren satırlardan sadece birini tutar
- Aynı EAN koduna sahip duplicate satırları temizler
"""

import pandas as pd
import sys

def clean_ean_column():
    input_file = "amazon de merged.csv"
    output_file = "amazon de merged.csv"
    
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
    
    if 'Product Codes: EAN' not in df.columns:
        print("Hata: 'Product Codes: EAN' sütunu bulunamadı!")
        print(f"Mevcut sütunlar: {', '.join(df.columns)}")
        sys.exit(1)
    
    # 1. EAN boş olan satırları sil
    print("\n[1/3] EAN boş olan satırlar siliniyor...")
    empty_before = len(df)
    df = df[df['Product Codes: EAN'].notna()].copy()
    df = df[df['Product Codes: EAN'].astype(str).str.strip() != ''].copy()
    empty_removed = empty_before - len(df)
    print(f"  ✓ {empty_removed} satır silindi (EAN boş)")
    print(f"  Kalan satır: {len(df)}")
    
    # 2. Birden fazla EAN içeren satırlardan sadece ilkini tut
    print("\n[2/3] Birden fazla EAN içeren satırlar temizleniyor...")
    
    def get_first_ean(ean_str):
        """Birden fazla EAN varsa (virgülle ayrılmış) sadece ilkini döndür"""
        if pd.isna(ean_str):
            return None
        ean_str = str(ean_str).strip()
        if ',' in ean_str:
            # Virgülle ayrılmış, ilkini al
            first_ean = ean_str.split(',')[0].strip()
            return first_ean
        return ean_str
    
    df['Product Codes: EAN'] = df['Product Codes: EAN'].apply(get_first_ean)
    
    # Tekrar boş kontrolü (virgülle ayrılmış ama ilki boş olabilir)
    df = df[df['Product Codes: EAN'].notna()].copy()
    df = df[df['Product Codes: EAN'].astype(str).str.strip() != ''].copy()
    
    # 3. Aynı EAN koduna sahip duplicate satırları temizle (sadece birini tut)
    print("\n[3/3] Aynı EAN koduna sahip duplicate satırlar temizleniyor...")
    duplicates_before = len(df)
    df = df.drop_duplicates(subset=['Product Codes: EAN'], keep='first')
    duplicates_removed = duplicates_before - len(df)
    
    print(f"\n=== SONUÇ ===")
    print(f"Önceki satır sayısı: {empty_before}")
    print(f"EAN boş olanlar silindi: {empty_removed}")
    print(f"Duplicate EAN'ler temizlendi: {duplicates_removed}")
    print(f"Final satır sayısı: {len(df)}")
    
    # Sonuçları kaydet
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ Temizlenmiş veriler '{output_file}' dosyasına kaydedildi.")
    
    return df

if __name__ == "__main__":
    clean_ean_column()
