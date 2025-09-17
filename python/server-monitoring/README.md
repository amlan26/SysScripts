# 🚀 Server Monitor: Your Server's Guardian Angel 😇

Keep your server healthy and get instant alerts with this lightweight Python script. **Server Monitor** continuously watches your server's vitals (CPU, RAM, and storage) and sends real-time notifications to a Discord webhook when usage exceeds your set thresholds.  

No more guessing—just **peace of mind**. ✨

---

## ✨ Features
- 🖥️ **Monitors Key Resources**: CPU, RAM, and storage usage, including a custom data mount point.  
- 🔔 **Instant Discord Alerts**: Get notified in a dedicated Discord channel the moment a resource hits a critical level.  
- 📉 **Threshold-Based Alerts**: Say goodbye to notification spam! Alerts are only sent when thresholds are breached.  
- 📝 **Detailed Logging**: Metrics logged daily with a 7-day retention for performance tracking.  
- ⚙️ **Systemd Service**: Runs reliably in the background with `systemd`.  
- 🎛️ **Highly Customizable**: Adjust thresholds, intervals, and paths with ease.  

---

## 📋 Prerequisites
- **OS**: Linux (tested on Ubuntu 22.04)  
- **Python**: 3.6+  
- **Dependencies**:  
  - `psutil` – Collect system metrics  
  - `requests` – Send Discord notifications  
- **Discord Webhook**: A webhook URL from your Discord server  
- **Root Access**: Required for setting up the `systemd` service  

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/server-monitor.git
cd server-monitor
```

### 2. Set Up the Environment
Create a virtual environment and install dependencies:
```bash
python3 -m venv /opt/venv
source /opt/venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure the Script
Open `src/server_monitor.py` and update:

```python
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/your-webhook-id/your-webhook-token"
SERVER_NAME = "Production Server"
DATA_MOUNT_POINT = "/mnt/storage"
```

You can also adjust:
- `CPU_THRESHOLD`
- `RAM_THRESHOLD`
- `STORAGE_THRESHOLD`
- `CHECK_INTERVAL`

### 4. Finalize Installation
Create a log directory and copy the script:
```bash
sudo mkdir -p /opt/server-monitor-logs
sudo chown -R ubuntu:ubuntu /opt/server-monitor-logs
sudo cp src/server_monitor.py /opt/server-monitor-logs/
```

### 5. Set Up the Systemd Service
Copy the service file:
```bash
sudo cp systemd/server-monitor.service /etc/systemd/system/
```

Reload systemd and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable server-monitor.service
sudo systemctl start server-monitor.service
```

Check status:
```bash
sudo systemctl status server-monitor.service
```

---

## 🛠️ How It Works
1. **Checks Vitals**: Collects CPU, RAM, and storage metrics using `psutil`.  
2. **Compares Thresholds**: Evaluates usage against your defined limits.  
3. **Sends Alerts**: Discord notifications are sent once per breach until usage returns to normal.  
4. **Logs Everything**: Daily rotating logs with 7-day retention.  

---

## 📂 Project Structure
```
server-monitor/
├── src/
│   └── server_monitor.py       # The main monitoring script
├── systemd/
│   └── server-monitor.service  # Systemd service configuration
├── requirements.txt            # Python dependencies
└── README.md                  # You are here! 👋
```

---

## 📜 Logs and Troubleshooting
- **Metrics Logs**: `/opt/server-monitor-logs/server_monitor-YYYY-MM-DD.log.txt`  
- **Service Logs**:  
  - `/opt/server-monitor-logs/service.log`  
  - `/opt/server-monitor-logs/service_error.log`  

Logs rotate daily and are cleaned up after 7 days.  

**Common Issues**:
- ❌ *Service Not Starting*: Check `sudo systemctl status server-monitor.service` and logs.  
- ❌ *No Discord Notifications*: Ensure webhook URL is valid and server has internet access.  
- ❌ *Invalid Data Path*: Verify `DATA_MOUNT_POINT` exists.  

---

## 📄 License & Contributing
This project is licensed under the **MIT License**.  

Contributions are welcome—open an issue or PR if you’d like to improve it.  

Built with 💻 by server admins, for server admins who want peace of mind!  
