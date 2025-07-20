import json
import os

# Load config only once
with open('config.json') as f:
    config = json.load(f)

# Accessor for config variables (so that I can just say from config import CHUNK_SIZE, etc.)
CHUNK_SIZE = config.get("chunk_size", 1024)
CHUNK_DIR = config.get("chunk_dir", "chunks")
RECONSTRUCTED_DIR = config.get("reconstructed_dir", "reconstructed")
FILENAME_PREFIX = config.get("filename_prefix", "chunk_")
HASH_ALGO = config.get("hash_algorithm", "sha256")
REPLICATION_FACTOR = config.get("replication_factor", 2)

os.makedirs(CHUNK_DIR, exist_ok=True)
os.makedirs(RECONSTRUCTED_DIR, exist_ok=True)

# Create directories for each node if using distributed storage

NODES = config.get("nodes", [])
for node in NODES:
    os.makedirs(os.path.join(CHUNK_DIR, node), exist_ok=True)