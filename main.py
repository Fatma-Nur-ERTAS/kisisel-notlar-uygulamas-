import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser, font
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import wave
import numpy as np
import sounddevice as sd
import threading
import os
import datetime
import shutil
import veritabani

kayit = False
kayit_verisi = []
kayit_samp_rate = 44100
aktif_medya_yolu = None
aktif_medya_turu = None
aktif_kullanici = None
resim_etiketleri = []
ses_thread = None
son_kaydedilen_not = None

def yazı_ayarlarini_ac(metin_kutusu):
    pencere = tk.Toplevel()
    pencere.title("Yazı Ayarları")
    pencere.geometry("300x400")

    font_adlari = list(font.families())
    secilen_font = tk.StringVar(value="Arial")
    secilen_boyut = tk.IntVar(value=12)
    kalin = tk.BooleanVar()
    italik = tk.BooleanVar()
    altcizgi = tk.BooleanVar()
    secilen_renk = tk.StringVar(value="#000000")

    tk.Label(pencere, text="Yazı Tipi:").pack(pady=5)
    tk.OptionMenu(pencere, secilen_font, *font_adlari).pack()

    tk.Label(pencere, text="Yazı Boyutu:").pack(pady=5)
    tk.Spinbox(pencere, from_=8, to=72, textvariable=secilen_boyut).pack()

    tk.Label(pencere, text="Yazı Stili:").pack(pady=5)
    tk.Checkbutton(pencere, text="Kalın", variable=kalin).pack()
    tk.Checkbutton(pencere, text="İtalik", variable=italik).pack()
    tk.Checkbutton(pencere, text="Altı Çizili", variable=altcizgi).pack()

    def renk_sec():
        renk = colorchooser.askcolor()[1]
        if renk:
            secilen_renk.set(renk)

    tk.Button(pencere, text="Yazı Rengini Seç", command=renk_sec).pack(pady=10)

    def uygula():
        stil = ""
        if kalin.get():
            stil += "bold"
        if italik.get():
            stil += " italic"
        if altcizgi.get():
            stil += " underline"
        font_ayari = (secilen_font.get(), secilen_boyut.get(), stil.strip())
        metin_kutusu.config(font=font_ayari, fg=secilen_renk.get())

    tk.Button(pencere, text="Ayarları Uygula", command=uygula, bg="#acf").pack(pady=10)

def ses_kayit_callback(indata, frames, time, status):
    global kayit_verisi, kayit
    if kayit:
        kayit_verisi.append(indata.copy())

def ses_kayit_thread():
    global kayit
    with sd.InputStream(channels=1, samplerate=kayit_samp_rate, callback=ses_kayit_callback):
        while kayit:
            sd.sleep(100)

def ses_kayit_penceresi(metin_kutusu):
    global kayit, kayit_verisi, ses_thread, aktif_medya_yolu, aktif_medya_turu
    pencere = tk.Toplevel()
    pencere.title("Ses Kaydı ve Seçimi")
    pencere.geometry("360x300")
    emblem_label = tk.Label(pencere, text="")
    emblem_label.pack(pady=5)

    def baslat():
        nonlocal emblem_label
        kayit_verisi.clear()
        global kayit
        kayit = True
        ses_thread = threading.Thread(target=ses_kayit_thread, daemon=True)
        ses_thread.start()
        emblem_label.config(text="🔴 Ses Kaydediliyor...")

    def durdur():
        global kayit
        kayit = False
        emblem_label.config(text="⏹️ Kayıt Durduruldu")

    def kaydet():
        global aktif_medya_yolu, aktif_medya_turu
        klasor = veritabani.kullanici_klasoru_olustur(aktif_kullanici)
        dosya_adi = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        yol = os.path.join(klasor, dosya_adi)
        try:
            data = np.concatenate(kayit_verisi)
            with wave.open(yol, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(kayit_samp_rate)
                wf.writeframes((data * 32767).astype(np.int16).tobytes())
            aktif_medya_yolu = yol
            aktif_medya_turu = "ses"
            metin_kutusu.insert(tk.END, f"\n[Ses: {os.path.basename(yol)}]")
        except Exception as e:
            messagebox.showerror("Hata", f"Ses kaydı kaydedilemedi: {e}")
        pencere.destroy()

    def cihazdan_sec():
        global aktif_medya_yolu, aktif_medya_turu
        yol = filedialog.askopenfilename(filetypes=[("Ses Dosyaları", "*.wav;*.mp3")])
        if yol:
            aktif_medya_yolu = yol
            aktif_medya_turu = "ses"
            metin_kutusu.insert(tk.END, f"\n[Ses: {os.path.basename(yol)}]")
            pencere.destroy()

    tk.Button(pencere, text="Kaydı Başlat", command=baslat).pack(pady=4)
    tk.Button(pencere, text="Kaydı Durdur", command=durdur).pack(pady=4)
    tk.Button(pencere, text="Kaydı Kaydet", command=kaydet).pack(pady=4)
    tk.Button(pencere, text="Cihazdan Ses Seç", command=cihazdan_sec).pack(pady=4)

def resim_ekle(canvas):
    global aktif_medya_yolu, aktif_medya_turu
    yol = filedialog.askopenfilename(filetypes=[("Resim Dosyaları", "*.png;*.jpg;*.jpeg")])
    if yol:
        img = Image.open(yol)
        img.thumbnail((300, 300))
        img_tk = ImageTk.PhotoImage(img)
        etiket = tk.Label(canvas, image=img_tk, bd=2, relief="groove")
        etiket.image = img_tk
        etiket.place(x=50, y=50)

        def surukle(event):
            etiket.place(x=event.x_root - canvas.winfo_rootx() - 50, y=event.y_root - canvas.winfo_rooty() - 50)

        etiket.bind("<B1-Motion>", surukle)
        aktif_medya_yolu = yol
        aktif_medya_turu = "resim"

def video_ekle(metin_kutusu):
    global aktif_medya_yolu, aktif_medya_turu
    yol = filedialog.askopenfilename(filetypes=[("Video Dosyaları", "*.mp4")])
    if yol:
        aktif_medya_yolu = yol
        aktif_medya_turu = "video"
        metin_kutusu.insert(tk.END, f"\n[Video: {os.path.basename(yol)}]")

def not_ekle(kullanici, icerik, medya_yolu, medya_turu):
    klasor = veritabani.kullanici_klasoru_olustur(kullanici)
    dosya_adi = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Dosyaları", "*.html")], title="Notu Kaydet")

    if dosya_adi:
        global son_kaydedilen_not
        try:
            with open(dosya_adi, "w", encoding="utf-8") as f:
                f.write(f"<html><body>")
                f.write(f"<h3>Kullanıcı: {kullanici}</h3>")
                f.write(f"<p><strong>Tarih:</strong> {datetime.datetime.now()}</p>")
                f.write(f"<p>{icerik.strip().replace('\n', '<br>')}</p>")

                if medya_yolu and medya_turu == "video":
                    f.write(f"<video controls width='320' height='240'><source src='{medya_yolu}' type='video/mp4'></video><br>")

                elif medya_yolu and medya_turu == "ses":
                    try:
                        hedef_yol = os.path.join(os.path.dirname(dosya_adi), os.path.basename(medya_yolu))
                        shutil.copy(medya_yolu, hedef_yol)
                        f.write(f"<audio controls><source src='{os.path.basename(medya_yolu)}' type='audio/wav'></audio><br>")
                    except Exception as e:
                        messagebox.showerror("Hata", f"Ses dosyası kopyalanamadı: {e}")

                elif medya_yolu and medya_turu == "resim":
                    try:
                        hedef_yol = os.path.join(os.path.dirname(dosya_adi), os.path.basename(medya_yolu))
                        shutil.copy(medya_yolu, hedef_yol)
                        f.write(f"<img src='{os.path.basename(medya_yolu)}' width='300'><br>")
                    except Exception as e:
                        messagebox.showerror("Hata", f"Resim dosyası kopyalanamadı: {e}")

                f.write("</body></html>")

            son_kaydedilen_not = dosya_adi
            messagebox.showinfo("Başarılı", f"Not HTML olarak kaydedildi:\n{dosya_adi}")

        except Exception as e:
            messagebox.showerror("Hata", f"Not kaydedilemedi: {e}")
    else:
        messagebox.showwarning("Uyarı", "Dosya adı seçilmedi.")

def kaydet(metin_kutusu):
    global aktif_medya_yolu, aktif_medya_turu, aktif_kullanici
    yazi = metin_kutusu.get("1.0", tk.END)
    not_ekle(aktif_kullanici, yazi, aktif_medya_yolu, aktif_medya_turu)
    aktif_medya_yolu = None
    aktif_medya_turu = None

def notlari_goster():
    global son_kaydedilen_not
    if son_kaydedilen_not:
        os.startfile(son_kaydedilen_not)
    else:
        messagebox.showinfo("Bilgi", "Henüz kaydedilmiş bir not bulunamadı.")

def main_uygulama(kullanici):
    global aktif_kullanici
    aktif_kullanici = kullanici
    veritabani.kullanici_klasoru_olustur(kullanici)
    pencere = tk.Tk()
    pencere.title(f"Kişisel Notlar - {kullanici}")
    x = (pencere.winfo_screenwidth() - 1000) // 2
    y = (pencere.winfo_screenheight() - 700) // 2
    pencere.geometry(f"1000x700+{x}+{y}")

    ust_cerceve = tk.Frame(pencere)
    ust_cerceve.pack(side="top", fill="x")

    tk.Button(ust_cerceve, text="Yazı Ayarları", command=lambda: yazı_ayarlarini_ac(metin_kutusu)).pack(side="left", padx=5)
    tk.Button(ust_cerceve, text="Resim Ekle", command=lambda: resim_ekle(canvas)).pack(side="left", padx=5)
    tk.Button(ust_cerceve, text="Video Ekle", command=lambda: video_ekle(metin_kutusu)).pack(side="left", padx=5)
    tk.Button(ust_cerceve, text="Sesli Not Ekle", command=lambda: ses_kayit_penceresi(metin_kutusu)).pack(side="left", padx=5)

    canvas = tk.Canvas(pencere, bg="white")
    canvas.pack(fill="both", expand=True, padx=10, pady=5)

    metin_kutusu = ScrolledText(canvas, font=("Arial", 12), wrap="word")
    metin_kutusu.place(x=10, y=10, width=600, height=400)

    alt_cerceve = tk.Frame(pencere)
    alt_cerceve.pack(side="bottom", fill="x")

    tk.Button(alt_cerceve, text="Notu Kaydet", bg="#f96", command=lambda: kaydet(metin_kutusu)).pack(side="right", padx=5, pady=5)
    tk.Button(alt_cerceve, text="Notları Göster", bg="#f96", command=notlari_goster).pack(side="right", padx=5, pady=5)

    pencere.mainloop()

if __name__ == "__main__":
    main_uygulama("fatmanur")