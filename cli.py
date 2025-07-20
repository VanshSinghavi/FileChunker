import os
import glob
from chunker import chunk_file
from reconstructor import reconstruct_file
from config import CHUNK_DIR

def list_metadata_files():
    meta_files = glob.glob(os.path.join(CHUNK_DIR, "*_metadata.json"))
    return [os.path.basename(mf).replace("_metadata.json", "") for mf in meta_files]

def interactive_cli():
    while True:
        print("\n=== FileChunker CLI ===")
        print("1. Store a file (chunk)")
        print("2. Reconstruct a file")
        print("3. List metadata files")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            file_path = input("Enter full path to the file you want to store: ").strip()
            if not os.path.exists(file_path):
                print("[ERROR] File not found.")
            else:
                chunk_file(file_path)

        elif choice == "2":
            available = list_metadata_files()
            if not available:
                print("[INFO] No metadata files available for reconstruction.")
                continue

            print("Available files:")
            for i, name in enumerate(available):
                print(f"{i+1}. {name}")

            sel = input("Select file number to reconstruct: ").strip()
            try:
                sel_idx = int(sel) - 1
                if sel_idx < 0 or sel_idx >= len(available):
                    print("[ERROR] Invalid selection.")
                    continue

                file_name = available[sel_idx]
                metadata_path = os.path.join(CHUNK_DIR, f"{file_name}_metadata.json")
                reconstruct_file(metadata_path)
            except ValueError:
                print("[ERROR] Enter a valid number.")

        elif choice == "3":
            available = list_metadata_files()
            if not available:
                print("[INFO] No metadata files found.")
            else:
                print("Available metadata:")
                for name in available:
                    print(f"- {name}")

        elif choice == "4":
            print("Exiting.")
            break

        else:
            print("[ERROR] Invalid choice. Try again.")

if __name__ == "__main__":
    interactive_cli()
