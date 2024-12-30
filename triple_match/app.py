from flask import Flask, render_template, jsonify
import random
import time

# Oyuncu sınıfı
class Oyuncu:
    def __init__(self, isim):
        self.isim = isim
        self.puan = 0
        self.carpan = 1  
        self.kayip_sayisi = 0  
        self.bekleme_suresi = None  # Bekleme süresi

    def puan_hesapla(self, kazandi_mi):
        # Puan hesaplama yeri 

        if kazandi_mi:
            self.puan += 5 + (self.carpan * 5)
            if self.carpan < 5:
                self.carpan += 1
        else:
            # Kaybedilirse 20 puan düşürülür.
            self.puan = max(0, self.puan - 20)  
            self.carpan = 1  # Kaybedildiği zaman çarpan 1'e düşer.
            self.kayip_sayisi += 1  # Kayıp sayısını arttırılır.

            if self.kayip_sayisi >= 4:
                self.bekleme_suresi = time.time() + 60  # Bekleme süresi 

# Oyun sınıfı
class Oyun:
    def __init__(self):
        self.sayi_izgarasi = []
        self.kazanma_durumu = False

    def sayilari_diz(self):
        # 3x3'lük ızgarayı rastgele oluştur 
        self.sayi_izgarasi = [[random.randint(1, 3) for _ in range(3)] for _ in range(3)]
        if random.random() < 0.5:
            same_number = random.randint(1, 3)
            self.sayi_izgarasi[0][1] = same_number  # Kazanma şansını arttırma kısmı
            self.sayi_izgarasi[1][1] = same_number
            self.sayi_izgarasi[2][1] = same_number

    def eslesmeleri_kontrol_et(self):
        # Her row 2. hücreyi kontrol eder.
        ikinci_hucreler = [row[1] for row in self.sayi_izgarasi]  

        # 2. hücreleri kontrol etme kısmı 
        if ikinci_hucreler[0] == ikinci_hucreler[1] == ikinci_hucreler[2]:
            self.kazanma_durumu = True
            return True
        return False

    def oyun_sonu(self):
        return "Kazandınız!" if self.kazanma_durumu else "Kaybettiniz!"

# Flask
app = Flask(__name__)

# Oyuncu 
oyuncu = Oyuncu(isim="Hakkı")

# Ana sayfa 
@app.route('/')
def ana_sayfa():
    return render_template('index.html')

# Oyun başlatma yeri
@app.route('/oyun-baslat')
def oyun_baslat():
    # Eğer bekleme süresi varsa, süre kontrol edilir. 
    if oyuncu.bekleme_suresi:
        if time.time() < oyuncu.bekleme_suresi:
            # Bekleme süresi devam ediyor, kalan süreyi hesapla
            remaining_time = int(oyuncu.bekleme_suresi - time.time())
            return jsonify({
                "sonuc": f"Lütfen {remaining_time} saniye bekleyin, tekrar oynayabilirsiniz.",
                "puan": oyuncu.puan,
                "carpan": oyuncu.carpan,
                "kazandiMi": None,
                "izgara": []
            })
        else:
            # Bekleme süresi tamamlandığında kayıp sayısını ve bekleme süresini sıfırlar.
            oyuncu.kayip_sayisi = 0
            oyuncu.bekleme_suresi = None

    # Yeni bir oyun başlat
    oyun = Oyun()
    oyun.sayilari_diz()  # Rastgele sayıları oluştur
    kazandi_mi = oyun.eslesmeleri_kontrol_et()  # Kazanma durumunu kontrol et

    # Puan hesaplama ve kayıp sayısı güncelleme
    oyuncu.puan_hesapla(kazandi_mi)

    if not kazandi_mi:  # Eğer oyuncu kaybettiyse
        if oyuncu.kayip_sayisi >= 4:
            # Bekleme süresini başlat
            oyuncu.bekleme_suresi = time.time() + 60  # 60 saniye bekleme süresi
            return jsonify({
                "sonuc": "3 kez kaybettiniz! Bekleme süresi başladı.",
                "puan": oyuncu.puan,
                "carpan": oyuncu.carpan,
                "kazandiMi": None,
                "izgara": []
            })

    return jsonify({
        "izgara": oyun.sayi_izgarasi,
        "sonuc": oyun.oyun_sonu(),
        "kazandiMi": kazandi_mi,
        "puan": oyuncu.puan,
        "carpan": oyuncu.carpan
    })

if __name__ == '__main__':
    app.run(debug=True)
