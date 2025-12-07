import time
import logging
import psutil
import requests
import os
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler

# ========================= CONFIGURATION =========================
LOG_DIR = "/opt/server-monitor-logs"                    # Log directory
LOG_BASE = os.path.join(LOG_DIR, "server_monitor.log.txt")  # Current log file

CPU_THRESHOLD = 70.0          # % - adjust as needed
RAM_THRESHOLD = 85.0          # %
STORAGE_THRESHOLD = 70.0      # %
CHECK_INTERVAL = 60           # seconds
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"   # <<< CHANGE THIS!
SERVER_NAME = "My Server"                          # Change to your server name
DATA_MOUNT_POINT = "/data"                         # Your data volume mount point
# =================================================================

# Create log directory
os.makedirs(LOG_DIR, exist_ok=True)

# Validate webhook
if not DISCORD_WEBHOOK_URL or DISCORD_WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_URL":
    print("ERROR: DISCORD_WEBHOOK_URL is not set!")
    exit(1)

# Set up logging with proper daily rotation + 7-day retention
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.Formatter.converter = time.gmtime  # UTC timestamps

handler = TimedRotatingFileHandler(
    LOG_BASE,
    when="midnight",
    interval=1,
    backupCount=7,        # Keep only last 7 days
    encoding="utf-8"
)

# Fix filename format: server_monitor-2025-12-07.log.txt
def namer(default_name):
    # default_name example: /opt/server-monitor-logs/server_monitor.log.txt.2025-12-07
    base, _ = os.path.splitext(default_name)  # Remove the added .2025-12-07
    return base + ".log.txt"                   # → server_monitor-2025-12-07.log.txt

handler.namer = namer

handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
logger.addHandler(handler)

# State tracking to prevent notification spam
alert_states = {
    'cpu': False,
    'ram': False,
    'root_storage': False,
    'data_storage': False
}

def bytes_to_gb(bytes_value):
    """Convert bytes to GB with 2 decimal places."""
    return round(bytes_value / (1024 ** 3), 2)

def send_discord_notification(resource, usage=None, threshold=None, total=None, used=None):
    colors = {
        'CPU': 0xFF0000,           # Red
        'RAM': 0xFFA500,           # Orange
        'Root Storage': 0xFFFF00,  # Yellow
        'Data Storage': 0xFFFF00   # Yellow
    }
    resource_name = resource.replace('_', ' ').title()

    total_str = f"{total} cores" if resource == 'cpu' else f"{total:.2f} GB"
    used_str = f"{usage:.1f}% ({used:.2f} GB used)" if resource != 'cpu' else f"{usage:.1f}% of {total} cores"

    payload = {
        "embeds": [{
            "title": f"Warning: {resource_name} High Usage on {SERVER_NAME}",
            "description": f"{resource_name} usage has exceeded {threshold}%!",
            "color": colors.get(resource_name, 0xFF0000),
            "fields": [
                {"name": "Current Usage", "value": f"{usage:.1f}%", "inline": True},
                {"name": "Threshold", "value": f"{threshold:.1f}%", "inline": True},
                {"name": "Used", "value": used_str, "inline": True},
                {"name": "Total", "value": total_str, "inline": True}
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "footer": {"text": "Server Monitor • Powered by psutil"}
        }]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        logging.info(f"Discord alert sent → {resource_name}: {usage:.1f}%")
    except requests.RequestException as e:
        logging.error(f"Failed to send Discord alert for {resource_name}: {e}")

def check_resources():
    try:
        # CPU
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_total = psutil.cpu_count(logical=True)

        if cpu_usage > CPU_THRESHOLD and not alert_states['cpu']:
            send_discord_notification("cpu", cpu_usage, CPU_THRESHOLD, cpu_total, cpu_usage)
            alert_states['cpu'] = True
        elif cpu_usage <= CPU_THRESHOLD:
            alert_states['cpu'] = False

        # RAM
        ram = psutil.virtual_memory()
        ram_usage = ram.percent
        ram_total_gb = bytes_to_gb(ram.total)
        ram_used_gb = bytes_to_gb(ram.used)

        if ram_usage > RAM_THRESHOLD and not alert_states['ram']:
            send_discord_notification("ram", ram_usage, RAM_THRESHOLD, ram_total_gb, ram_used_gb)
            alert_states['ram'] = True
        elif ram_usage <= RAM_THRESHOLD:
            alert_states['ram'] = False

        # Root filesystem
        root = psutil.disk_usage('/')
        root_usage = root.percent
        root_total_gb = bytes_to_gb(root.total)
        root_used_gb = bytes_to_gb(root.used)

        if root_usage > STORAGE_THRESHOLD and not alert_states['root_storage']:
            send_discord_notification("root_storage", root_usage, STORAGE_THRESHOLD, root_total_gb, root_used_gb)
            alert_states['root_storage'] = True
        elif root_usage <= STORAGE_THRESHOLD:
            alert_states['root_storage'] = False

        # Data volume (optional)
        data_usage = data_total_gb = data_used_gb = None
        try:
            data = psutil.disk_usage(DATA_MOUNT_POINT)
            data_usage = data.percent
            data_total_gb = bytes_to_gb(data.total)
            data_used_gb = bytes_to_gb(data.used)

            if data_usage > STORAGE_THRESHOLD and not alert_states['data_storage']:
                send_discord_notification("data_storage", data_usage, STORAGE_THRESHOLD, data_total_gb, data_used_gb)
                alert_states['data_storage'] = True
            elif data_usage <= STORAGE_THRESHOLD:
                alert_states['data_storage'] = False
        except Exception as e:
            logging.warning(f"Could not read {DATA_MOUNT_POINT}: {e}")

        # Log current metrics
        logging.info(
            f"Metrics | CPU: {cpu_usage:.1f}% ({cpu_total} cores) | "
            f"RAM: {ram_usage:.1f}% ({ram_used_gb:.2f}/{ram_total_gb:.2f} GB) | "
            f"Root: {root_usage:.1f}% ({root_used_gb:.2f}/{root_total_gb:.2f} GB) | "
            f"Data ({DATA_MOUNT_POINT}): {'N/A' if data_usage is None else f'{data_usage:.1f}% ({data_used_gb:.2f}/{data_total_gb:.2f} GB)'}"
        )

    except Exception as e:
        logging.error(f"Error in check_resources(): {e}")

# ======================== MAIN LOOP ========================
if __name__ == "__main__":
    logging.info("Server Monitor started.")
    while True:
        check_resources()
        time.sleep(CHECK_INTERVAL)