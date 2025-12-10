# 📋 תוכנית תשתית אחסון חיצוני למערכת Nervesys
# External Storage Infrastructure Plan for Nervesys

**תאריך / Date:** 2025-12-10  
**סטטוס / Status:** תכנון / Planning  
**גרסה / Version:** 2.0 - ארכיטקטורת "הסוכן הרזה"  
**מטרה / Goal:** הגדרת מאגר נתונים (DB) ומערכת לוגים חיצונית לכל סוכני ה-AI

---

## 🎯 עקרון מנחה: "הסוכן הרזה" (The Lean Agent)

**המטרה:** הסוכן שוקל כמעט כלום. אין לו DB כבד מקומי. הוא רק "צינור" שמעביר מידע החוצה.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LEAN AGENT ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────┐    git pull     ┌─────────────────────────────────┐  │
│   │   GitHub    │◄───────────────►│  Agent (AIGARDEN01 / Server)    │  │
│   │  nervesys   │   Config/Brain  │  ┌─────────────────────────┐    │  │
│   └─────────────┘                 │  │  SQLite Buffer (≤100MB) │    │  │
│                                   │  └───────────┬─────────────┘    │  │
│   ┌─────────────┐                 │              │                  │  │
│   │   Storj     │◄────────────────│──────────────┤ Upload & Delete  │  │
│   │  (Archive)  │   GZIP Logs     │              │ Every 10 min     │  │
│   └─────────────┘                 │              │                  │  │
│                                   │              ▼                  │  │
│   ┌─────────────┐                 │  ┌─────────────────────────┐    │  │
│   │ Orchestrator│◄────────────────│──│    Heartbeat/Status     │    │  │
│   │  Postgres   │   Real-time     │  │  (CPU, RAM, Alerts)     │    │  │
│   └─────────────┘                 │  └─────────────────────────┘    │  │
│                                   └─────────────────────────────────┘  │
│   ┌─────────────┐                                                      │
│   │Google Drive │◄──────────────── Daily PDF/Excel Reports             │
│   │  (Reports)  │                                                      │
│   └─────────────┘                                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🧠 שכבה 1: המוח וההגדרות (GitHub - Nervesys)

**השיטה:** GitOps - הסוכן לא מחזיק לוגיקה קשיחה. הוא מושך אותה.

### הפעולה:
כשסוכן (Agent) עולה ב-AIGARDEN01 או בכל מקום אחר:
```bash
git pull https://github.com/bitonpro/nervesys
```

### מה הסוכן מקבל:
- **Config** - מי אני? מה התפקיד שלי?
- **Thresholds** - מה הספים להתראה?
- **Rules** - כללי התנהגות ולוגיקה

### היתרון:
✅ שינוי אחד בגיטהאב מעדכן את **כל** החווה!

### מבנה Config מוצע ב-nervesys:
```
nervesys/
├── config/
│   ├── agents/
│   │   ├── grok.yaml
│   │   ├── deepseek.yaml
│   │   ├── gimai.yaml
│   │   ├── chatgpt.yaml
│   │   └── copilot.yaml
│   ├── thresholds.yaml       # ספים להתראות
│   ├── orchestrator.yaml     # הגדרות Orchestrator
│   └── storage.yaml          # הגדרות Storj/Google Drive
└── scripts/
    ├── agent_bootstrap.sh    # סקריפט אתחול סוכן
    └── sync_config.sh        # סנכרון הגדרות
```

---

## 💾 שכבה 2: זיכרון לטווח קצר (SQLite / RAM Buffer)

**המטרה:** סוכן AI צריך לזכור מה קרה לפני דקה. אבל **אסור** לו לתפוס מקום.

### הפתרון:
שימוש ב-**SQLite** (קובץ בודד) או **In-Memory DB**

### הפעולה:
```
הסוכן רושם לוגים ונתונים לקובץ זמני מקומי:
/tmp/agent/buffer.db
```

### 🚨 החוק הקדוש:
```
הקובץ הזה לעולם לא עובר גודל של 100MB!
אם הוא מתמלא → הוא נשלח החוצה ונמחק.
```

### מבנה טבלת Buffer:
```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    level TEXT,           -- INFO, WARN, ERROR, CRITICAL
    agent_id TEXT,
    action TEXT,
    message TEXT,
    context TEXT,         -- JSON stored as TEXT (SQLite 3.9+ has JSON1 extension)
    uploaded INTEGER DEFAULT 0
);

-- Index for quick queries
CREATE INDEX idx_uploaded ON logs(uploaded);
CREATE INDEX idx_timestamp ON logs(timestamp);
CREATE INDEX idx_agent_time ON logs(agent_id, timestamp);
```

**הערה:** SQLite 3.9+ תומך ב-JSON1 extension. אם משתמשים בגרסה ישנה יותר, הנתונים נשמרים כ-TEXT.

---

## 📦 שכבה 3: זיכרון לטווח ארוך (Storj - Archive)

**המטרה:** זה ה"מחסן" - כל ההיסטוריה נשמרת כאן.

### הבאקט (Bucket):
```
שם: owalai-production
אזור: EU1 (כפי שמופיע בקישור שלך)
```

### מבנה הארכיון:
```
owalai-production/
├── logs/
│   ├── AIGARDEN01/
│   │   ├── 2025-12-10/
│   │   │   ├── 00-00.json.gz
│   │   │   ├── 00-10.json.gz
│   │   │   └── ...
│   │   └── 2025-12-11/
│   └── AIGARDEN02/
├── backups/
│   └── daily/
└── configs/
    └── snapshots/
```

### הפעולה (כל 10 דקות או 10MB):
```
1. הסוכן צובר לוגים ב-SQLite
2. הסוכן דוחס אותם (GZIP) - הקטנה של ~90%!
3. הסוכן שולח (Upload) ל-Storj דרך פרוטוקול S3
4. הסוכן מוחק את הקובץ המקומי
```

### ✅ התוצאה:
**הדיסק של השרת המקומי נשאר ריק תמיד!**

### Environment Variables:
```bash
# Storj Configuration
STORJ_ACCESS_KEY=<your-access-key>
STORJ_SECRET_KEY=<your-secret-key>
STORJ_BUCKET=owalai-production
STORJ_ENDPOINT=https://gateway.storjshare.io
STORJ_REGION=eu1
```

---

## ⚡ שכבה 4: מצב בזמן אמת (Postgres ב-Orchestrator)

**המטרה:** Storj זה לארכיון (היסטוריה). ה-AI המרכזי צריך לדעת מה קורה **עכשיו**.

### הפעולה:
הסוכן שולח **"דופק" (Heartbeat)** וסטטוס קריטי:
```json
{
  "agent_id": "GROK",
  "server": "AIGARDEN01",
  "timestamp": "2025-12-10T19:45:00Z",
  "status": "healthy",
  "metrics": {
    "cpu_percent": 45.2,
    "ram_percent": 62.1,
    "disk_percent": 23.4,
    "buffer_size_mb": 12.5
  },
  "alerts": [],
  "last_action": "code_review",
  "uptime_seconds": 86400
}
```

### זה נשמר ב-Postgres המרכזי (OVH):
```sql
CREATE TABLE agent_status (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(50),
    server VARCHAR(100),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20),
    metrics JSONB,
    alerts JSONB,
    last_action VARCHAR(100),
    uptime_seconds INTEGER
);

-- Index for real-time queries
CREATE INDEX idx_agent_status_time ON agent_status(agent_id, timestamp DESC);
```

---

## 📊 שכבה 5: דוחות מנהלים (Google Drive)

**הכלל:** אל תשתמש ב-Drive ללוגים. תשתמש בו לדוחות אנושיים!

### הפעולה:
ה-**Orchestrator** מייצר בסוף יום:
- דוח PDF מסכם
- Excel עם נתונים
- גרפים ותרשימים

### מבנה ב-Google Drive:
```
OWAL AI Reports/
├── Daily/
│   ├── 2025-12-10_summary.pdf
│   ├── 2025-12-10_metrics.xlsx
│   └── ...
├── Weekly/
│   └── Week_50_2025.pdf
└── Alerts/
    └── Critical_2025-12-10.pdf
```

### היתרון:
✅ קריאה אנושית נוחה
✅ שיתוף קל עם הצוות
✅ לא עומס על המערכת

---

## 🛠️ Best Practices - עצות לשיפור

### 1️⃣ דחיסה לפני שליחה (Compression)
```
❌ לעולם אל תשלח טקסט (Log) גולמי ל-Storj!
✅ הסוכן צריך לדחוס ל-GZIP לפני השליחה
📉 זה מקטין את הנפח ב-90%!
```

### 2️⃣ Zero-Config Agent
```
הסוכן לא צריך לדעת כלום כשהוא מותקן חוץ מ-Token אחד!

עם הטוקן הזה הוא:
1. הולך ל-Orchestrator
2. מקבל את ה-Storj Credentials
3. מקבל את ה-Git Config
4. מתחיל לעבוד!
```

### 3️⃣ Buffer למקרה של נתק
```
אם האינטרנט נופל, הסוכן לא קורס!

הסוכן:
1. ממשיך לכתוב ל-SQLite המקומי
2. ברגע שהרשת חוזרת
3. "מקיא" את כל המידע ל-Storj
4. מתרוקן
```

### 4️⃣ Edge AI - לוגיקה חכמה
```
לפני שהסוכן שולח לוג שגיאה ל-Storj:

ה-AI הקטן המקומי מנתח אותו:
- אם זה קריטי → התראה מיידית ל-API
- אם זה סתם "Info" → זה הולך לארכיון ב-Storj

אפשרויות מודל Edge:
- TinyLlama 1.1B (מומלץ - קל וחזק)
- Phi-2 (Microsoft)
- או כל מודל GGUF קטן
```

---

## 📋 סיכום הפעולה המיידית

### שלב 1: Storj
```bash
# צור Bucket בשם owalai-production
# צור Access Key ו-Secret Key
# שמור אותם במקום בטוח!
```

### שלב 2: Orchestrator
```bash
# הכנס את המפתחות ל-Vault
# (ב-docker-compose של השרת הראשי)
```

### שלב 3: Agent
```bash
# עדכן את הסקריפט:
# - לא לשמור לוגים מקומית לנצח
# - Upload & Delete ל-Storj כל 10 דקות
```

---

## 🔄 הפתרון המשולש - סיכום

| שכבה | מטרה | טכנולוגיה | תדירות |
|------|------|-----------|---------|
| **1. Real-time** | מה קורה עכשיו | Postgres (Orchestrator) | כל דקה (Heartbeat) |
| **2. Archive** | היסטוריה ולוגים | Storj (S3) | כל 10 דק / 10MB |
| **3. Reports** | קריאה אנושית | Google Drive | יומי |

### תרשים זרימה:
```
Agent Local          →  Orchestrator API  →  Postgres (Real-time)
     ↓
SQLite Buffer (≤100MB)
     ↓
GZIP Compress
     ↓
Storj Upload (Archive)
     ↓
Local Delete
     ↓
Orchestrator generates  →  Google Drive (Daily Reports)
```

---

## 📁 מבנה קבצים מוצע לפרויקט

```
nervesys/
├── CONTRIBUTORS.json              # AI Collaborators
├── docs/
│   ├── STORAGE_INFRASTRUCTURE_PLAN.md
│   ├── SETUP.md
│   └── API.md
├── config/
│   ├── agents/
│   │   ├── grok.yaml
│   │   ├── deepseek.yaml
│   │   ├── gimai.yaml
│   │   ├── chatgpt.yaml
│   │   └── copilot.yaml
│   ├── thresholds.yaml
│   ├── orchestrator.yaml
│   └── storage.yaml
├── src/
│   ├── agent/
│   │   ├── bootstrap.py          # Agent startup
│   │   ├── buffer.py             # SQLite buffer management
│   │   ├── uploader.py           # Storj upload logic
│   │   ├── heartbeat.py          # Real-time status
│   │   └── edge_ai.py            # Local AI analysis
│   ├── orchestrator/
│   │   ├── api.py                # REST API
│   │   ├── database.py           # Postgres connection
│   │   └── reports.py            # PDF/Excel generation
│   └── storage/
│       ├── storj_client.py       # S3 compatible client
│       └── gdrive_client.py      # Google Drive API
├── scripts/
│   ├── agent_bootstrap.sh
│   ├── sync_config.sh
│   └── generate_reports.sh
├── tests/
│   └── test_storage.py
└── .env.example
```

---

## ⏭️ הצעדים הבאים / Next Steps

### מיידי (היום):
1. ✅ אשר את התוכנית
2. צור Bucket `owalai-production` ב-Storj
3. צור Access Key ו-Secret Key

### שבוע 1:
4. הגדר Agent bootstrap script
5. יישם SQLite buffer
6. יישם Storj upload

### שבוע 2:
7. הגדר Orchestrator API
8. חבר Postgres
9. יישם Heartbeat

### שבוע 3:
10. חבר Google Drive
11. יישם דוחות יומיים
12. בדיקות E2E

---

## 🤔 שאלות לבירור

1. **שם הבאקט** - `owalai-production` או שם אחר?
2. **Edge AI** - להשתמש ב-TinyLlama או מודל אחר?
3. **תדירות דוחות** - יומי מספיק או צריך גם שבועי?
4. **Orchestrator** - איפה הוא יושב? OVH?

---

**הערה:** תוכנית זו מבוססת על ארכיטקטורת "הסוכן הרזה" - מינימום מקומי, מקסימום בענן!

---

*נוצר על ידי GitHub Copilot עבור פרויקט Nervesys - גרסה 2.0*
