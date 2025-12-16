import os
import sys
import time
import subprocess
import logging
import logging.handlers

# --- GENESIS CONFIGURATION ---
PORT = 8080
SERVICE = "nervesys-webhook"
REPO_DIR = "/opt/nervesys"
LOG_FILE = "/var/log/genesis_watchdog.log"

# --- LOGGER SETUP ---
logger = logging.getLogger("Genesis")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().strip()
    except:
        return None

def kill_zombies():
    zombies = run("ps -A -o stat,pid,ppid | grep -e '^[Zz]'")
    if zombies:
        logger.warning(f"Zombies detected. Purging...")
        # הרג אגרסיבי של תהליכי Node תקועים
        run("pkill -9 -f 'node /opt/nervesys'")
        run(f"fuser -k {PORT}/tcp")

def fix_git():
    # תיקון הבעיה הספציפית שלך עם חסימת הריפו
    run(f"git config --global --add safe.directory {REPO_DIR}")

def check_pulse():
    # בדיקת HTTP פשוטה
    status = run(f"curl -s -o /dev/null -w '%{{http_code}}' http://127.0.0.1:{PORT}/health")
    return status == "200"

def main():
    logger.info(">>> GENESIS WATCHDOG ACTIVE <<<")
    
    while True:
        # 1. שחרית (בדיקה)
        alive = check_pulse()
        
        # 2. מנחה (תיקון)
        if not alive:
            logger.error("Pulse lost! Initiating Protocol...")
            kill_zombies()
            fix_git()
            
            # 3. ערבית (החייאה)
            logger.info("Restarting Service...")
            run(f"systemctl restart {SERVICE}")
            time.sleep(5)
            
            if check_pulse():
                logger.info("✅ System Resurrected.")
            else:
                logger.critical("❌ Resurrection Failed.")
        
        # 4. תיקון חצות (דופק קבוע)
        time.sleep(10)

if __name__ == "__main__":
    main()
