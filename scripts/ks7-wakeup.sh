#!/bin/bash
# ks7 AI Wakeup — מושך זיכרון מ-GitHub בהפעלה

NERVESYS_DIR="/opt/ks7/nervesys"
GITHUB_REPO="git@github.com:bitonpro/nervesys.git"
SSH_KEY="/opt/ks7/claude-memory/ssh/ripo_ed25519"
LOG="/var/log/ks7-wakeup.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "[$TIMESTAMP] wakeup on $(hostname)" >> "$LOG"

export GIT_SSH_COMMAND="ssh -i $SSH_KEY -o StrictHostKeyChecking=no -o BatchMode=yes"

if [ -d "$NERVESYS_DIR/.git" ]; then
  git -C "$NERVESYS_DIR" pull --quiet 2>> "$LOG"
else
  mkdir -p "$NERVESYS_DIR"
  git clone "$GITHUB_REPO" "$NERVESYS_DIR" --quiet 2>> "$LOG"
fi

# סנכרן CLAUDE.md לנתיב הסטנדרטי
[ -f "$NERVESYS_DIR/memory/rules/CLAUDE.md" ] && \
  cp "$NERVESYS_DIR/memory/rules/CLAUDE.md" ~/CLAUDE.md

echo "[$TIMESTAMP] done" >> "$LOG"
