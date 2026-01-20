#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Argos Translate ile Türkçe Çeviri Scripti - Total Products
Title ve Categories: Tree sütunlarını offline olarak Türkçe'ye çevirir.
"""

import pandas as pd
import sys
import time
from argostranslate import translate

def ensure_argos_models():
    """EN->TR ve DE->TR modellerinin yüklü olduğundan emin ol"""
    from argostranslate import package
    
    print("Argos Translate modelleri kontrol ediliyor...")
    
    # Yüklü paketleri listele
    installed_packages = package.get_installed_packages()
    installed_languages = {pkg.from_code: pkg.to_code for pkg in installed_packages}
    
    # EN->TR modeli kontrol et
    en_to_tr_installed = any(
        pkg.from_code == 'en' and pkg.to_code == 'tr' 
        for pkg in installed_packages
    )
    
    if not en_to_tr_installed:
        print("EN->TR modeli bulunamadı. Yükleniyor...")
        try:
            available_packages = package.get_available_packages()
            en_to_tr_pkg = [pkg for pkg in available_packages 
                          if pkg.from_code == 'en' and pkg.to_code == 'tr'][0]
            package.install_from_path(en_to_tr_pkg.download())
            print("✓ EN->TR modeli yüklendi")
        except Exception as e:
            print(f"EN->TR modeli yüklenirken hata: {e}")
            print("Manuel yükleme için: argostranslate --update-languages")
            return None
    
    # Translator oluştur
    try:
        translator = translate.get_translation_from_codes('en', 'tr')
        if translator is None:
            print("EN->TR translator oluşturulamadı!")
            return None
        print("✓ EN->TR translator hazır")
        return translator
    except Exception as e:
        print(f"Translator oluşturulurken hata: {e}")
        return None

def build_unique(series: pd.Series) -> list:
    """Benzersiz değerleri çıkar"""
    return (
        series.dropna()
        .astype(str)
        .map(lambda s: s.strip())
        .loc[lambda s: s != ""]
        .unique()
        .tolist()
    )

def translate_uniques(translator, uniques: list, label: str = "") -> dict:
    """Benzersiz değerleri çevir"""
    result = {}
    total = len(uniques)
    
    print(f"[{label}] Başlıyor | toplam benzersiz={total}")
    
    for i, orig in enumerate(uniques, start=1):
        try:
            translated = translator.translate(orig)
            result[orig] = translated
        except Exception as e:
            print(f"[{label}] Çeviri hatası [{i}/{total}]: {e}")
            result[orig] = None
        
        if i % 100 == 0:
            print(f"[{label}] İlerleme {i}/{total} | ok={sum(1 for v in result.values() if v is not None)} fail={sum(1 for v in result.values() if v is None)}")
    
    return result

def main():
    input_file = "total products merged.csv"
    output_file = "total products merged.csv"
    
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
    required_columns = ['Title', 'Categories: Tree']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Hata: Eksik sütunlar: {', '.join(missing_columns)}")
        sys.exit(1)
    
    # Argos Translate modelini hazırla
    translator = ensure_argos_models()
    if translator is None:
        print("Hata: Translator oluşturulamadı!")
        sys.exit(1)
    
    # Benzersiz değerleri çıkar
    print("\nBenzersiz değerler çıkarılıyor...")
    unique_titles = build_unique(df['Title'])
    unique_categories = build_unique(df['Categories: Tree'])
    
    print(f"Benzersiz Title: {len(unique_titles)}")
    print(f"Benzersiz Category: {len(unique_categories)}")
    
    # Çevirileri yap
    print("\n" + "="*50)
    print("Title çevirileri başlıyor...")
    title_map = translate_uniques(translator, unique_titles, "Title EN->TR")
    
    print("\n" + "="*50)
    print("Category çevirileri başlıyor...")
    category_map = translate_uniques(translator, unique_categories, "Category EN->TR")
    
    # Map uygula
    print("\nÇeviriler uygulanıyor...")
    df['Türkçe İsim'] = df['Title'].astype(str).map(title_map)
    df['Türkçe Kategori Ağacı'] = df['Categories: Tree'].astype(str).map(category_map)
    
    print(f"\n=== SONUÇ ===")
    print(f"Başarıyla çevrilen Title: {df['Türkçe İsim'].notna().sum()} / {len(df)}")
    print(f"Başarıyla çevrilen Category: {df['Türkçe Kategori Ağacı'].notna().sum()} / {len(df)}")
    
    # Örnek göster
    print(f"\n=== ÖRNEK ÇEVİRİLER ===")
    sample_df = df[df['Türkçe İsim'].notna()].head(3)
    for idx, row in sample_df.iterrows():
        print(f"\nOrijinal: {row['Title'][:80]}...")
        print(f"Türkçe: {row['Türkçe İsim'][:80]}...")
    
    # Kaydet
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ Sonuçlar '{output_file}' dosyasına kaydedildi.")
    print(f"Yeni sütunlar: 'Türkçe İsim', 'Türkçe Kategori Ağacı'")

if __name__ == "__main__":
    main()
