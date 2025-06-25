# login.py - Giriş ekranı bcrypt destekli

import tkinter as tk
from tkinter import messagebox
import veritabani
import main

# Veritabanı oluşturuluyor (zaten varsa dokunmaz)
veritabani.db_olustur()

def giris_ekrani():
    pencere = tk.Tk()
    pencere.title("Giriş Ekranı")
    pencere.configure(bg="#2E4053")

    genislik = 500
    yukseklik = 300
    ekran_genislik = pencere.winfo_screenwidth()
    ekran_yukseklik = pencere.winfo_screenheight()
    x = (ekran_genislik // 2) - (genislik // 2)
    y = (ekran_yukseklik // 2) - (yukseklik // 2)
    pencere.geometry(f"{genislik}x{yukseklik}+{x}+{y}")

    label_font = ("Arial", 14, "bold")
    entry_font = ("Arial", 13)
    button_font = ("Arial", 12, "bold")

    tk.Label(pencere, text="Kullanıcı Adı:", bg="#2E4053", fg="white", font=label_font).pack(pady=(40, 5))
    kullanici_adi_girdi = tk.Entry(pencere, font=entry_font)
    kullanici_adi_girdi.pack(ipady=6, padx=50)

    tk.Label(pencere, text="Şifre:", bg="#2E4053", fg="white", font=label_font).pack(pady=(15, 5))
    sifre_girdi = tk.Entry(pencere, show="*", font=entry_font)
    sifre_girdi.pack(ipady=6, padx=50)

    def giris_yap():
        kullanici = kullanici_adi_girdi.get().strip()
        sifre = sifre_girdi.get().strip()
        if veritabani.kullanici_var_mi(kullanici, sifre):
            messagebox.showinfo("Başarılı", f"Hoş Geldin, {kullanici}!")
            pencere.destroy()
            main.main_uygulama(kullanici)
        else:
            messagebox.showerror("Hata", "Kullanıcı adı veya şifre yanlış!")

    def hesap_olustur():
        kullanici = kullanici_adi_girdi.get().strip()
        sifre = sifre_girdi.get().strip()
        if not kullanici or not sifre:
            messagebox.showwarning("Uyarı", "Kullanıcı adı ve şifre boş olamaz!")
            return
        if veritabani.kullanici_ekle(kullanici, sifre):
            messagebox.showinfo("Başarılı", "Hesap oluşturuldu!")
        else:
            messagebox.showerror("Hata", "Bu kullanıcı adı zaten var!")

    def hesap_sil():
        kullanici = kullanici_adi_girdi.get().strip()
        sifre = sifre_girdi.get().strip()
        if messagebox.askyesno("Onay", "Bu hesabı silmek istediğinize emin misiniz?"):
            if veritabani.kullanici_sil(kullanici, sifre):
                messagebox.showinfo("Başarılı", "Hesap silindi!")
            else:
                messagebox.showerror("Hata", "Kullanıcı adı veya şifre yanlış!")

    buton_cerceve = tk.Frame(pencere, bg="#2E4053")
    buton_cerceve.pack(pady=30)

    tk.Button(buton_cerceve, text="Giriş Yap", width=12, font=button_font, bg="#27AE60", fg="white", command=giris_yap).pack(side=tk.LEFT, padx=10)
    tk.Button(buton_cerceve, text="Yeni Hesap", width=12, font=button_font, bg="#2980B9", fg="white", command=hesap_olustur).pack(side=tk.LEFT, padx=10)
    tk.Button(buton_cerceve, text="Hesap Sil", width=12, font=button_font, bg="#C0392B", fg="white", command=hesap_sil).pack(side=tk.LEFT, padx=10)

    pencere.mainloop()

if __name__ == "__main__":
    giris_ekrani()
