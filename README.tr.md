<div align="center">

# ⚡ DailyBrief

**Terminalinizdeki kişisel yapay zeka geliştirici asistanınız.**  
Dağınık günlük notlarınızı, çoklu Git aktivitelerinizi ve dünden devreden önceliklerinizi net bir yönetici brifingine ve kronik tıkanıklık uyarısına dönüştürün.

[English Documentation (İngilizce README)](README.md) • [Hata Bildir](https://github.com/DrWellsy/dailybrief/issues) • [Özellik İste](https://github.com/DrWellsy/dailybrief/issues)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Version](https://img.shields.io/badge/version-0.3.0-emerald)](https://github.com/DrWellsy/dailybrief)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Sponsor](https://img.shields.io/badge/sponsor-%E2%9D%A4-red)](https://github.com/sponsors/DrWellsy)

<br/>

![DailyBrief Demo](demo.gif)

</div>

---

## 💡 Neden DailyBrief?

Geliştiriciler olarak çalışmalarımız gün içinde dağılır: hızlı karalama notları, birden fazla Git deposu ve dünden devreden ertelenmiş maddeler. Sabah masanın başına geçtiğinizde kahvenizi yudumlamadan önce 10 farklı dosyayı ve dünkü commit'leri hatırlamaya çalışmak ciddi bir zihinsel yorgunluk yaratır.

**DailyBrief**, terminalinizde çalışan otonom bir geliştirici ajanıdır:
- 🛡️ **Yerel DLP ve Gizli Bilgi Güvenlik Duvarı:** Asla dışarıya API anahtarı veya şifre sızdırmaz! Notlardaki ve git diff'lerindeki API anahtarlarını (`sk-...`, `ghp_...`, `AIza...`), JWT token'larını, veritabanı bağlantı adreslerini ve özel SSH anahtarlarını LLM'e iletmeden önce otomatik sansürler.
- 🔍 **Kod İçi `TODO` / `FIXME` Hasadı:** Kod dosyalarındaki satır içi yorumları (`TODO:`, `FIXME:`, `HACK:`) son değiştirilen dosyalara öncelik vererek tarar ve günlük brifinge dahil eder (`--no-todos` ile kapatılabilir).
- 📊 **Akıllı Bağlam Bütçesi & Maliyet/Gecikme Telemetrisi:** Büyük lockfile farklarını kırparak bağlam taşmasını önler; brifingin altında kesin gecikme (`⏱️ 1.2s`), tahmini token ve dolar maliyetini (`💰 $0.0035`) gösterir.
- 📈 **Haftalık Sprint Retrospektifi (`--weekly`):** Son 7 günün Git commit'lerini ve brifing hafızasını analiz ederek Geliştirici Hız Skorunu (%) ve Cuma günleri yöneticinizle paylaşabileceğiniz haftalık standup özetini üretir (`[c]` ile kopyalama).
- 🚀 **Kabuk Otomatik Selamlama Kancası (`--init-shell`):** Sabah terminalinizi ilk açtığınızda günde sadece bir kez brifingi çalıştırır (sonraki sekmelerde 0ms gecikme).
- 📦 **Python Gerektirmeyen Bağımsız İkili Dosya:** Windows (`.exe`), macOS veya Linux üzerinde Python veya sanal ortam kurmaya gerek kalmadan tek tıkla çalıştırın.
- ⚡ **Saniyeden Hızlı Paralel Motor & Sıfır Token Akıllı Önbellek:** Çoklu not dosyalarını ve Git depolarını eşzamanlı iş parçacıklarıyla okur. Deterministik SHA-256 durum önbelleği sayesinde girdi değişmediğinde brifingi 50ms altında `⚡ Anlık önbellekten yüklendi (0 token kullanıldı)` rozetiyle sunar.
- ⏰ **Otonom Sabah Zamanlayıcısı (`--schedule 08:45`):** Bilgisayarınızı açtığınızda sabah brifinginizi hazır eder; yerel işletim sistemi görev zamanlayıcısını kullanarak önbelleği ısıtır ve yerel masaüstü bildirimi gönderir.
- 🩺 **Sistem Öz-Tanılaması (`--doctor`):** Yapılandırma dosyası, API anahtarları / yerel Ollama bağlantısı, Git durumu ve ses motorunu kontrol eden zengin tanılama tablosu sunar.
- 🔒 **Çoklu-LLM ve %100 Yerel / Gizlilik Odaklı Mod:** Anthropic Claude, OpenAI, Google Gemini seçin veya **yerel Ollama** (`llama3.2`, `mistral`) ile API anahtarı gerekmeden %100 çevrimdışı ve gizli çalıştırın.
- 🔌 **Yerel MCP (Model Context Protocol) Sunucusu:** `dailybrief --mcp` ile brifinginizi, Git durumunuzu ve hafızanızı doğrudan Cursor, Windsurf ve Claude Desktop gibi yapay zeka IDE'lerine bağlayın.
- 🌙 **Gün Sonu Otonom Mutabakatı (`--eod`):** Gününüzün döngüsünü kapatır. Sabah önceliklerinizi gün içindeki Git commit'leri ve not güncellemeleriyle kıyaslayıp Tamamlanan, Devam Eden ve Yarına Aktarılan olarak otomatik sınıflandırır.
- ⚡ **Öngörülü Git Çakışma & Upstream Radarı:** Çalışma dizininize dokunmadan upstream (`HEAD..@{u}` / `origin/main`) ayrışmasını kontrol eder; çakışma riski taşıyan dosyaları önceden uyarır.
- 🎙️ **Yönetici Sesli Brifingi (`--voice`):** Sabah kahvenizi içerken dinleyebileceğiniz 30–45 saniyelik akıcı ve konuşma dilinde sesli podcast özeti üretir ve terminalde oynatır.
- 🐙 **Çoklu Git Deposu Algısı:** Bir veya birden fazla depoyu (`-g /yol/depo`) izleyerek aktif dalı, son 48 saatteki commit'leri ve henüz commit edilmemiş değişiklikleri otomatik harmanlar.
- ⚠️ **Kronik Tıkanıklık & Erteleme Takip Motoru:** Son 3–5 günlük brifing geçmişiyle Git aktivitelerini çapraz sorgular. Bir görev 2 veya daha fazla gündür devrediyorsa ve ilgili commit yoksa, DailyBrief bunu özel bir uyarı paneliyle bildirir ve somut çözme tavsiyesi verir.
- ⚡ **Etkileşimli Ajan Menüsü (`-i`):**
  - **`[c]` Standup Kopyala:** Slack veya Teams için hazır madde imli standup özetini panoya kopyalar.
  - **`[s]` Markdown Kaydet:** Brifingi `brief-YYYY-MM-DD.md` dosyasına kaydeder.
  - **`[b]` Görevi Böl:** Öncelikli bir görev numarası seçtiğinizde yapay zeka bu görevi 3 adımlı teknik uygulama kontrol listesine bölerek `tasks-YYYY-MM-DD.md` dosyasına yazar.
  - **`[g]` Dal Aç (Checkout Branch):** 1. öncelikli göreve göre otomatik temiz bir Git dalı adı (ör. `fix/login-session-timeout`) önerir ve onayınızla `git checkout -b` çalıştırır.
  - **`[r]` Brifingi Düzelt / Sohbet:** Doğal dilde bir komut vererek (*"2. görevi çıkar, auth hatasını öne al"*) brifingi anında günceller ve hafızaya işler.

---

## 🖥️ Örnek Terminal Çıktısı

```text
╭─────────────────────────────────────────────────────────────────────────────╮
│                                 DailyBrief                                  │
│               Tarih: 2026-10-15  •  Sağlayıcı: anthropic (claude)           │
╰─────────────────────────────────────────────────────────────────────────────╯
[Git] 2 Git deposu izleniyor: dailybrief ('main'), api ('feat/auth') | 2 değişiklik
[Memory] Hafıza: Önceki brifingden (2026-10-14) görev devamlılığı sağlandı

╭─ ⚠️ Tıkanıklık / Devreden Görev Uyarısı ────────────────────────────────────╮
│ 1. Login session timeout hatasını öğleden önce çöz [2 gündür devrediyor]   │
│    💡 Bu görev son 2 gündür brifinglerde devrediyor ve ilgili Git            │
│       aktivitesi yok. Tavsiye: Görevi 15 dakikalık ilk alt adıma bölün      │
│       veya engelleyen sebebi netleştirmek için issue açın.                  │
╰─────────────────────────────────────────────────────────────────────────────╯

╭─ Günlük Brifing ────────────────────────────────────────────────────────────╮
│                                                                             │
│ Bugün Öncelikli 3-5 Madde                                                   │
│ 1. Login session timeout hatasını öğleden önce çöz (Dünden devreden)       │
│ 2. v0.2.0 sürüm notlarını tamamla ve GitHub'da paylaş                       │
│ 3. Onboarding metin değişiklikleri için tasarım ekibiyle görüş              │
│                                                                             │
│ Unutulmaması Gerekenler                                                     │
│ • Saat 10:30'da Standup toplantısı (5 dk hazırlık)                          │
│ • Saat 16:00'da analytics dönüşüm raporunu incele                           │
│ • dailybrief/cli.py dosyasındaki değişiklikleri pushlamadan önce test et   │
│                                                                             │
╰─────────────────────────────────────────────────────────────────────────────╯
3 dosyadan derlendi

[c] Standup Kopyala  •  [s] MD Kaydet  •  [b] Görevi Böl  •  [g] Dal Aç  •  [r] Düzelt  •  [Enter] Çık
>>
```

---

## 🚀 Kurulum

### 1. Python Gerektirmeyen Bağımsız İkili (.exe / Binary) Kurulumu (Önerilen)
Python veya sanal ortam kurmanıza gerek yoktur! Terminalinizde tek bir komut çalıştırmanız yeterlidir:

**macOS ve Linux (Bash / Zsh):**
```bash
curl -fsSL https://raw.githubusercontent.com/DrWellsy/dailybrief/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/DrWellsy/dailybrief/main/install.ps1 | iex
```

*Veya derlenmiş ikili dosyayı doğrudan [GitHub Releases](https://github.com/DrWellsy/dailybrief/releases) sayfasından indirin:*
- **Windows x64:** `dailybrief-windows-x64.exe`
- **macOS Apple Silicon:** `dailybrief-macos-arm64`
- **Linux x64:** `dailybrief-linux-x64`

---

### 2. Python Paket Yöneticileri (`uv` veya `pipx`)

**`uv`** ile:
```bash
uv tool install git+https://github.com/DrWellsy/dailybrief.git
```

**`pipx`** ile:
```bash
pipx install git+https://github.com/DrWellsy/dailybrief.git
```

### 3. Kaynak Koddan Kurulum

```bash
git clone https://github.com/DrWellsy/dailybrief.git
cd dailybrief
pip install -e .
```

---

## ⚙️ Yapılandırma ve Sağlayıcılar

DailyBrief ayarlarını `~/.dailybrief/config.toml` dosyasında tutar:

```toml
# ~/.dailybrief/config.toml
provider = "anthropic"            # "anthropic", "openai", "gemini", veya "ollama"
model = "claude-sonnet-4-6"       # İsteğe bağlı model adı
watched_repos = [
    "/Users/dev/projeler/dailybrief",
    "/Users/dev/projeler/api-backend"
]

# Yönetici Sesli Brifing Ayarları
voice_provider = "openai"         # "openai", "elevenlabs", veya yerel çevrimdışı sistem sesi
voice_name = "alloy"              # "alloy", "echo", "fable", "onyx", "nova", "shimmer"
```

### 1. %100 Yerel ve Gizli Mod (Ollama)
Herhangi bir API anahtarı gerekmez. [Ollama](https://ollama.ai) kurup çalıştırın:

```bash
# Modeli indirin
ollama run llama3.2

# DailyBrief'i tamamen yerel çalıştırın
dailybrief --provider ollama --model llama3.2
```

### 2. Bulut Sağlayıcılar (Anthropic, OpenAI, Gemini)
Ortam değişkenlerinizi ayarlayın veya DailyBrief ilk çalıştırmada anahtarınızı güvenle kaydetsin:

```bash
# Anthropic Claude (Varsayılan)
export ANTHROPIC_API_KEY="api_anahtariniz"

# OpenAI GPT-4o ve TTS
export OPENAI_API_KEY="api_anahtariniz"
dailybrief --provider openai --model gpt-4o

# Google Gemini
export GEMINI_API_KEY="api_anahtariniz"
dailybrief --provider gemini --model gemini-2.5-flash
```

---

## 🔌 MCP Sunucu Entegrasyonu (Cursor / Claude Desktop / Windsurf)

DailyBrief, standart **Model Context Protocol (MCP)** protokolünü `stdio` üzerinden JSON-RPC 2.0 ile destekler. Bu sayede yapay zeka kod editörleriniz sabah brifinginizi, Git durumunuzu ve görev hafızanızı doğrudan okuyabilir ve güncelleyebilir.

### Cursor (`~/.cursor/mcp.json`) ve Claude Desktop (`claude_desktop_config.json`) Kurulumu

Aşağıdaki JSON bloğunu MCP yapılandırmanıza ekleyin:

```json
{
  "mcpServers": {
    "dailybrief": {
      "command": "dailybrief",
      "args": ["--mcp"]
    }
  }
}
```

### Yapay Zeka Ajanlarına Sunulan 3 Temel Araç:
1. **`get_daily_briefing`**: Bugünkü yapılandırılmış öncelikleri, hatırlatmaları ve not özetini döndürür.
2. **`get_git_and_blocker_context`**: Aktif dal isimlerini, commit edilmemiş değişiklikleri ve günlerdir ertelenen kronik tıkanıklıkları iletir.
3. **`mark_task_completed`**: Belirli bir önceliği tamamlandı olarak işaretler ve hafızaya not düşerek yarın sabahki brifingin kusursuz olmasını sağlar.

---

## 🌙 Gün Sonu Otonom Mutabakat Modu (`--eod`)

Geliştirici gününüzü manuel takip zahmetine girmeden otonom kapatın:

```bash
dailybrief --eod
```

### Tam Günlük Döngü
1. **Sabah (`dailybrief -i`):** Günün en kritik 3-5 önceliğini belirler.
2. **Mesai:** Git depolarında kod yazar, commit atar ve notlarınızdaki `[x]` maddelerini tamamlarsınız.
3. **Akşam (`dailybrief --eod`):** Sabah brifingini gün içindeki Git commit'leri, değiştirilen dosyalar ve notlarla karşılaştırır.

Görevler otomatik olarak 3 gruba ayrılır:
- `✅ Bugün Tamamlananlar`: İlgili commit'lerle veya notlardaki `[x]` işaretleriyle eşleşenler.
- `🔄 Devam Edenler`: Kısmi commit atılmış veya henüz commit edilmemiş dosya değişiklikleri olanlar.
- `⏭️ Yarına Aktarılanlar`: Gün içinde dokunulmamış ve yarına devredecek görevler.

`[c]` tuşuna basarak Slack veya Teams kanalınıza göndermek üzere tek tuşla profesyonel gün sonu standup özetini panonuza kopyalayabilirsiniz!

---

## 🎙️ Yönetici Sesli Brifingi (`--voice`)

Terminaldeki sabah brifinginizi kahvenizi yudumlarken dinleyebileceğiniz 30–45 saniyelik bir podcast'e dönüştürün:

```bash
dailybrief --voice
```

- Markdown etiketlerini, linkleri ve tabloları doğal bir konuşma metnine dönüştürür.
- OpenAI TTS (`alloy`, `echo`, vb.) veya ElevenLabs ile stüdyo kalitesinde ses üretimi sağlar.
- **Sıfır Çökme / Çevrimdışı Güvencesi:** İnternet veya API anahtarı olmadığında sistemin kendi ses motorunu (Windows SAPI / COM, macOS `say`, Linux `espeak`) otomatik kullanarak her koşulda çalışır.
- Terminalde şık bir ses dalgası animasyonu gösterir; `Ctrl+C` ile çalma işlemi CLI çökmeden temiz bir şekilde atlanabilir.

---

## ⚡ Öngörülü Git Çakışma & Upstream Radarı

Daha kod yazmaya başlamadan dal çakışmalarını önleyin. DailyBrief, yerel çalışma dosyalarınıza dokunmadan arka planda güvenle upstream ayrışmasını (`HEAD..@{u}` / `origin/main`) inceler:

```text
╭─ ⚡ Git Radarı / Çakışma Riski ─────────────────────────────────────────────╮
│ ⚠️  origin/main üzerinde 2 yeni upstream commit var                         │
│ Upstream değişen: api/auth.py, tests/test_auth.py                          │
│ 🚨 Yüksek Çakışma Riski: Notlarınızda geçen veya yerel değişen dosyalarla   │
│    upstream commit'leri çakışıyor!                                         │
│ 💡 Tavsiye: Çalışmaya başlamadan önce pull veya rebase yapın.               │
╰─────────────────────────────────────────────────────────────────────────────╯
```

---

## ⚡ Saniyeden Hızlı Paralel Motor & Sıfır Token Akıllı Önbellek

Aynı brifing için boşuna beklemeyin veya gereksiz token harcamayın:
- **Paralel Not ve Git Okuma:** Çoklu not dosyalarını ve birden fazla Git deposunu eşzamanlı multi-thread I/O havuzlarıyla ışık hızında okur.
- **Deterministik SHA-256 Durum Önbelleği:** Notların içeriğini, mtime damgalarını, Git commit'lerini ve yapılandırmayı hashler. Girdiler değişmediyse brifingi <50ms içinde sunar:
  ```text
  ⚡ Anlık önbellekten yüklendi (0 token kullanıldı)
  ```
- **Önbelleği Atlama:** İstediğiniz zaman `--force` parametresiyle sıfırdan yapay zeka çalıştırması tetikleyebilirsiniz.

---

## ⏰ Otonom Sabah Zamanlayıcısı & Masaüstü Bildirimleri

Sabah masanıza oturmadan önce brifinginiz hazır olsun:

```bash
# Her sabah 08:45 için otonom brifing zamanla
dailybrief --schedule 08:45

# Zamanlanmış görevi kaldır
dailybrief --unschedule
```

- **İşletim Sisteminin Kendi Görev Yöneticisi:** Windows Görev Zamanlayıcı (`schtasks`) veya macOS/Linux `crontab` entegrasyonuyla çalışır.
- **Sessiz Arka Plan Modu:** Arka planda notları ve Git durumunu okur, anlık önbelleği ısıtır, `brief-YYYY-MM-DD.md` dosyasını kaydeder ve yerel masaüstü bildirimi gönderir:
  > *"⚡ Günün brifingi hazır! Terminalden `dailybrief` çalıştırarak görüntüleyin."*

---

## 🩺 Sistem Öz-Tanılaması (`dailybrief --doctor`)

Kurulumunuzu ve ortamınızı tek komutla denetleyin:

```bash
dailybrief --doctor
```

```text
                      DailyBrief Sistem Tanılama (Doctor)                      
┌──────────┬──────────────────┬────────┬──────────────────┬───────────────────┐
│ Kategori │ Kontrol          │ Durum  │ Detaylar         │ Öneri             │
├──────────┼──────────────────┼────────┼──────────────────┼───────────────────┤
│ Config   │ Ayar Dosyası     │ ✔ PASS │ ~/.dailybrief/…  │                   │
│ LLM      │ Anthropic Key    │ ✔ PASS │ Tanımlı (sk-…)   │                   │
│ Git      │ Git Komutu       │ ✔ PASS │ git v2.54.0      │                   │
│ Git      │ Aktif Git Deposu │ ✔ PASS │ 'main' dalı      │                   │
│ Notes    │ Notlar Klasörü   │ ✔ PASS │ 5 not bulundu    │                   │
│ Cache    │ İçerik Önbelleği │ ✔ PASS │ 9 hazır brifing  │                   │
│ Voice    │ Ses Motoru       │ ✔ PASS │ Windows SAPI COM │                   │
└──────────┴──────────────────┴────────┴──────────────────┴───────────────────┘
```

---

## 💻 Parametreler ve Seçenekler

```bash
dailybrief [SEÇENEKLER]
```

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `-s, --source <YOL>` | Notların okunacağı klasör yolu | `./notes` |
| `-l, --lang <en\|tr>` | Arayüz ve brifing dili (`tr` veya `en`) | `en` |
| `-p, --provider <ad>` | LLM sağlayıcısı (`anthropic`, `openai`, `gemini`, `ollama`) | `anthropic` |
| `-m, --model <ad>` | Özel model adı override | sağlayıcı varsayılanı |
| `-g, --git-repo <YOL>` | İzlenecek ek Git deposu yolu (tekrar edilebilir) | Mevcut klasör |
| `-i, --interactive` | Etkileşimli ajan menüsünü açar | `false` |
| `--eod` | Gün sonu otonom mutabakat modu | `false` |
| `--voice` | Yönetici sesli brifingini üretir ve çalar | `false` |
| `--mcp` | Standart stdio Model Context Protocol (MCP) sunucusu olarak çalıştırır | `false` |
| `--force` | Anlık önbelleği atlayarak yapay zeka ile taze brifing üretir | `false` |
| `--schedule <SS:DD>` | Belirtilen saatte otonom günlük sabah brifingi zamanlar | `None` |
| `--unschedule` | Zamanlanmış otonom görevi kaldırır | `false` |
| `--background` | Sessiz arka plan modunda çalışır ve masaüstü bildirimi gönderir | `false` |
| `--doctor` | Kapsamlı sistem tanılamasını çalıştırır | `false` |
| `--redact-pii` | Kimlik bilgilerine ek olarak e-posta ve IP adreslerini de sansürler | `false` |
| `--no-todos` | Kod içi `TODO`/`FIXME` yorumlarını taramayı devre dışı bırakır | `false` |
| `--weekly` | Haftalık sprint retrospektifi ve hız puan kartı üretir | `false` |
| `--init-shell <KABUK>` | Kabuk otomatik selamlama kancası üretir (`bash`, `zsh`, `powershell`, `fish`) | `None` |
| `--no-git` | Otomatik Git durumu ve commit taramasını kapatır | `false` |
| `--no-history` | Önceki günlerin brifing hafızasını ve tıkanıklık takibini kapatır | `false` |
| `-h, --help` | Yardım mesajını gösterir | |

---

## 🧪 Testler

136'dan fazla birim testini çalıştırmak için:

```bash
pytest
```

---

## 📄 Lisans

Bu proje MIT Lisansı altında sunulmaktadır. Ayrıntılar için [LICENSE](LICENSE) dosyasına bakabilirsiniz.
