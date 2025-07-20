import os
import hashlib
from config import CHUNK_SIZE, CHUNK_DIR, RECONSTRUCTED_DIR, FILENAME_PREFIX, HASH_ALGO, NODES, REPLICATION_FACTOR
from utils import select_random_replicas

def hash_chunk(data):
    h = hashlib.new(HASH_ALGO)
    h.update(data)
    return h.hexdigest()

def chunk_file(file_path, chunk_size=CHUNK_SIZE):
    file_name = os.path.basename(file_path)
    name_wo_ext = os.path.splitext(file_name)[0]

    print(f"[INFO-LOG] Chunking {file_name} into {chunk_size} byte chunks...")

    meta_data = []

    try:
        with open(file_path, 'rb') as f:
            chunk_index = 0
            while True:
                # Creating/Opening node specific directories
                primary_node =  NODES[chunk_index % len(NODES)] # Could chose primary node based on distance from the source or other criteria...
                output_dir = os.path.join(CHUNK_DIR, primary_node, name_wo_ext)  # TODO: Add node-specific directories
                os.makedirs(output_dir, exist_ok=True)
                
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                chunk_hash = hash_chunk(chunk)
                chunk_filename = f"{FILENAME_PREFIX}{chunk_index:04d}.bin"
                chunk_path = os.path.join(output_dir, chunk_filename)   # TODO: Make other logics on how the data is distributed across nodes.
                relative_path = os.path.relpath(chunk_path, CHUNK_DIR)

                # Writing the chunk to the primary node...
                with open(chunk_path, 'wb') as chunk_file:
                    chunk_file.write(chunk)

                # Replicating the chunk to other nodes
                replicas = []
                replicas_nodes = select_random_replicas(NODES, primary_node, REPLICATION_FACTOR)
                for replica_node in replicas_nodes:
                    replica_dir = os.path.join(CHUNK_DIR, replica_node, f'{name_wo_ext}_replica')
                    os.makedirs(replica_dir, exist_ok=True)
                    replica_path = os.path.join(replica_dir, chunk_filename)

                    with open(replica_path, 'wb') as replica_file:
                        replica_file.write(chunk)

                    replicas.append({
                        "node": replica_node,
                        "replica_path": replica_path,
                    })

                # Adding metadata for the chunk
                meta_data.append({
                    "chunk_index": chunk_index,
                    "chunk_filename": chunk_filename,
                    "relative_path": relative_path,
                    "chunk_path": chunk_path,
                    "node": NODES[chunk_index % len(NODES)],
                    "chunk_size": len(chunk),
                    "chunk_hash": chunk_hash,
                    "replicas": replicas,
                })      # TODO: Add timestamp and other metadata for better tracking and future scaling and versioning. Could also add node id for distributed systems.

                print(f"[INFO-LOG] Created chunk: {chunk_filename} with hash: {chunk_hash}")

                chunk_index += 1
        
        metadata_path = os.path.join(CHUNK_DIR, f'{name_wo_ext}_metadata.json')
        with open(metadata_path, 'w') as meta_file:
            import json
            json.dump(meta_data, meta_file, indent=4)

        print(f"[INFO-LOG] Metadata saved to {metadata_path} successfully...")

    except Exception as e:
        print(f"[ERROR-LOG] An error occurred while chunking the file: {e}")
        raise e


chunk_file('sample_files/testing.txt')  # Example usage, replace with actual file path

