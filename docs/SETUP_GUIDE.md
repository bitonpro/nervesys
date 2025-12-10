# 🛠️ מדריך התקנה - OWAL AI OS Setup Guide
# Step-by-Step Infrastructure Setup

**תאריך / Date:** 2025-12-10  
**גרסה / Version:** 1.0  
**מטרה / Goal:** הגדרת כל התשתיות לפני התקנת הסוכן

---

## 📋 סדר הפעולות / Setup Order

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SETUP ORDER / סדר ההתקנה                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STEP 1: Setup External Services (Storj, Google Drive, Grafana)            │
│     ↓                                                                       │
│  STEP 2: Collect Credentials (URLs, API Keys, Tokens)                      │
│     ↓                                                                       │
│  STEP 3: Create Config Files in nervesys GitHub                            │
│     ↓                                                                       │
│  STEP 4: Test Connections                                                   │
│     ↓                                                                       │
│  STEP 5: Deploy Agent                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ שלב 1: הגדרת Storj (External DB)

### 1.1 יצירת חשבון (כבר יש לך!)
- **URL:** https://eu1.storj.io
- **Project:** כבר קיים

### 1.2 יצירת Bucket
```
שם הבאקט: owalai-production
אזור: EU1
הצפנה: Enabled
```

**בממשק Storj:**
1. לחץ על "Buckets" בתפריט
2. לחץ "+ Create Bucket"
3. הכנס שם: `owalai-production`
4. לחץ "Create"

### 1.3 יצירת Access Key
1. לחץ על "Access" בתפריט
2. לחץ "Create S3 Credentials"
3. בחר:
   - Name: `owalai-agent`
   - Permissions: `All` (או רק `Read`, `Write`, `List`, `Delete`)
   - Buckets: `owalai-production`
4. לחץ "Create Access"

### 1.4 שמור את הפרטים!
```
📝 שמור את הערכים האלה:
┌─────────────────────────────────────────────────────────────────┐
│ STORJ_ACCESS_KEY = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX            │
│ STORJ_SECRET_KEY = YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY    │
│ STORJ_ENDPOINT   = https://gateway.storjshare.io               │
│ STORJ_BUCKET     = owalai-production                           │
│ STORJ_REGION     = eu1                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 שלב 2: הגדרת Google Drive (Archive)

### 2.1 יצירת תיקייה ב-Google Drive
1. פתח Google Drive
2. צור תיקייה חדשה: `OWAL-AI-Archive`
3. צור תת-תיקיות:
   ```
   OWAL-AI-Archive/
   ├── Logs/
   ├── Reports/
   │   ├── Daily/
   │   └── Weekly/
   └── Backups/
   ```

### 2.2 יצירת Service Account (לגישה מהסוכן)

**בGoogle Cloud Console:**
1. לך ל: https://console.cloud.google.com
2. צור פרויקט חדש או בחר קיים
3. לחץ "APIs & Services" → "Credentials"
4. לחץ "+ Create Credentials" → "Service Account"
5. הכנס שם: `owalai-drive-access`
6. לחץ "Create"
7. הוסף Role: "Editor"
8. לחץ "Done"

### 2.3 יצירת מפתח
1. לחץ על ה-Service Account שיצרת
2. לחץ "Keys" → "Add Key" → "Create New Key"
3. בחר "JSON"
4. הורד את הקובץ

### 2.4 שיתוף התיקייה עם Service Account
1. בGoogle Drive, לחץ ימני על `OWAL-AI-Archive`
2. לחץ "Share"
3. הכנס את האימייל של ה-Service Account:
   `owalai-drive-access@your-project.iam.gserviceaccount.com`
4. תן הרשאת "Editor"

### 2.5 שמור את הפרטים!
```
📝 שמור את הערכים האלה:
┌─────────────────────────────────────────────────────────────────┐
│ GDRIVE_SERVICE_ACCOUNT_JSON = (תוכן קובץ ה-JSON)               │
│ GDRIVE_FOLDER_ID = your-folder-id-here                          │
│   (מה-URL של התיקייה: drive.google.com/drive/folders/ID_HERE)  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 שלב 3: הגדרת Grafana (Monitor)

### אפשרות A: Grafana Cloud (מומלץ להתחלה)
1. לך ל: https://grafana.com/products/cloud/
2. צור חשבון חינמי
3. צור ארגון חדש

### אפשרות B: Self-Hosted Grafana
```bash
# Docker
docker run -d \
  --name=grafana \
  -p 3000:3000 \
  -v grafana-storage:/var/lib/grafana \
  grafana/grafana
```

### 3.1 יצירת API Key
1. לך ל: Configuration → API Keys
2. לחץ "Add API Key"
3. שם: `owalai-agent`
4. Role: `Editor`
5. לחץ "Add"

### 3.2 שמור את הפרטים!
```
📝 שמור את הערכים האלה:
┌─────────────────────────────────────────────────────────────────┐
│ GRAFANA_URL     = https://your-instance.grafana.net            │
│ GRAFANA_API_KEY = glsa_XXXXXXXXXXXXXXXXXXXXXXXXX               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ שלב 4: הגדרת Proxmox (אם רלוונטי)

### 4.1 יצירת API Token ב-Proxmox
1. התחבר ל-Proxmox Web UI
2. לך ל: Datacenter → Permissions → API Tokens
3. לחץ "Add"
4. הגדר:
   - User: `root@pam` (או משתמש אחר)
   - Token ID: `owalai`
   - Privilege Separation: ✅
5. לחץ "Add"

### 4.2 הגדרת הרשאות
1. לך ל: Datacenter → Permissions
2. לחץ "Add" → "API Token Permission"
3. הוסף את ההרשאות הנדרשות

### 4.3 שמור את הפרטים!
```
📝 שמור את הערכים האלה:
┌─────────────────────────────────────────────────────────────────┐
│ PROXMOX_URL   = https://proxmox.example.com:8006               │
│ PROXMOX_TOKEN = root@pam!owalai=XXXX-XXXX-XXXX-XXXX           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 שלב 5: הגדרת Alibaba Cloud AI (אופציונלי)

### 5.1 יצירת API Key
1. לך ל: Alibaba Cloud Console
2. לך ל: RAM → Users
3. צור Access Key

### 5.2 שמור את הפרטים!
```
📝 שמור את הערכים האלה:
┌─────────────────────────────────────────────────────────────────┐
│ ALIBABA_ACCESS_KEY = XXXXXXXXXXXXXXXX                          │
│ ALIBABA_SECRET_KEY = YYYYYYYYYYYYYYYY                          │
│ ALIBABA_REGION     = cn-shanghai (או אחר)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📄 שלב 6: יצירת קבצי Config ב-GitHub

### 6.1 מבנה התיקיות ב-nervesys
```
nervesys/
├── config/
│   ├── storage.yaml        # הגדרות Storj + Google Drive
│   ├── monitoring.yaml     # הגדרות Grafana
│   ├── proxmox.yaml        # הגדרות Proxmox
│   ├── alibaba.yaml        # הגדרות Alibaba Cloud
│   └── agents/
│       ├── default.yaml    # הגדרות ברירת מחדל
│       └── {hostname}.yaml # הגדרות ספציפיות לשרת
└── .env.example            # דוגמה לסודות (לא הסודות עצמם!)
```

### 6.2 קובץ storage.yaml
```yaml
# config/storage.yaml
# External Storage Configuration

storj:
  # Endpoint and region (can be in git - not secret)
  endpoint: "https://gateway.storjshare.io"
  region: "eu1"
  bucket: "owalai-production"
  
  # Paths inside bucket
  paths:
    logs: "logs/{server}/{date}/"
    metrics: "metrics/{server}/{date}/"
    backups: "backups/{server}/{date}/"
  
  # Upload settings
  upload:
    interval_minutes: 10
    max_buffer_mb: 100
    compress: true  # GZIP

google_drive:
  # Folder structure
  folders:
    archive: "OWAL-AI-Archive"
    logs: "Logs"
    reports: "Reports"
    backups: "Backups"
  
  # Sync settings
  sync:
    reports_daily: true
    reports_weekly: true
    archive_after_days: 7
```

### 6.3 קובץ monitoring.yaml
```yaml
# config/monitoring.yaml
# Grafana Configuration

grafana:
  # URL can be in git (not the API key!)
  # API key should be in environment variable
  
  dashboards:
    - name: "Agent Overview"
      uid: "owalai-overview"
    - name: "Server Metrics"
      uid: "owalai-metrics"
    - name: "Alerts"
      uid: "owalai-alerts"
  
  alerts:
    cpu_threshold: 90
    memory_threshold: 85
    disk_threshold: 80
    heartbeat_timeout_seconds: 300
```

### 6.4 קובץ .env.example
```bash
# .env.example
# Copy this to .env and fill in your values
# NEVER commit .env to git!

# Storj
STORJ_ACCESS_KEY=your-access-key-here
STORJ_SECRET_KEY=your-secret-key-here

# Google Drive
GDRIVE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'
GDRIVE_FOLDER_ID=your-folder-id-here

# Grafana
GRAFANA_URL=https://your-instance.grafana.net
GRAFANA_API_KEY=your-api-key-here

# Proxmox (optional)
PROXMOX_URL=https://proxmox.example.com:8006
PROXMOX_TOKEN=your-token-here

# Alibaba Cloud (optional)
ALIBABA_ACCESS_KEY=your-access-key-here
ALIBABA_SECRET_KEY=your-secret-key-here
```

---

## ✅ שלב 7: צ'קליסט סופי

### לפני שממשיכים, וודא:

```
□ Storj
  □ Bucket נוצר: owalai-production
  □ Access Key נוצר
  □ Secret Key נשמר במקום בטוח

□ Google Drive
  □ תיקייה נוצרה: OWAL-AI-Archive
  □ Service Account נוצר
  □ JSON Key הורד
  □ תיקייה שותפה עם Service Account

□ Grafana
  □ Instance פועל (Cloud או Self-hosted)
  □ API Key נוצר

□ Proxmox (אם רלוונטי)
  □ API Token נוצר
  □ הרשאות הוגדרו

□ GitHub nervesys
  □ config/storage.yaml נוצר
  □ config/monitoring.yaml נוצר
  □ .env.example נוצר
  □ .gitignore מכיל .env
```

---

## 🚀 שלב 8: פריסת הסוכן

אחרי שכל הנ"ל מוכן:

```bash
# 1. Clone nervesys
git clone https://github.com/bitonpro/nervesys
cd nervesys

# 2. Copy env example and fill values
cp .env.example .env
nano .env  # Fill in your secrets

# 3. Run agent
docker run -d \
  --name owalai-agent \
  --env-file .env \
  owalai/agent:latest
```

---

## 📊 תרשים זרימה מלא

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COMPLETE SETUP FLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  YOU (Setup Phase)                                                          │
│  ════════════════                                                           │
│       │                                                                     │
│       ├──► Storj Console ───► Create Bucket ───► Create Keys               │
│       │         │                                                           │
│       │         └──► Get: ACCESS_KEY, SECRET_KEY, BUCKET, ENDPOINT         │
│       │                                                                     │
│       ├──► Google Cloud ───► Create Service Account ───► Create Key        │
│       │         │                                                           │
│       │         └──► Get: SERVICE_ACCOUNT_JSON, FOLDER_ID                  │
│       │                                                                     │
│       ├──► Grafana ───► Create Instance ───► Create API Key                │
│       │         │                                                           │
│       │         └──► Get: GRAFANA_URL, API_KEY                             │
│       │                                                                     │
│       └──► Proxmox ───► Create API Token                                   │
│                 │                                                           │
│                 └──► Get: PROXMOX_URL, TOKEN                               │
│                                                                             │
│  ═════════════════════════════════════════════════════════════════════════ │
│                                                                             │
│  GitHub nervesys (Config Files)                                             │
│  ══════════════════════════════                                             │
│       │                                                                     │
│       ├──► config/storage.yaml      (Non-secret settings)                  │
│       ├──► config/monitoring.yaml   (Non-secret settings)                  │
│       ├──► config/proxmox.yaml      (Non-secret settings)                  │
│       └──► .env.example             (Template for secrets)                 │
│                                                                             │
│  ═════════════════════════════════════════════════════════════════════════ │
│                                                                             │
│  Agent Deployment                                                           │
│  ════════════════                                                           │
│       │                                                                     │
│       ├──► git pull nervesys                                               │
│       ├──► Create .env (with real secrets)                                 │
│       └──► docker run owalai/agent                                         │
│                                                                             │
│  ═════════════════════════════════════════════════════════════════════════ │
│                                                                             │
│  Agent Running                                                              │
│  ═════════════                                                              │
│       │                                                                     │
│       ├──► Reads config from GitHub                                        │
│       ├──► Reads secrets from .env                                         │
│       ├──► Connects to Storj, GDrive, Grafana                             │
│       └──► Starts working!                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 חשוב לגבי אבטחה

```
⚠️ מה לשים ב-GitHub (בטוח):
   ✅ URLs (endpoints)
   ✅ Bucket names
   ✅ Folder IDs
   ✅ Dashboard configs
   ✅ Threshold values

⚠️ מה לא לשים ב-GitHub (סודי):
   ❌ Access Keys
   ❌ Secret Keys
   ❌ API Tokens
   ❌ Passwords
   ❌ Service Account JSON
```

**הסודות יישמרו:**
- בקובץ `.env` מקומי (לא ב-git!)
- או ב-Vault (HashiCorp)
- או ב-GitHub Secrets (לCI/CD)

---

*מדריך זה יעזור להכין את כל התשתיות לפני התקנת הסוכן*
