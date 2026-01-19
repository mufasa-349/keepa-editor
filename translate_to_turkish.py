#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Türkçe Çeviri Scripti
Title ve Categories: Tree sütunlarını Türkçe'ye çevirir.
"""

import pandas as pd
import re
import sys
import time
from deep_translator import GoogleTranslator

def clean_title_before_translation(title):
    """
    Çeviriden önce "Renewed" ve "refurbished" kelimelerini kaldırır.
    """
    if pd.isna(title) or title == '':
        return title
    
    title = str(title)
    
    # Renewed ve refurbished kelimelerini kaldır (case-insensitive)
    title = re.sub(r'\b(Renewed|renewed|REFURBISHED|refurbished)\b', '', title, flags=re.IGNORECASE)
    
    # Fazla boşlukları temizle
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title

def clean_translated_text(text):
    """
    Çevrilmiş metinden "yenilenmiş" kelimesini kaldırır.
    """
    if pd.isna(text) or text == '':
        return text
    
    text = str(text)
    
    # "yenilenmiş" kelimesini kaldır (case-insensitive)
    text = re.sub(r'\b(yenilenmiş|Yenilenmiş|YENİLENMİŞ)\b', '', text, flags=re.IGNORECASE)
    
    # Fazla boşlukları temizle
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def translate_to_turkish():
    input_file = "merged_lego_products.csv"
    output_file = "merged_lego_products.csv"
    
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
    
    # Gerekli sütunları kontrol et
    required_columns = ['Locale', 'Title', 'Categories: Tree']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Hata: Eksik sütunlar: {', '.join(missing_columns)}")
        sys.exit(1)
    
    # Yeni sütunlar için listeler
    turkish_titles = []
    turkish_categories = []
    
    print("\nÇeviri başlatılıyor...")
    print("Bu işlem biraz zaman alabilir (4500+ satır)...")
    
    total = len(df)
    for idx, row in df.iterrows():
        locale = str(row['Locale']).lower()
        title = row['Title']
        category = row['Categories: Tree']
        
        # Kaynak dili belirle
        source_lang = 'en' if locale == 'com' else 'de'
        
        # Translator oluştur (her satır için yeniden oluşturulabilir)
        try:
            translator = GoogleTranslator(source=source_lang, target='tr')
        except Exception as e:
            print(f"  Satır {idx+1}: Translator oluşturma hatası - {e}")
            turkish_titles.append(None)
            turkish_categories.append(None)
            continue
        
        # Title çevirisi
        turkish_title = None
        if pd.notna(title) and title != '':
            # Önce "Renewed" ve "refurbished" kelimelerini kaldır
            cleaned_title = clean_title_before_translation(title)
            
            if cleaned_title and cleaned_title.strip():
                try:
                    # Çevir
                    turkish_title = translator.translate(cleaned_title)
                    
                    # Çevrilmiş metinden "yenilenmiş" kelimesini kaldır
                    turkish_title = clean_translated_text(turkish_title)
                except Exception as e:
                    print(f"  Satır {idx+1}: Title çeviri hatası - {e}")
                    turkish_title = None
                    time.sleep(1)  # Rate limiting için bekle
            else:
                turkish_title = None
        else:
            turkish_title = None
        
        # Category çevirisi
        turkish_category = None
        if pd.notna(category) and category != '':
            try:
                # Kategori ağacını çevir
                turkish_category = translator.translate(str(category))
            except Exception as e:
                print(f"  Satır {idx+1}: Category çeviri hatası - {e}")
                turkish_category = None
                time.sleep(1)  # Rate limiting için bekle
        else:
            turkish_category = None
        
        turkish_titles.append(turkish_title)
        turkish_categories.append(turkish_category)
        
        # İlerleme göster
        if (idx + 1) % 100 == 0:
            print(f"  İlerleme: {idx + 1}/{total} satır çevrildi...")
        
        # Rate limiting - API limitlerini aşmamak için
        # Her 50 çeviride bir daha uzun bekle
        if (idx + 1) % 50 == 0:
            time.sleep(2)
        else:
            time.sleep(0.2)
    
    # Yeni sütunları ekle
    df['Türkçe İsim'] = turkish_titles
    df['Türkçe Kategori Ağacı'] = turkish_categories
    
    print(f"\nÇeviri tamamlandı!")
    print(f"Başarıyla çevrilen title sayısı: {df['Türkçe İsim'].notna().sum()}")
    print(f"Başarıyla çevrilen category sayısı: {df['Türkçe Kategori Ağacı'].notna().sum()}")
    
    # Örnek sonuçları göster
    print(f"\n=== ÖRNEK ÇEVİRİLER ===")
    sample_df = df[df['Türkçe İsim'].notna()].head(5)
    for idx, row in sample_df.iterrows():
        print(f"\nOrijinal: {row['Title']}")
        print(f"Türkçe: {row['Türkçe İsim']}")
        print(f"Kategori: {row['Türkçe Kategori Ağacı']}")
        print("-" * 50)
    
    # Sonuçları kaydet
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nSonuçlar '{output_file}' dosyasına kaydedildi.")
    print(f"Yeni 'Türkçe İsim' ve 'Türkçe Kategori Ağacı' sütunları eklendi.")
    
    return df

if __name__ == "__main__":
    translate_to_turkish()
