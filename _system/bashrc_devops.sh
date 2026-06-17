#!/usr/bin/env bash
# DevOps 대시보드 ~/.bashrc 설정 백업
# 재설치 후 복구: cat bashrc_devops.sh >> ~/.bashrc

# DevOps 대시보드 aliases
alias dash='python3 /home/jsy/devops-portfolio/_system/dashboard.py'
alias cl='python3 /home/jsy/devops-portfolio/_system/dashboard.py checklist'
alias jobcheck='python3 /home/jsy/devops-portfolio/_system/job_watch.py'
unalias done 2>/dev/null
alias check='python3 /home/jsy/devops-portfolio/_system/done.py'
alias night='python3 /home/jsy/devops-portfolio/_system/auto_night.py'

# AI 제안 응답 명령어
accept()  { python3 /home/jsy/devops-portfolio/_system/suggest_cmd.py accept "$@"; }
decline() { python3 /home/jsy/devops-portfolio/_system/suggest_cmd.py decline "$@"; }
uncheck() { python3 /home/jsy/devops-portfolio/_system/done.py --undo "$@"; }

# 강제 재실행 단축어
rerun() {
    echo "[rerun] 웹 수집 + AI 분析 강제 재실행..."
    python3 /home/jsy/devops-portfolio/_system/web_intel.py --force
    python3 /home/jsy/devops-portfolio/_system/claude_morning.py --force
    python3 /home/jsy/devops-portfolio/_system/dashboard.py
}
reai() {
    echo "[reai] AI 분析만 강제 재실행..."
    python3 /home/jsy/devops-portfolio/_system/claude_morning.py --force
    python3 /home/jsy/devops-portfolio/_system/dashboard.py
}

# 터미널 열 때 자동으로 대시보드 표시 (로그인 셸에서만, 서브셸 제외)
if [[ $SHLVL -eq 1 ]] && [[ $- == *i* ]]; then
    python3 /home/jsy/devops-portfolio/_system/auto_day.py
    python3 /home/jsy/devops-portfolio/_system/web_intel.py
    python3 /home/jsy/devops-portfolio/_system/claude_morning.py
    python3 /home/jsy/devops-portfolio/_system/job_watch.py --silent
    python3 /home/jsy/devops-portfolio/_system/dashboard.py
fi
