import os
import subprocess
import logging

# ==============================
# LOG CONFIGURATION
# ==============================
log_file_path = "/folder-location/mongodb_restore.log"
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==============================
# MONGODB CONFIG
# ==============================
# NOTE:
# Replace placeholders before use
MONGO_HOST = "your-mongo-host"
MONGO_PORT = "27017"
MONGO_USER = "<USERNAME>"
MONGO_PASS = "<PASSWORD>"

# Backup folder
BACKUP_FOLDER = "/folder-location/db-backup"


# ==============================
# RESTORE FUNCTION
# ==============================
def restore_backup(backup_file):
    # Extract DB name from filename
    db_name = backup_file.split("_")[0]
    backup_path = os.path.join(BACKUP_FOLDER, backup_file)

    # MongoDB connection URI
    uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{db_name}?authSource=admin"

    command = [
        "mongorestore",
        "--uri", uri,
        "--gzip",
        "--archive=" + backup_path,
        "--drop"  # overwrite existing data
    ]

    logging.info(f"Starting restore for {db_name}")

    try:
        subprocess.run(command, check=True)
        logging.info(f"Restore completed for {db_name}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Restore failed for {db_name}: {e}")


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    for filename in os.listdir(BACKUP_FOLDER):
        if filename.endswith(".gz"):
            restore_backup(filename)
