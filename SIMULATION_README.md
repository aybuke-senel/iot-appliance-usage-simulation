# IoT-Based Appliance Usage Tracker - Simulation Documentation

## Genel Bakış

Bu simülasyon, **IoT-Based Appliance Usage Tracker** sisteminin tam bir simülasyonunu gerçekleştirir. Sistem üç katmanlı bir mimariyi taklit eder:

1. **Cihaz Katmanı (Device Layer)**: CSV dosyalarından veri okuma (akıllı prizlerin sensör verilerini simüle eder)
2. **İletişim Katmanı (Communication Layer)**: MQTT mesaj yayınlama simülasyonu
3. **Uygulama Katmanı (Application Layer)**: Bulut tabanlı mesaj işleme ve canlı dashboard gösterimi

## Simülasyon Dosyası

- **`simulation_main.py`**

## Kullanım

### Gereksinimler
```bash
pip install pandas numpy
```

### Simülasyonu Çalıştırma
```bash
python3 simulation_main.py
```

## Simülasyon Parametreleri

`simulation_main.py` dosyasında aşağıdaki parametreleri ayarlanmalıdır:

```python
SAMPLE_SIZE = None      # None = Tüm kayıtlar, veya sayı belirtin (örn: 1000)
PUBLISH_RATE = 10000.0  # Saniyede mesaj sayısı (10000 = hızlı simülasyon)
```

## Simülasyon Bileşenleri

### 1. MQTT Publish Simülasyonu
```python
def fake_mqtt_publish(topic, payload, stats, verbose=True):
    """
    Gerçek bir MQTT broker'a mesaj gönderme işlemini simüle eder.
    Gerçek sistemde bu, MQTT broker'a bağlanıp mesaj yayınlar.
    """
```

**Simüle Edilen Davranış:**
- MQTT topic formatı: `home/appliance/{device_id}/power`
- JSON payload formatı: `{"device_id": "...", "timestamp": "...", "power": ...}`
- Mesaj yayınlama hızı: `PUBLISH_RATE` parametresi ile kontrol edilir

### 2. Bulut İşlemci Simülasyonu
```python
class CloudProcessor:
    """
    Bulut tabanlı mesaj işlemciyi simüle eder.
    Gerçek sistemde bu, MQTT broker'dan mesajları subscribe eder ve işler.
    """
```

**Simüle Edilen Davranış:**
- MQTT mesajlarını alma (subscribe)
- Mesajları parse etme ve doğrulama
- İstatistik hesaplama
- Veri depolama hazırlığı

### 3. Canlı Dashboard Simülasyonu
```python
def print_dashboard(stats, processor):
    """
    Canlı dashboard gösterimi.
    Gerçek sistemde bu, web tabanlı bir dashboard olur.
    """
```

**Gösterilen Bilgiler:**
- Cihaz bilgileri (ID, isim)
- Gerçek zamanlı güç tüketimi
- İstatistikler (ortalama, maksimum, minimum güç)
- İşlenen mesaj sayısı
- Güç görselleştirme çubuğu

### 4. İstatistik Takibi
```python
class LiveStats:
    """
    Simülasyon sırasında canlı istatistikleri takip eder.
    """
```

**Takip Edilen Metrikler:**
- Toplam mesaj sayısı
- Toplam güç tüketimi
- Maksimum/minimum güç
- Anlık güç değeri
- Son güç değerleri (son 20 kayıt)

## Simülasyon Akışı

```
1. CSV Dosyası Okuma
   ↓
2. Her Satır için Döngü:
   ├─ MQTT Payload Oluşturma
   ├─ MQTT Publish Simülasyonu
   ├─ Bulut İşlemci Simülasyonu
   ├─ İstatistik Güncelleme
   └─ Dashboard Güncelleme (periyodik)
   ↓
3. Final Dashboard Gösterimi
   ↓
4. Özet Rapor
```

## Projemizdeki Kullanımı

### Paper'da Bahsettiğimiz Kodlar

1. **Ana Simülasyon Dosyası**: `simulation_main.py`
   - Tüm simülasyon mantığını içerir
   - İyi dokümante edilmiş
   - Proje için uygun format

2. **Simülasyon Bileşenleri**:
   - `fake_mqtt_publish()`: MQTT yayınlama simülasyonu
   - `CloudProcessor`: Bulut işlemci simülasyonu
   - `LiveStats`: İstatistik takibi
   - `print_dashboard()`: Dashboard gösterimi

### Sunumumuz İçin Kullanım

Simülasyonu kaydetmek için terminal ekranını kaydettim:
```bash
# macOS kullandığım için
script -a simulation_output.txt python3 simulation_main.py

```

## Simülasyon Çıktıları

### Terminal Çıktısı
- Canlı dashboard güncellemeleri
- İlerleme çubuğu
- Gerçek zamanlı istatistikler
- MQTT mesaj logları (isteğe bağlı)

### Log Dosyası 
- `iot_simulation.log`: Detaylı simülasyon logları

## Teknik Detaylar

### Veri Formatı
- **Giriş**: CSV dosyaları (`fridge_207.csv`, `vacuum_254.csv`)
- **Format**: `timestamp`, `power` kolonları
- **Timestamp**: ISO format datetime

### MQTT Mesaj Formatı
```json
{
  "device_id": "fridge_207",
  "timestamp": "2024-01-01T00:00:00",
  "power": 45.5
}
```

### Performans Optimizasyonları
- Büyük veri setleri için dashboard güncellemeleri periyodik yapılır
- Mesaj logları her mesaj için değil, örnekleme ile gösterilir
- İlerleme çubuğu her 100 kayıtta bir güncellenir

## Referanslar

Bu simülasyon aşağıdaki gerçek sistem bileşenlerini taklit eder:

1. **ESP32 Akıllı Prizler**: CSV dosyalarından okunan veriler
2. **MQTT Broker**: `fake_mqtt_publish()` fonksiyonu
3. **Bulut Sunucu**: `CloudProcessor` sınıfı
4. **Web Dashboard**: `print_dashboard()` fonksiyonu

## Notlar

- Bu simülasyon gerçek bir MQTT broker kullanmaz
- Tüm iletişim Python içinde simüle edilir
- Simülasyon amacıyla tasarlanmıştır, gerçek IoT sistemine dönüştürülebilir
- Büyük veri setleri için simülasyon süresi uzun olabilir (2.5M kayıt için ~4-5 dakika)

## Akademik Kullanım

Bu simülasyon kodu, projemizin **"Proposed Methodology"** bölümünde şu şekilde açıklanmaktadır:

> "Simülasyonumuz üç katmanlı mimariyi taklit eder: (1) Cihaz katmanında CSV dosyalarından sensör verileri okunur, (2) İletişim katmanında MQTT protokolü ile mesaj yayınlama simüle edilir, (3) Uygulama katmanında bulut tabanlı mesaj işleme ve canlı dashboard gösterimi gerçekleştirilir."

Simülasyon kodları `simulation_main.py` dosyasında bulunmaktadır ve projenin teknik detaylarını kanıtlamak için kullanılabilir.

