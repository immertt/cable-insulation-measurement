# Kablo İzolasyon Kalınlığı Ölçüm Sistemi

## Proje Hakkında

Bu proje, TÜBİTAK 2247-C STAR Programı kapsamında verilen görev doğrultusunda geliştirilmiştir.

Amaç, kablo kesit görüntülerini görüntü işleme yöntemleri ile analiz ederek kablonun geometrik özelliklerini otomatik olarak ölçmek ve kalite kontrol süreçlerinde kullanılabilecek bir ölçüm sistemi oluşturmaktır.

Sistem aşağıdaki kablo tiplerini desteklemektedir:

* Som telli (tek damarlı)
* Çok telli (tek damarlı, çok iletkenli)
* Üç damarlı (çok damarlı)

---

## Özellikler

### Görüntü İşleme

* Görüntü okuma (Unicode dosya yolu desteği dahil)
* Gri seviyeye dönüştürme
* Gaussian Blur ile gürültü azaltma
* Otsu eşikleme (Thresholding)
* Kontur tespiti ve hiyerarşi analizi
* Çok telli kablolar için HSV renk tabanlı ön işleme

### Ölçümler

* Dış çap ve iç çap
* İzolasyon kalınlığı (genel)
* Radyal kalınlık ölçümü (6 / 8 / 10 / 12 açı — ayarlanabilir)
* Minimum, maksimum ve ortalama kalınlık
* Eksen kaçıklığı
* Üç damarlı kablolarda t1, t2, t3 — her damar için ayrı minimum kalınlık
* Tüm sonuçlar piksel (px) ve milimetre (mm) olarak

### Görselleştirme

* Dış kontur (turuncu) ve iç kontur (mavi) çizimi
* Dış ve iç merkez noktaları işaretleme
* Eksen kaçıklığı çizgisi
* Açısal ölçüm çizgileri (min → kırmızı, max → yeşil)
* Sol üst köşede yarı saydam bilgi paneli
* Kesit ID damgası

### Raporlama

* JSON çıktısı (`outputs/results.json`)
* Açıklamalı sonuç görseli (`outputs/web_result.png`)
* Piksel → milimetre dönüşümü (kullanıcı tanımlı katsayı)

### Web Arayüzü

* Kablo tipi seçimi (Som Telli / Çok Telli / Üç Damarlı)
* Kesit görüntüsü yükleme ve sürükle-bırak
* Kamera yakalama simülasyonu
* Kesit ID, tarih, pixel-mm katsayısı ve ölçüm sayısı girişi
* Sonuçların metrik kartlar ve tablo ile gösterimi
* Açısal kalınlık bar grafiği
* JSON rapor indirme

---

## Proje Yapısı

```text
StarProje/
│
├── backend/
│   ├── app.py                # Flask web sunucusu
│   ├── main.py               # Ana işlem akışı
│   ├── image_processing.py   # Görüntü ön işleme ve kontur tespiti
│   ├── measurements.py       # Geometrik ölçüm hesaplamaları
│   ├── visualization.py      # Sonuç görseli oluşturma
│   ├── uploads/              # Yüklenen görüntüler (geçici)
│   ├── templates/
│   │   └── index.html        # Web arayüzü
│   └── static/
│
├── data/                     # Örnek kablo kesit görüntüleri
│   ├── som_telli_1.jpg
│   ├── som_telli_2.png
│   ├── cok_telli_1.jpg
│   ├── cok_telli_2.jpeg
│   ├── uc_damarli_1.jpg
│   └── uc_damarli_2.jpeg
│
├── outputs/                  # Üretilen çıktılar
│   ├── web_result.png
│   ├── threshold.png
│   └── results.json
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Kurulum

**1. Depoyu klonlayın:**

```bash
git clone <repo-url>
cd StarProje
```

**2. Sanal ortam oluşturun ve aktifleştirin:**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

**3. Bağımlılıkları yükleyin:**

```bash
pip install -r requirements.txt
```

---

## Uygulamayı Çalıştırma

### Flask ile (geliştirme)

```bash
python backend/app.py
```

Tarayıcıdan açın:

```
http://127.0.0.1:5000
```

### Docker ile

```bash
docker build -t kablo-olcum .
docker run -p 5000:5000 kablo-olcum
```

---

## Kullanım

1. **Kablo Tipi** seçin: Som Telli, Çok Telli veya Üç Damarlı
2. **Kesit görüntüsü** yükleyin (dosya seç veya sürükle-bırak) ya da **Kameradan Görüntü Al** butonunu kullanın
3. **Kesit bilgilerini** girin: Kesit ID, tarih, pixel-mm katsayısı, ölçüm sayısı
4. **Hesapla** butonuna tıklayın
5. Sonuçları arayüzde inceleyin veya **Rapor Oluştur** ile JSON olarak indirin

---

## Hesaplanan Parametreler

| Parametre | Birim | Açıklama |
|---|---|---|
| Dış Çap | px / mm | Kablonun toplam dış çapı |
| İç Çap | px / mm | İletken bölgenin çapı |
| İzolasyon Kalınlığı | px / mm | (Dış çap − İç çap) / 2 |
| Min Kalınlık | px / mm | Ölçüm noktaları arasındaki en ince yer |
| Max Kalınlık | px / mm | Ölçüm noktaları arasındaki en kalın yer |
| Ort. Kalınlık | px / mm | Tüm ölçümlerin ortalaması |
| Eksen Kaçıklığı | px / mm | Dış ve iç merkez arasındaki mesafe |
| t1, t2, t3 | px / mm | Üç damarlı kablolarda her damarın min. kalınlığı |

---

## Kullanılan Teknolojiler

| Katman | Teknoloji |
|---|---|
| Dil | Python 3.10 |
| Görüntü İşleme | OpenCV 4.x, NumPy |
| Web Sunucu | Flask |
| Arayüz | HTML, CSS, JavaScript |
| Konteyner | Docker |

---

## Geliştirici

**İbrahim Mert Akbaş**  
Erciyes Üniversitesi — Bilgisayar Mühendisliği  
TÜBİTAK 2247-C STAR Programı