import hashlib
import os
import json
import sys

# File where hashes will be stored
HASH_DB = "hashes.json"


# Function to calculate SHA256 hash of a file
def calculate_hash(file_path):
    sha256 = hashlib.sha256()

    try:
        with open(file_path, "rb") as file:
            while True:
                data = file.read(4096)
                if not data:
                    break
                sha256.update(data)

        return sha256.hexdigest()

    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None


# Function to get files from a directory or single file
def get_files(path):

    files = []

    if os.path.isfile(path):
        files.append(path)

    elif os.path.isdir(path):
        for root, dirs, filenames in os.walk(path):
            for name in filenames:
                files.append(os.path.join(root, name))

    return files


# Initialize hashes (first run)
def initialize(path):

    files = get_files(path)

    hashes = {}

    for file in files:
        file_hash = calculate_hash(file)

        if file_hash:
            hashes[file] = file_hash

    with open(HASH_DB, "w") as db:
        json.dump(hashes, db, indent=4)

    print("Hashes stored successfully.")


# Check file integrity
def check_integrity(path):

    if not os.path.exists(HASH_DB):
        print("No hash database found. Run init first.")
        return

    with open(HASH_DB, "r") as db:
        stored_hashes = json.load(db)

    files = get_files(path)

    for file in files:

        new_hash = calculate_hash(file)

        old_hash = stored_hashes.get(file)

        if old_hash is None:
            print(f"{file} → Status: Not monitored")

        elif new_hash == old_hash:
            print(f"{file} → Status: Unmodified")

        else:
            print(f"{file} → Status: Modified (Hash mismatch)")


# Update hash if file legitimately changed
def update_hash(path):

    if not os.path.exists(HASH_DB):
        print("No hash database found.")
        return

    with open(HASH_DB, "r") as db:
        hashes = json.load(db)

    files = get_files(path)

    for file in files:

        new_hash = calculate_hash(file)

        if new_hash:
            hashes[file] = new_hash

    with open(HASH_DB, "w") as db:
        json.dump(hashes, db, indent=4)

    print("Hash updated successfully.")


# Main command system
if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage:")
        print("python3 integrity_check.py init <path>")
        print("python3 integrity_check.py check <path>")
        print("python3 integrity_check.py update <path>")
        sys.exit()

    command = sys.argv[1]
    path = sys.argv[2]

    if command == "init":
        initialize(path)

    elif command == "check":
        check_integrity(path)

    elif command == "update":
        update_hash(path)

    else:
        print("Unknown command")
