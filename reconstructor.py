import os
import json
import hashlib
from config import CHUNK_SIZE, CHUNK_DIR, RECONSTRUCTED_DIR, FILENAME_PREFIX, HASH_ALGO, NODES

def verify_hash(data, expected_hash):
    h = hashlib.new(HASH_ALGO)
    h.update(data)
    return h.hexdigest() == expected_hash

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

                chunk_abs_path = os.path.join(CHUNK_DIR, chunk_relative_path)

                if not os.path.exists(chunk_abs_path):
                    print(f"[ERROR-LOG] Chunk file {chunk_abs_path} does not exist. Skipping...")
                    continue

                with open(chunk_abs_path, 'rb') as chunk_file:
                    chunk_data = chunk_file.read()
                    if verify_hash(chunk_data, chunk_hash):
                        reconstructed_file.write(chunk_data)
                        print(f"[INFO-LOG] Successfully added chunk {chunk_info['chunk_filename']} to the reconstructed file.")
                    else:
                        print(f"[ERROR-LOG] Hash mismatch for chunk {chunk_info['chunk_filename']}. Skipping...")
            
        print(f"[INFO-LOG] Reconstructed file saved to {reconstructed_path} successfully.")

    except Exception as e:
        print(f"[ERROR-LOG] An error occurred during file reconstruction: {e}")
        raise e

# # Example usage
# reconstruct_file(os.path.join(CHUNK_DIR, 'testing_metadata.json'))