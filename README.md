# nervesys — ks7 Flow AI Memory

זיכרון משותף לכל ה-AI instances בקלסטר ks7 Flow.

## כשאתה קם מחדש
```bash
/usr/local/bin/ks7-wakeup.sh
```

## מבנה
```
memory/
  rules/CLAUDE.md     ← Torah Core + כללים
  identity/           ← מי אנחנו
  cluster/servers.json ← כל השרתים
  learning/           ← זיכרון נרכש
scripts/
  ks7-wakeup.sh       ← סקריפט התעוררות
logs-forensics/       ← לוגים ופורנזיקס
```

## IVR Test Extensions
| Extension | Node |
|-----------|------|
| 9100 | cloudai (gama-2) |
| 9200 | storai |
| 9300 | arcai |
| 9400 | dgxsec |
| 9500 | 5060i |
