import time
import logging
import psutil
import requests
import os
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler

# Set up logging
LOG_DIR = "/opt/server-monitor-logs"  # Log directory
LOG_BASE = os.path.join(LOG_DIR, "server_monitor")
os.makedirs(LOG_DIR, exist_ok=True)  # Create log directory if it doesn't exist

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Ensure logs use UTC timestamps
logging.Formatter.converter = time.gmtime

# Create TimedRotatingFileHandler for daily logs with 7-day retention
handler = TimedRotatingFileHandler(
    LOG_BASE,
    when="midnight",
    interval=1,
    backupCount=7,  # Keep 7 days of logs
    encoding="utf-8"
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
handler.suffix = "-%Y-%m-%d.log.txt"  # Combined suffix for date + .log.txt
logger.addHandler(handler)

# Define threshold values
CPU_THRESHOLD = 70.0  # Low for testing; consider 65.0 for production
RAM_THRESHOLD = 80.0  # Low for testing; consider 80.0 for production
STORAGE_THRESHOLD = 70.0  # Low for testing; consider 70.0 for production
CHECK_INTERVAL = 60  # Short for testing; consider 60 for production
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"  # Replace with your Discord webhook URL
SERVER_NAME = "My Server"  # Customize with your server name
DATA_MOUNT_POINT = "/data"  # Customize with your mounted data volume path (e.g., '/mnt/storage')

if not DISCORD_WEBHOOK_URL or DISCORD_WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_URL":
    logging.error("DISCORD_WEBHOOK_URL is not set. Exiting.")
    exit(1)

# State tracking to avoid spamming notifications
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
    # Define colors for different resources
    colors = {
        'CPU': 0xFF0000,  # Red
        'RAM': 0xFFA500,  # Orange
        'Root Storage': 0xFFFF00,  # Yellow
        'Data Storage': 0xFFFF00  # Yellow
    }
    resource_name = resource.replace('_', ' ').title()
    
    # Create payload for resource alert
    total_str = f"{total} cores" if resource == 'cpu' else f"{total:.2f} GB"
    used_str = f"{usage:.1f}% of {total} cores" if resource == 'cpu' else f"{used:.2f} GB"
    payload = {
        "embeds": [{
            "title": f"⚠️ {resource_name} Alert on {SERVER_NAME}",
            "description": f"{resource_name} usage has exceeded {threshold}%!",
            "color": colors.get(resource_name, 0xFF0000),
            "fields": [
                {"name": "Current Usage", "value": f"{usage:.1f}%", "inline": True},
                {"name": "Threshold", "value": f"{threshold:.1f}%", "inline": True},
                {"name": "Used", "value": used_str, "inline": True},
                {"name": "Total", "value": total_str, "inline": True}
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "footer": {"text": "Server Monitor"}
        }]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        logging.info(f"Notification sent for {resource_name}: {usage:.1f}% (Used: {used_str}, Total: {total_str})")
    except requests.RequestException as e:
        logging.error(f"Failed to send notification for {resource_name}: {e}")

def check_resources():
    try:
        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_total = psutil.cpu_count(logical=True)
        if cpu_usage > CPU_THRESHOLD and not alert_states['cpu']:
            send_discord_notification("cpu", cpu_usage, CPU_THRESHOLD, cpu_total, cpu_usage)
            alert_states['cpu'] = True
        elif cpu_usage <= CPU_THRESHOLD and alert_states['cpu']:
            alert_states['cpu'] = False

        # RAM usage
        ram_info = psutil.virtual_memory()
        ram_usage = ram_info.percent
        ram_total = bytes_to_gb(ram_info.total)
        ram_used = bytes_to_gb(ram_info.used)
        if ram_usage > RAM_THRESHOLD and not alert_states['ram']:
            send_discord_notification("ram", ram_usage, RAM_THRESHOLD, ram_total, ram_used)
            alert_states['ram'] = True
        elif ram_usage <= RAM_THRESHOLD and alert_states['ram']:
            alert_states['ram'] = False

        # Root storage usage
        root_info = psutil.disk_usage('/')
        root_usage = root_info.percent
        root_total = bytes_to_gb(root_info.total)
        root_used = bytes_to_gb(root_info.used)
        if root_usage > STORAGE_THRESHOLD and not alert_states['root_storage']:
            send_discord_notification("root_storage", root_usage, STORAGE_THRESHOLD, root_total, root_used)
            alert_states['root_storage'] = True
        elif root_usage <= STORAGE_THRESHOLD and alert_states['root_storage']:
            alert_states['root_storage'] = False

        # Data storage usage (using configurable mount point)
        try:
            data_info = psutil.disk_usage(DATA_MOUNT_POINT)
            data_usage = data_info.percent
            data_total = bytes_to_gb(data_info.total)
            data_used = bytes_to_gb(data_info.used)
            if data_usage > STORAGE_THRESHOLD and not alert_states['data_storage']:
                send_discord_notification("data_storage", data_usage, STORAGE_THRESHOLD, data_total, data_used)
                alert_states['data_storage'] = True
            elif data_usage <= STORAGE_THRESHOLD and alert_states['data_storage']:
                alert_states['data_storage'] = False
        except FileNotFoundError:
            data_usage = data_total = data_used = None
            logging.warning(f"Disk {DATA_MOUNT_POINT} not found, skipping.")

        # Log all metrics in a formatted way
        logging.info(
            f"Metrics | CPU: {cpu_usage:.1f}% of {cpu_total} cores | "
            f"RAM: {ram_usage:.1f}% ({ram_used:.2f}/{ram_total:.2f} GB) | "
            f"Root Storage: {root_usage:.1f}% ({root_used:.2f}/{root_total:.2f} GB) | "
            f"Data Storage ({DATA_MOUNT_POINT}): {'N/A' if data_usage is None else f'{data_usage:.1f}% ({data_used:.2f}/{data_total:.2f} GB)'}"
        )
    except Exception as e:
        logging.error(f"Error checking resources: {e}")

while True:
    check_resources()
    time.sleep(CHECK_INTERVAL)