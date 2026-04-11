# Mongo Backup Automation

## 📦 Overview

This repository contains simple Python scripts to: - Backup MongoDB
databases using `mongodump` - Restore MongoDB backups using
`mongorestore`

------------------------------------------------------------------------

## 📁 Structure

    mongo-backup-automation/
    ├── backup_mongodb.py
    ├── restore_mongodb.py
    └── README.md

------------------------------------------------------------------------

## ⚙️ Requirements

Install the following on your server:

### 1. Python

``` bash
sudo apt update
sudo apt install -y python3
```

### 2. MongoDB Database Tools

``` bash
sudo apt install -y mongodb-database-tools
```

Check:

``` bash
mongodump --version
mongorestore --version
```

------------------------------------------------------------------------

## 📂 Required Directories

Create required folders:

``` bash
sudo mkdir -p /folder-location/db-backup
sudo mkdir -p /folder-location
sudo chown -R $USER:$USER /mongo-data
```

------------------------------------------------------------------------

## 🚀 Backup Script

### Run manually:

``` bash
python3 backup_mongodb.py
```

### What it does:

-   Takes MongoDB backup
-   Stores as `.gz`
-   Deletes old backups (based on retention)

------------------------------------------------------------------------

## ♻️ Restore Script

### Run manually:

``` bash
python3 restore_mongodb.py
```

### What it does:

-   Reads `.gz` backup files
-   Restores them into MongoDB
-   Overwrites existing data (`--drop`)

------------------------------------------------------------------------

## ⏰ Automate with Cron (Optional)

Edit crontab:

``` bash
crontab -e
```

Run backup daily at 2 AM:

``` bash
0 2 * * * /usr/bin/python3 /path/to/backup_mongodb.py
```

------------------------------------------------------------------------

## ⚠️ Notes

-   Make sure MongoDB server is accessible
-   Ensure proper permissions for backup folder
-   Keep credentials secure (avoid committing sensitive data)

------------------------------------------------------------------------

