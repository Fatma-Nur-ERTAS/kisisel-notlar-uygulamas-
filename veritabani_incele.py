import sqlite3
import os

def veritabani_oku(dosya_adi, tablo_adi):
    if os.path.exists(dosya_adi):
        print(f"\n📂 {dosya_adi} veritabanı bulundu.")
        con = sqlite3.connect(dosya_adi)
        cur = con.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablolar = cur.fetchall()
        print("🔍 Tablolar:", tablolar)

        if (tablo_adi,) in tablolar:
            print(f"\n📄 '{tablo_adi}' tablosunun içeriği:")
            cur.execute(f"SELECT * FROM {tablo_adi}")
            satirlar = cur.fetchall()
            if satirlar:
                for sira, row in enumerate(satirlar, 1):
                    print(f"{sira}. {row}")
            else:
                print("Tabloda hiç veri yok.")
        else:
            print(f"⚠️ Tablo bulunamadı: {tablo_adi}")

        con.close()
    else:
        print(f"🚫 {dosya_adi} veritabanı bulunamadı!")

veritabani_oku("kullanicilar.db", "users")
veritabani_oku("notlar.db", "notlar")
