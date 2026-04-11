import os
import subprocess
import datetime
import logging
from threading import Lock

# ==============================
# LOG CONFIGURATION
# ==============================
log_file_path = "/folder-location/mongodb_backup.log"
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==============================
# DATABASE CONFIG
# ==============================
# NOTE:
# - Replace <USERNAME>, <PASSWORD>, <CLUSTER_URL>
# - Do NOT commit real credentials to git
database_configs = [
    {
        'name': 'your-database-name',
        'uri': 'mongodb+srv://<USERNAME>:<PASSWORD>@<CLUSTER_URL>/your-database-name',
        'backup_folder': '/folder-location/db-backup',
        'retention_days': 3
    },
]

backup_lock = Lock()


# ==============================
# DELETE OLD BACKUPS
# ==============================
def delete_old_backups(db_config):
    retention_hours = db_config['retention_days'] * 24
    backup_folder = db_config['backup_folder']
    current_time = datetime.datetime.now()

    for filename in os.listdir(backup_folder):
        if filename.startswith(db_config['name']):
            file_path = os.path.join(backup_folder, filename)

            file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            file_age_hours = (current_time - file_mtime).total_seconds() / 3600

            if file_age_hours >= retention_hours:
                try:
                    os.remove(file_path)
                    logging.info(f"Deleted old backup: {file_path}")
                except Exception as e:
                    logging.error(f"Failed to delete {file_path}: {e}")


# ==============================
# CREATE BACKUP
# ==============================
def create_backup(db_config):
    with backup_lock:
        os.makedirs(db_config['backup_folder'], exist_ok=True)

        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        backup_filename = f"{db_config['name']}_{date_str}.gz"
        backup_filepath = os.path.join(db_config['backup_folder'], backup_filename)

        command = [
            'mongodump',
            '--uri', db_config['uri'],
            '--gzip',
            '--archive=' + backup_filepath
        ]

        logging.info(f"Starting backup for {db_config['name']}")

        try:
            subprocess.run(command, check=True)
            logging.info(f"Backup completed: {backup_filepath}")

            delete_old_backups(db_config)

        except subprocess.CalledProcessError as e:
            logging.error(f"Backup failed: {e}")

            if os.path.exists(backup_filepath):
                os.remove(backup_filepath)
                logging.info("Removed incomplete backup file")


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    for db_config in database_configs:
        create_backup(db_config)
