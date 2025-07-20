import os
import json
import hashlib
from config import CHUNK_SIZE, CHUNK_DIR, RECONSTRUCTED_DIR, FILENAME_PREFIX, HASH_ALGO, NODES

def verify_hash(data, expected_hash):
    h = hashlib.new(HASH_ALGO)
    h.update(data)
    return h.hexdigest() == expected_hash

def try_read_valid_chunk(paths, expected_hash):
    first = True
    for path in paths:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = f.read()
                if verify_hash(data, expected_hash):
                    if not first:
                        print(f"[INFO-LOG] Fallback chunk used: {path}, hash verified. Primary chunk may have been corrupted or missing.")
                    return data
                else:
                    print(f"[ERROR-LOG] Chunk at {path} does not match expected hash. Skipping...")
        first = False
    return None

def reconstruct_file(metadata_path):
    try:
        # Load metadata
        with open(metadata_path, 'r') as meta_file:
            meta_data = json.load(meta_file)

        if not meta_data:
            print("[ERROR-LOG] No metadata found to reconstruct the file.")
            return
    
        original_file_name = os.path.splitext(os.path.basename(metadata_path))[0].replace('_metadata', '')
        reconstructed_path = os.path.join(RECONSTRUCTED_DIR, f"{original_file_name}_reconstructed.bin")

        with open(reconstructed_path, 'wb') as reconstructed_file:
            for chunk_info in sorted(meta_data, key=lambda x: x['chunk_index']):
                chunk_hash = chunk_info['chunk_hash']
                chunk_relative_path = chunk_info['relative_path']
                chunk_filename = chunk_info['chunk_filename']
                chunk_abs_path = os.path.join(CHUNK_DIR, chunk_relative_path)

                paths_to_try = [os.path.join(CHUNK_DIR, chunk_info['relative_path'])]
                for replica_rel in chunk_info.get('replicas', []):
                    paths_to_try.append(os.path.join(replica_rel['replica_path']))

                chunk_data = try_read_valid_chunk(paths_to_try, chunk_hash)
                if chunk_data is None:
                    print(f"[ERROR-LOG] Chunk {chunk_filename} with hash {chunk_hash} could not be found or is corrupted. Skipping...")
                    continue
                else:
                    reconstructed_file.write(chunk_data)

        print(f"[INFO-LOG] Reconstructed file saved to {reconstructed_path} successfully.")

    except Exception as e:
        print(f"[ERROR-LOG] An error occurred during file reconstruction: {e}")
        raise e

# Example usage
reconstruct_file(os.path.join(CHUNK_DIR, 'testing_metadata.json'))