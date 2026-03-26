import os
import time
import csv
import shutil
import requests
import subprocess
from datetime import datetime

# --- АБСОЛЮТНЫЕ ПУТИ ---
BASE_DIR = "/Users/artiom/Desktop/bunker-opa/Community/Signals_Potentially_Anomaly/metadata"
LOG_FILE = os.path.join(BASE_DIR, "network_audit.csv")
# Путь к speedtest-cli (проверь: which speedtest-cli)
SPEEDTEST_PATH = "/Users/artiom/.local/share/mamba/envs/de/bin/speedtest-cli"

# Получаем токен из системы
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_TOKEN_Opa = os.getenv('GITHUB_TOKEN_Opa')

# Проверка (на случай, если переменная не подгрузилась)
if not GITHUB_TOKEN:
    print("Ошибка: GITHUB_TOKEN не найден в переменных окружения")

INTERVAL = 900 
REPOS = [
    "skovnats/SVE-Systemic-Verification-Engineering",
    "Opa-Collective/bunker",
    "skovnats/bunker"
]
HEADERS = [
    "Timestamp", "Ping_Google", "Ping_GitHub", "Free_Disk_GB", "External_IP", "Speed_Stats",
    "SVE_Date", "SVE_Msg", "SVE_URL",
    "Bunker_Opa_Date", "Bunker_Opa_Msg", "Bunker_Opa_URL",
    "Bunker_Skov_Date", "Bunker_Skov_Msg", "Bunker_Skov_URL"
]

def get_audit_data():
    # 1. Ping
    p_google = "UP" if os.system("ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1") == 0 else "DOWN"
    p_github = "UP" if os.system("ping -c 1 -W 2 github.com > /dev/null 2>&1") == 0 else "DOWN"
    
    # 2. Disk
    _, _, free = shutil.disk_usage("/")
    disk_gb = round(free / (1024**3), 2)
    
    # 3. Network
    headers = {'User-Agent': 'SVE-Auditor-Agent-v2.4', 'Authorization': f'token {GITHUB_TOKEN}'}
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
    except:
        ip = "CONN_ERR"
        
    try:
        speed = subprocess.check_output([SPEEDTEST_PATH, "--simple"], timeout=60).decode("utf-8").replace("\n", " | ")
    except:
        speed = "SPEED_ERR"
        
    # 4. GitHub
    commits_info = []
    for repo in REPOS:
        current_token = GITHUB_TOKEN_Opa if "Opa-Collective" in repo else GITHUB_TOKEN
        headers = {'User-Agent': 'SVE-Auditor-Agent-v2.4', 'Authorization': f'token {current_token}'}
        
        try:
            r = requests.get(f"https://api.github.com/repos/{repo}/commits?per_page=1", timeout=10, headers=headers)
            if r.status_code == 200:
                data = r.json()[0]
                date = data['commit']['committer']['date']
                # Очищаем сообщение от переносов строк, чтобы не ломать структуру CSV
                msg = data['commit']['message'].replace('\n', ' ').replace('\r', '')
                url = data['html_url']
                commits_info.extend([date, msg, url])
            else:
                commits_info.extend([f"HTTP_{r.status_code}", "N/A", "N/A"])
        except:
            commits_info.extend(["TIMEOUT", "N/A", "N/A"])
            
    return [p_google, p_github, disk_gb, ip, speed] + commits_info

while True:
    try:
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', newline='') as f:
                csv.writer(f).writerow(HEADERS)

        row = get_audit_data()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(LOG_FILE, 'a', newline='') as f:
            csv.writer(f).writerow([now] + row)
        
        print(f"[{now}] Logged. Waiting 15m...")
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(INTERVAL)