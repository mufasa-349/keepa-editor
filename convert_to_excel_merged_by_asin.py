#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV'den Excel'e Dönüştürme Scripti - Merged by ASIN
merged_by_asin.csv dosyasını Excel formatına (.xlsx) çevirir.
"""

import pandas as pd
import sys

def convert_to_excel():
    input_file = "merged_by_asin.csv"
    output_file = "merged_by_asin.xlsx"
    
    print("CSV dosyası okunuyor...")
    
    try:
        df = pd.read_csv(input_file, low_memory=False)
        print(f"Toplam satır sayısı: {len(df)}")
        print(f"Sütun sayısı: {len(df.columns)}")
        print(f"Sütunlar: {', '.join(df.columns)}")
    except FileNotFoundError:
        print(f"Hata: '{input_file}' dosyası bulunamadı!")
        sys.exit(1)
    except Exception as e:
        print(f"Hata: Dosya okuma hatası - {e}")
        sys.exit(1)
    
    print(f"\nExcel dosyası oluşturuluyor: {output_file}")
    
    try:
        # Excel'e yaz (openpyxl engine kullan)
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"✓ Excel dosyası başarıyla oluşturuldu: {output_file}")
        print(f"  - Satır sayısı: {len(df)}")
        print(f"  - Sütun sayısı: {len(df.columns)}")
    except ImportError:
        print("\nHata: 'openpyxl' kütüphanesi bulunamadı!")
        print("Yüklemek için: pip install openpyxl")
        sys.exit(1)
    except Exception as e:
        print(f"\nHata: Excel dosyası oluşturulurken hata oluştu - {e}")
        sys.exit(1)
    
    return df

if __name__ == "__main__":
    convert_to_excel()
