# 🚀 Astria (Atria-ASI) Automated Bulk Farmer & Key Generator

An automated tool designed to bulk-register accounts, auto-bypass/receive OTP verification codes, authenticate, and generate API keys for the **Atria Dawn Preview (`Atria-Dawn-Preview`)** model API.

Includes direct auto-injection support into **9router / One-API / New-API** router backup JSON configurations, granting **100,000,000 (100M) tokens** per account.

---

## ✨ Features

- ⚡ **Automated Registration**: Automatically initializes OIDC interaction flows with Logto backend.
- 📬 **Auto-OTP Resolution**: Fetches disposable mail and extracts 6-digit verification codes automatically via regex without human intervention.
- 🔑 **Instant API Key Provisioning**: Generates `atr_...` API keys with customizable node names.
- 🔄 **Direct Router Injection**: Automatically inserts new active connections into your `9router-backup-*.json` file.
- 📦 **Standalone Export Mode**: Save harvested accounts and keys to a standalone `harvested_keys.json` formatted for easy copy-paste.
- 📊 **Interactive CLI**: Choose the number of accounts to farm, select output paths, and track real-time progress per account.

---

## 🛠️ Prerequisites

- Python 3.8+ (Compatible with Python 3.10, 3.12, 3.14+)
- Standard Python libraries only (`urllib`, `http.cookiejar`, `json`, `re`, `uuid`) - **No external pip dependencies required!**

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/ahkurdev/Astria-Asi-Farmer.git
cd Astria-Asi-Farmer
```

### 2. Run Farmer
On Windows:
```powershell
py atria_bulk_farmer.py
# Or simply double-click run_farmer.bat
```

On Linux / macOS:
```bash
python3 atria_bulk_farmer.py
```

---

## 💻 Interactive Usage

When launched, the script will prompt you interactively:

```text
=================================================================
        ENI'S ATRIA AUTOMATED BULK FARMING TOOL v2.0            
=================================================================

>> Mau panen berapa akun, sayang? (Contoh: 5 / 10 / 500): 5

>> Mau langsung di-inject ke file backup router 9router kamu?
   Pilih (y/n) [Default: y]: y

   Target path default: c:\path\to\9router-backup.json
   Tekan [ENTER] untuk pakai path default, atau ketik path lain: 
```

### Real-Time Live Output:
```text
[*] MEMULAI PROSES FARMING (5 Akun Target)...
=================================================================

--------------------------------------------------
[*] Try 1 account...
    Email: trdwnllx@guerrillamailblock.com
    Mengirim OTP... Menunggu kode masuk...
    OTP diterima: 306306
[+] Try 1 account: SUKSES -> Key: atr_eHdWrgPujtORx2CNXqvOia1vwdelIBkr
    [Status Sementara: 1 Sukses | 0 Gagal | Total Target: 5]

=================================================================
[+] Berhasil menginjeksi 5 koneksi langsung ke: 9router-backup.json

>>> 5 account success 500,000,000 token granted <<<
=================================================================
```

---

## 📂 Project Structure

```text
├── atria_bulk_farmer.py     # Main bulk farming & injection script
├── run_farmer.bat           # Windows 1-click execution batch launcher
├── harvested_keys.json      # Standalone harvested keys output (generated)
└── README.md                # Documentation
```

---

## ⚙️ Model Information

- **Model ID**: `Atria-Dawn-Preview`
- **Context Window**: `256K tokens`
- **Base URL**: `https://api.atria-asi.ai/v1`
- **Endpoints**: Supports OpenAI Chat Completions (`/v1/chat/completions`) and Anthropic Messages (`/v1/messages`).

---

## 📜 Disclaimer

This project is created strictly for educational, research, and authorized testing purposes. Please adhere to the terms of service of the respective service providers.
