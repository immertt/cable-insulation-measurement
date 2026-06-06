# Kablo İzolasyon Kalınlığı Ölçüm Sistemi

## Proje Hakkında

Bu proje, TÜBİTAK 2247-C STAR Programı kapsamında verilen görev doğrultusunda geliştirilmiştir.

Amaç, kablo kesit görüntülerini görüntü işleme yöntemleri ile analiz ederek kablonun geometrik özelliklerini otomatik olarak ölçmek ve kalite kontrol süreçlerinde kullanılabilecek bir ölçüm sistemi oluşturmaktır.

Sistem;

* Som telli kabloları
* Çok telli kabloları

analiz edebilmektedir.

Kullanıcı web arayüzü üzerinden bir kablo kesit görüntüsü yükleyerek ölçüm sonuçlarını elde edebilir.

---

# Özellikler

## Görüntü İşleme

* Görüntü okuma
* Gri seviyeye dönüştürme
* Gaussian Blur ile gürültü azaltma
* Eşikleme (Thresholding)
* Kontur (Contour) tespiti
* Kontur hiyerarşisi analizi
* Renk tabanlı ön işleme

## Ölçümler

* Dış çap ölçümü
* İç çap ölçümü
* İzolasyon kalınlığı ölçümü
* Eksen kaçıklığı (Eccentricity)
* 6 farklı açıdan radyal kalınlık ölçümü
* Minimum kalınlık
* Maksimum kalınlık
* Ortalama kalınlık

## Raporlama

* JSON çıktısı oluşturma
* Sonuç görüntüsü oluşturma
* Piksel → Milimetre dönüşümü

## Web Arayüzü

* Görsel yükleme
* Otomatik analiz
* Sonuçların tablo halinde gösterimi
* İşlenmiş görüntünün görüntülenmesi

---

# Proje Yapısı

```text
StarProje/
│
├── backend/
│   ├── app.py
│   ├── main.py
│   ├── image_processing.py
│   ├── measurements.py
│   ├── visualization.py
│   ├── uploads/
│   ├── templates/
│   └── static/
│
├── data/
│
├── outputs/
│
├── requirements.txt
│
└── README.md
```

---

# Kurulum

Sanal ortam oluşturma:

```bash
python -m venv venv
```

Sanal ortamı aktifleştirme:

```bash
venv\Scripts\activate
```

Gerekli kütüphaneleri yükleme:

```bash
pip install -r requirements.txt
```

---

# Uygulamayı Çalıştırma

Flask uygulamasını başlatın:

```bash
python backend/app.py
```

Daha sonra tarayıcıdan:

```text
http://127.0.0.1:5000
```

adresine giderek sistemi kullanabilirsiniz.

---

# Hesaplanan Parametreler

Sistem aşağıdaki ölçümleri gerçekleştirmektedir:

* Dış çap
* İç çap
* İzolasyon kalınlığı
* Minimum kalınlık
* Maksimum kalınlık
* Ortalama kalınlık
* Eksen kaçıklığı

Sonuçlar hem:

* Piksel (px)
* Milimetre (mm)

olarak raporlanmaktadır.

---

# Kullanılan Teknolojiler

* Python 3.10
* OpenCV
* NumPy
* Flask
* HTML
* CSS

---

# Gelecekte Yapılabilecek Geliştirmeler

* Üç damarlı kablo desteği
* Kamera kalibrasyonu
* Gerçek zamanlı video analizi
* Otomatik piksel-mm dönüşümü
* PDF rapor üretimi

---

# Geliştirici

İbrahim Mert Akbaş

Erciyes Üniversitesi
Bilgisayar Mühendisliği
