<div align="center">

# ⚡ DailyBrief

**Terminalinizdeki kişisel yapay zeka geliştirici asistanınız.**  
Dağınık günlük notlarınızı, Git durumunuzu ve dünden devreden görevlerinizi tek bakışta net bir yönetici brifingine dönüştürün.

[English Documentation (İngilizce README)](README.md) • [Hata Bildir](https://github.com/DrWellsy/dailybrief/issues) • [Özellik İste](https://github.com/DrWellsy/dailybrief/issues)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Sponsor](https://img.shields.io/badge/sponsor-%E2%9D%A4-red)](https://github.com/sponsors/DrWellsy)

<br/>

![DailyBrief Demo](demo.gif)

</div>

---

## 💡 Neden DailyBrief?

Geliştiriciler olarak sabah masanın başına geçtiğimizde en büyük vakit kaybı; dünden kalan notları, açık branch'leri, yarım kalan commit'leri ve ertelediğimiz maddeleri tek tek hatırlamaya çalışmaktır.

**DailyBrief**, terminalinizde çalışan tam teşekküllü bir kişisel ajandır:
- 📂 **Çoklu Kaynak:** `.md` ve `.txt` notlarınızı (Türkçe, İngilizce veya karışık) okur.
- 🐙 **Git Durum Algısı:** Bulunduğunuz Git dalını (branch), son 48 saatteki commit'leri ve henüz commit edilmemiş yarım kalan değişiklikleri otomatik tespit eder.
- 🧠 **Kalıcı Hafıza & Takip:** Dünün brifingini (`~/.dailybrief/history/`) hatırlayarak ertelenen veya devam eden işleri ön plana çıkarır.
- ⚡ **Etkileşimli Terminal Aksiyonları:** Brifing bittiğinde tek tuşla Slack/Teams için Standup metnini panoya kopyalar (`[c]`) veya Markdown olarak kaydeder (`[s]`).

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum

Projeyi klonlayın ve bağımlılıkları yükleyin:

```bash
git clone https://github.com/DrWellsy/dailybrief.git
cd dailybrief
pip install -r requirements.txt
```

*(Opsiyonel) Komut satırına bağlamak için:*

```bash
pip install -e .
```

### 2. API Anahtarı Ayarı

DailyBrief, Anthropic Claude API anahtarına (`ANTHROPIC_API_KEY`) ihtiyaç duyar.

**Linux / macOS:**
```bash
export ANTHROPIC_API_KEY="api_anahtariniz"
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="api_anahtariniz"
```

> **Kolay Kurulum:** İlk çalıştırmada API anahtarı tanımlı değilse, terminalden anahtarınızı güvenle ister ve `~/.dailybrief/config.toml` dosyasına kaydeder.

---

## 💻 Kullanım ve Seçenekler

```bash
dailybrief [SEÇENEKLER]
```

Veya modül olarak:

```bash
python -m dailybrief [SEÇENEKLER]
```

### Parametreler ve Seçenekler

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `-s, --source <YOL>` | Notların okunacağı klasör yolu | `./notes` |
| `-l, --lang <en\|tr>` | Arayüz ve brifing dili (`tr` veya `en`) | `en` |
| `-i, --interactive` | Brifing sonrası etkileşimli menüyü (kopyala, kaydet) açar | `false` |
| `--no-git` | Otomatik Git durumu ve commit taramasını kapatır | `false` |
| `--no-history` | Önceki günlerin brifing hafızasını kapatır | `false` |
| `-h, --help` | Yardım mesajını gösterir | |

#### Örnekler

**Sabah etkileşimli Türkçe brifing almak:**
```bash
dailybrief -l tr -i
```

**Özel bir Obsidian klasöründen brifing üretmek:**
```bash
dailybrief -s ~/Documents/ObsidianVault/Daily -l tr -i
```

---

## 🧠 Ajan Nasıl Çalışır?

```text
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│ Yerel Notlar   │     │ Git Deposu     │     │ Hafıza/Geçmiş  │
│ (.md ve .txt)  │     │ (branch/durum) │     │ (~/.dailybrief)│
└───────┬────────┘     └───────┬────────┘     └───────┬────────┘
        │                      │                      │
        └───────────────► 🤖 DailyBrief ◄─────────────┘
                               │
                      Anthropic Claude Sonnet
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │ ⚡ DailyBrief Terminal Yönetici Paneli        │
        │                                              │
        │ 📌 Bugün Öncelikli 3–5 Madde                 │
        │ ⚡ Unutulmaması Gerekenler & Takipler        │
        └──────────────────────┬───────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
     [c] Standup Kopyala                  [s] Markdown Kaydet
     (Sistem Panosu)                      (brief-YYYY-MM-DD.md)
```

---

## 🧪 Testler

Test paketini çalıştırmak için:

```bash
pytest
```

---

## 📄 Lisans

Bu proje MIT Lisansı altında sunulmaktadır. Ayrıntılar için [LICENSE](LICENSE) dosyasına bakabilirsiniz.
