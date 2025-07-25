import sqlite3
import os
import bcrypt

DB_DOSYA = "kullanicilar.db"


def db_olustur():
    con = sqlite3.connect(DB_DOSYA)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash BLOB NOT NULL
        )
    """)
    con.commit()
    con.close()


def sifre_hashle(sifre):
    return bcrypt.hashpw(sifre.encode('utf-8'), bcrypt.gensalt())


def sifre_dogrula(sifre, hashli_sifre):
    return bcrypt.checkpw(sifre.encode('utf-8'), hashli_sifre)


def kullanici_ekle(username, password):
    con = sqlite3.connect(DB_DOSYA)
    cur = con.cursor()
    try:
       
        cur.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            return False  
        hashed_pw = sifre_hashle(password)
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_pw))
        con.commit()
        return True
    except Exception as e:
        return False
    finally:
        con.close()


def kullanici_var_mi(username, password):
    con = sqlite3.connect(DB_DOSYA)
    cur = con.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    con.close()
    if row:
        return sifre_dogrula(password, row[0])
    return False


def kullanici_sil(username, password):
    if not kullanici_var_mi(username, password):
        return False
    con = sqlite3.connect(DB_DOSYA)
    cur = con.cursor()
    cur.execute("DELETE FROM users WHERE username = ?", (username,))
    con.commit()
    etkilenen = cur.rowcount
    con.close()
    return etkilenen > 0


def kullanici_klasoru_olustur(kullanici_adi):
    yol = os.path.join("notlar", kullanici_adi)
    os.makedirs(yol, exist_ok=True)
    return yol


def veritabani_baglan_ve_olustur(klasor_yolu):
    db_yolu = os.path.join(klasor_yolu, "notlar.db")
    conn = sqlite3.connect(db_yolu)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            baslik TEXT,
            icerik TEXT,
            tarih TEXT,
            dosya_yolu TEXT,
            not_turu TEXT
        )
    """)
    conn.commit()
    return conn, cursor


if __name__ == "__main__":
    db_olustur()
