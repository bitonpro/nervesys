# 📋 תוכנית תשתית אחסון חיצוני למערכת Nervesys
# External Storage Infrastructure Plan for Nervesys

**תאריך / Date:** 2025-12-10  
**סטטוס / Status:** תכנון / Planning  
**מטרה / Goal:** הגדרת מאגר נתונים (DB) ומערכת לוגים חיצונית לכל סוכני ה-AI

---

## 🎯 מטרות / Objectives

1. **מאגר נתונים (Database)** - מקום מרכזי לשמירת מידע, היסטוריה, והחלטות של כל AI
2. **מערכת לוגים (Logging)** - תיעוד פעולות, שגיאות, ותקשורת בין הסוכנים
3. **אחסון חיצוני** - שמירת קבצים, מסמכים, וגיבויים

---

## 🔍 השוואת אפשרויות / Options Comparison

### אפשרות 1: Storj (מומלץ! ✅)
**קישור:** https://eu1.storj.io

| יתרון | תיאור |
|-------|-------|
| ✅ **מבוזר** | אחסון מבוזר - אמינות גבוהה |
| ✅ **S3 Compatible** | תואם AWS S3 API - קל לאינטגרציה |
| ✅ **הצפנה** | הצפנה מקצה לקצה |
| ✅ **עלות** | זול יותר מ-AWS/GCP |
| ✅ **יש לך מנוי** | כבר יש לך חשבון פעיל! |

**מבנה מומלץ ב-Storj:**
```
nervesys-bucket/
├── databases/
│   ├── grok/
│   ├── deepseek/
│   ├── gimai/
│   ├── chatgpt/
│   └── copilot/
├── logs/
│   ├── system/
│   ├── errors/
│   └── activity/
├── backups/
│   └── daily/
└── shared/
    └── knowledge-base/
```

### אפשרות 2: Google Drive
| יתרון | חסרון |
|-------|-------|
| ✅ ממשק ידידותי | ❌ API מוגבל |
| ✅ שיתוף קל | ❌ לא מתאים ל-DB |
| ✅ חינמי עד 15GB | ❌ לא S3 compatible |

**מסקנה:** Google Drive מתאים לגיבוי מסמכים, לא לבסיס נתונים פעיל.

### אפשרות 3: פתרון משולב (Best Practice ⭐)
```
┌──────────────────────────────────────────────────────┐
│                    NERVESYS                          │
├──────────────────────────────────────────────────────┤
│  Storj (Primary)          │  Google Drive (Backup)  │
│  ├── Database files       │  ├── Documents          │
│  ├── Real-time logs       │  ├── Reports            │
│  └── Active storage       │  └── Archives           │
└──────────────────────────────────────────────────────┘
```

---

## 📊 שלב 1: בחירת בסיס נתונים / Database Selection

### אפשרויות מומלצות:

#### 1️⃣ SQLite + Storj (פשוט ביותר)
```
יתרונות:
- ✅ קובץ בודד - קל לגבות
- ✅ אין צורך בשרת
- ✅ מושלם להתחלה

חסרונות:
- ❌ לא מתאים לגישה במקביל
```

#### 2️⃣ PostgreSQL + Supabase (מומלץ לסביבת ייצור)
```
יתרונות:
- ✅ מנוהל בענן
- ✅ API מובנה
- ✅ Real-time capabilities
- ✅ Free tier זמין

חסרונות:
- ❌ יותר מורכב להתקנה
```

#### 3️⃣ MongoDB Atlas (NoSQL)
```
יתרונות:
- ✅ גמיש - מתאים ללוגים
- ✅ Free tier 512MB

חסרונות:
- ❌ פחות מתאים לנתונים מובנים
```

### המלצה: התחל עם SQLite + Storj, שדרג ל-Supabase כשצריך

---

## 📝 שלב 2: מבנה הלוגים / Logging Structure

### מבנה לוג מוצע:
```json
{
  "timestamp": "2025-12-10T19:30:00Z",
  "agent_id": "GROK",
  "level": "INFO|WARN|ERROR|DEBUG",
  "action": "code_review",
  "message": "Reviewed PR #42",
  "context": {
    "repository": "nervesys",
    "file": "main.py",
    "duration_ms": 1234
  },
  "metadata": {
    "model_version": "latest",
    "tokens_used": 500
  }
}
```

### קטגוריות לוגים:
| קטגוריה | תיאור | שמירה |
|---------|-------|-------|
| `system` | אתחול, כיבוי, שגיאות קריטיות | 90 יום |
| `activity` | פעולות שוטפות | 30 יום |
| `errors` | שגיאות ואזהרות | 180 יום |
| `audit` | פעולות רגישות | שנה |

---

## 🛠️ שלב 3: תוכנית יישום / Implementation Plan

### שבוע 1: הכנה
- [ ] הגדרת Bucket ב-Storj
- [ ] יצירת Access Keys
- [ ] בדיקת חיבור בסיסי

### שבוע 2: בסיס נתונים
- [ ] יצירת סכמת DB
- [ ] טבלאות עבור כל AI agent
- [ ] הגדרת גיבויים אוטומטיים

### שבוע 3: מערכת לוגים
- [ ] יצירת מודול logging
- [ ] הגדרת רמות לוגים
- [ ] בדיקות

### שבוע 4: אינטגרציה
- [ ] חיבור כל הסוכנים למערכת
- [ ] בדיקות E2E
- [ ] תיעוד

---

## 🔧 שלב 4: הגדרות Storj / Storj Setup

### 4.1 יצירת Bucket
```
שם: nervesys-storage
אזור: EU1 (כפי שמופיע בקישור שלך)
הצפנה: Server-side + Client-side (מומלץ)
```

### 4.2 Access Grants
צור שני Access Grants נפרדים:
1. **nervesys-db-access** - גישה מלאה ל-databases/
2. **nervesys-logs-access** - גישה לכתיבה ל-logs/

### 4.3 Environment Variables (לעתיד)
```
STORJ_ACCESS_GRANT=<your-access-grant>
STORJ_BUCKET=nervesys-storage
STORJ_ENDPOINT=https://gateway.storjshare.io
```

---

## 💡 שלב 5: עצות לשיפור / Improvement Tips

### 🔐 אבטחה
1. **הפרדת הרשאות** - כל AI מקבל גישה רק למה שהוא צריך
2. **הצפנת נתונים** - השתמש ב-encryption של Storj
3. **Audit trail** - תעד כל גישה לנתונים
4. **גיבוי כפול** - Storj + Google Drive למסמכים חשובים

### 📈 ביצועים
1. **Caching** - שמור נתונים נפוצים מקומית
2. **Batch writes** - כתוב לוגים באצוות, לא אחד-אחד
3. **Compression** - דחוס לוגים ישנים
4. **Retention policy** - מחק לוגים ישנים אוטומטית

### 🔄 אמינות
1. **Health checks** - בדוק חיבור ל-Storj מדי שעה
2. **Retry logic** - נסה שוב אם הכתיבה נכשלה
3. **Fallback** - אם Storj לא זמין, שמור מקומית זמנית
4. **Monitoring** - התראות על שגיאות

### 🤝 שיתוף פעולה בין AI
1. **Shared knowledge base** - מאגר ידע משותף לכל הסוכנים
2. **Communication logs** - תיעוד תקשורת בין סוכנים
3. **Task history** - היסטוריית משימות
4. **Learning from errors** - למידה משגיאות עבר

---

## 📁 שלב 6: מבנה קבצים מוצע לפרויקט

```
nervesys/
├── CONTRIBUTORS.json          # קיים
├── docs/
│   ├── STORAGE_INFRASTRUCTURE_PLAN.md  # קובץ זה
│   ├── SETUP.md
│   └── API.md
├── src/
│   ├── storage/
│   │   ├── storj_client.py    # לקוח Storj
│   │   ├── database.py        # ניהול DB
│   │   └── logger.py          # מערכת לוגים
│   ├── agents/
│   │   ├── base_agent.py      # מחלקת בסיס
│   │   ├── grok.py
│   │   ├── deepseek.py
│   │   ├── gimai.py
│   │   ├── chatgpt.py
│   │   └── copilot.py
│   └── config/
│       └── settings.py        # הגדרות
├── tests/
│   └── test_storage.py
└── .env.example               # דוגמה למשתני סביבה
```

---

## ⏭️ הצעדים הבאים / Next Steps

1. **אשר את התוכנית** - האם זה מה שחשבת?
2. **הגדר Storj** - צור Bucket ו-Access Grant
3. **שתף פרטי גישה** - (באופן מאובטח!)
4. **התחל יישום** - נתחיל לכתוב קוד?

---

## 📞 שאלות לבירור / Questions to Clarify

לפני שממשיכים, אשמח לדעת:

1. **עדיפות** - מה חשוב יותר קודם: DB או לוגים?
2. **שפת תכנות** - Python? Node.js? אחר?
3. **רמת מורכבות** - התחלה מינימלית פשוטה או מערכת מלאה?
4. **Google Drive** - רוצה להשתמש גם בו, או רק Storj?
5. **תקציב** - יש מגבלות על שימוש ב-Storj?

---

**הערה:** תוכנית זו היא נקודת התחלה. ניתן להרחיב או לצמצם לפי הצורך.

---

*נוצר על ידי GitHub Copilot עבור פרויקט Nervesys*
