#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Translate ile Türkçe Çeviri Scripti - Amazon DE Merged
Title ve Categories: Tree sütunlarını Almanca'dan Türkçe'ye çevirir.
Cache/dedup kullanarak hızlı çeviri yapar.
Her 100 çeviride bir ara kayıt yapar, progress korunur.
"""

import pandas as pd
import sys
import time
import json
import os
from googletrans import Translator

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

def load_progress(progress_file: str) -> dict:
    """Önceki progress'i yükle"""
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_progress(progress_file: str, result: dict):
    """Progress'i kaydet"""
    try:
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Progress kaydetme hatası: {e}")

def translate_uniques(translator, uniques: list, src: str, dest: str, label: str = "", progress_file: str = None) -> dict:
    """Benzersiz değerleri çevir (progress korumalı)"""
    # Progress dosyası adı
    if progress_file is None:
        progress_file = f"progress_{label.replace(' ', '_').replace('->', '_')}.json"
    
    # Önceki progress'i yükle
    result = load_progress(progress_file)
    print(f"[{label}] Önceki progress: {len(result)}/{len(uniques)} çevrilmiş")
    
    # Zaten çevrilmiş olanları atla
    remaining = [u for u in uniques if u not in result]
    total = len(uniques)
    start_idx = len(result)
    
    print(f"[{label}] Başlıyor | src={src} dest={dest} | toplam benzersiz={total} | kalan={len(remaining)}")
    
    for i, orig in enumerate(remaining, start=1):
        global_idx = start_idx + i
        try:
            translated = translator.translate(orig, src=src, dest=dest)
            result[orig] = translated.text
        except Exception as e:
            print(f"[{label}] Çeviri hatası [{global_idx}/{total}]: {e}")
            result[orig] = None
            # Hata durumunda translator'ı yeniden oluştur
            try:
                translator = Translator()
            except:
                pass
            time.sleep(1)
        
        # Her 25'te bir ilerleme göster
        if global_idx % 25 == 0:
            ok_count = sum(1 for v in result.values() if v is not None)
            fail_count = sum(1 for v in result.values() if v is None)
            elapsed = time.time() - start_time if 'start_time' in globals() else 0
            if elapsed > 0 and ok_count > 0:
                speed = ok_count / elapsed
                remaining_count = total - global_idx
                remaining_time = remaining_count / speed if speed > 0 else 0
                print(f"[{label}] İlerleme {global_idx}/{total} | ok={ok_count} fail={fail_count} | hız={speed:.2f}/sn | kalan~{remaining_time/60:.1f} dk")
            else:
                print(f"[{label}] İlerleme {global_idx}/{total} | ok={ok_count} fail={fail_count}")
        
        # Her 100'de bir progress kaydet
        if global_idx % 100 == 0:
            save_progress(progress_file, result)
            print(f"[{label}] ✓ Ara kayıt yapıldı ({global_idx}/{total})")
        
        # Rate limiting
        if global_idx % 50 == 0:
            time.sleep(2)
        else:
            time.sleep(0.2)
    
    # Final kayıt
    save_progress(progress_file, result)
    print(f"[{label}] ✓ Final kayıt yapıldı")
    
    return result

def main():
    input_file = "amazon de merged.csv"
    output_file = "amazon de merged.csv"
    
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
    
    # Translator oluştur
    translator = Translator()
    
    # Benzersiz değerleri çıkar
    print("\nBenzersiz değerler çıkarılıyor...")
    unique_titles = build_unique(df['Title'])
    unique_categories = build_unique(df['Categories: Tree'])
    
    print(f"Benzersiz Title: {len(unique_titles)}")
    print(f"Benzersiz Category: {len(unique_categories)}")
    
    # Çevirileri yap
    global start_time
    start_time = time.time()
    
    print("\n" + "="*50)
    print("Title çevirileri başlıyor (DE->TR)...")
    title_map = translate_uniques(translator, unique_titles, src='de', dest='tr', label="Title DE->TR", progress_file="progress_title_de_tr.json")
    
    # Ara kayıt: Title çevirilerini uygula ve kaydet
    print("\n[Ara kayıt] Title çevirileri uygulanıyor ve kaydediliyor...")
    df['Türkçe İsim'] = df['Title'].astype(str).map(title_map)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✓ Ara kayıt yapıldı: {output_file}")
    
    print("\n" + "="*50)
    print("Category çevirileri başlıyor (DE->TR)...")
    category_map = translate_uniques(translator, unique_categories, src='de', dest='tr', label="Category DE->TR", progress_file="progress_category_de_tr.json")
    
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
    
    # Final kayıt
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ Final sonuçlar '{output_file}' dosyasına kaydedildi.")
    print(f"Yeni sütunlar: 'Türkçe İsim', 'Türkçe Kategori Ağacı'")
    
    # Progress dosyalarını temizle (opsiyonel)
    # os.remove("progress_title_de_tr.json")
    # os.remove("progress_category_de_tr.json")

if __name__ == "__main__":
    main()
