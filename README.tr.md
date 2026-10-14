<div align="center">

# ⚡ DailyBrief

**Terminalinizdeki kişisel yapay zeka asistanınız.**  
Dağınık günlük notlarınızı, sprint maddelerinizi ve yapılacakları tek bakışta net bir brifinge dönüştürün.

[English Documentation (İngilizce README)](README.md) • [Hata Bildir](https://github.com/DrWellsy/dailybrief/issues) • [Özellik İste](https://github.com/DrWellsy/dailybrief/issues)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Sponsor](https://img.shields.io/badge/sponsor-%E2%9D%A4-red)](https://github.com/sponsors/DrWellsy)

<br/>

![DailyBrief Demo](demo.gif)

</div>

---

## 💡 Neden DailyBrief?

Geliştiriciler ve üreticiler olarak notlarımızı her yere dağıtırız: hızlı karalamalar, sprint öncelikleri, Jira notları, Obsidian sayfaları ve gün sonu hatırlatıcıları. Sabah masanın başına geçtiğinizde 10 farklı dosyayı tek tek okumak ciddi bir zihinsel yük yaratır.

**DailyBrief**, yerel not klasörünüzdeki Markdown (`.md`) ve düz metin (`.txt`) dosyalarını tarar, Anthropic Claude API ile analiz eder ve saniyeler içinde şık bir terminal brifingi sunar:

- **Bugün Öncelikli 3–5 Madde** (İlk olarak odaklanmanız gereken aksiyonlar)
- **Unutulmaması Gerekenler** (Toplantılar, teslim tarihleri, takip maddeleri)

Notlarınız Türkçe ve İngilizce karışık olsa bile, DailyBrief içeriği pürüzsüzce anlar ve seçtiğiniz dilde (`--lang tr` veya `--lang en`) tek bir düzenli çıktıda özetler.

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum

Projeyi klonlayın ve bağımlılıkları yükleyin:

```bash
git clone https://github.com/Aloostor/dailybrief.git
cd dailybrief
pip install -r requirements.txt
```

*(Opsiyonel) CLI komutu olarak sisteme bağlamak için:*

```bash
pip install -e .
```

### 2. API Anahtarı Ayarı

DailyBrief, Anthropic API anahtarına (`ANTHROPIC_API_KEY`) ihtiyaç duyar.

**Linux / macOS:**
```bash
export ANTHROPIC_API_KEY="api_anahtariniz"
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="api_anahtariniz"
```

**Windows (Komut İstemi - CMD):**
```cmd
set ANTHROPIC_API_KEY=api_anahtariniz
```

> **İlk Çalıştırma:** Eğer ortam değişkeni tanımlı değilse, DailyBrief terminal üzerinden anahtarınızı güvenle ister ve `~/.dailybrief/config.toml` dosyasına kaydeder.

---

## 💻 Kullanım

Varsayılan `./notes` klasörüyle çalıştırmak için:

```bash
python -m dailybrief
```

Veya sistem genelinde kuruluysa:

```bash
dailybrief
```

### Parametreler ve Seçenekler

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `-s, --source <YOL>` | Notların okunacağı klasör yolu | `./notes` |
| `-l, --lang <en\|tr>` | Arayüz ve özet dili (`tr` veya `en`) | `en` |
| `-h, --help` | Yardım mesajını ve parametreleri gösterir | |

#### Örnekler

**Farklı bir not klasöründen Türkçe brifing almak:**
```bash
dailybrief -s ~/Documents/ObsidianVault/Daily -l tr
```

**Modül olarak çalıştırma:**
```bash
python -m dailybrief --source ./notlarim --lang tr
```

---

## 🛠️ Proje Mimarisi

```text
dailybrief/
├── dailybrief/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py          # Click CLI & Rich terminal panelleri
│   ├── i18n.py         # Çoklu dil mesajları ve sistem komutları (en/tr)
│   ├── reader.py       # Not okuyucu (UTF-8, Windows-1254 desteği)
│   └── summarizer.py   # Anthropic Claude API entegrasyonu
├── notes/              # Örnek not dosyaları
├── scripts/
│   └── generate_demo.py # Modern demo.gif üretici script
├── tests/              # Test paketi (pytest)
├── pyproject.toml
└── demo.gif
```

---

## 🧪 Testler

Testleri çalıştırmak için:

```bash
pytest
```

---

## 🎨 Demo GIF'ini Yeniden Üretmek

Projedeki demo animasyonu, Rich arayüzünü birebir simüle eden bağımsız bir PIL scripti ile oluşturulmuştur:

```bash
python scripts/generate_demo.py
```

---

## 🤝 Katkıda Bulunma

Her türlü katkı, geri bildirim ve öneriye açığız!
Hata bildirmek veya yeni bir özellik önermek için GitHub üzerinden issue açabilir veya PR gönderebilirsiniz.

---

## 📄 Lisans

Bu proje MIT Lisansı altında sunulmaktadır. Ayrıntılar için [LICENSE](LICENSE) dosyasına göz atabilirsiniz.
