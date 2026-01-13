"""
Compress Files/ directory into optimized zip archives for smaller EXE size.
Run this before building the executable.
"""

import os
import zipfile
import shutil

FILES_DIR = "Files"
COMPRESSED_DIR = "FilesCompressed"

# Group files by usage pattern for optimal extraction
FILE_GROUPS = {
    "core": [
        "EmptyStandbyList.exe",
        "nssm.exe", 
        "SetTimerResolutionService.exe",
    ],
    "nvidia": [
        "nvidiaProfileInspector.exe",
        "Base_Profile.nip",
        "meoboost.nip",
    ],
    "audio": [
        "REAL.exe",
    ],
    "display": [
        "dccmd.exe",
        "libiconv2.dll",
        "libintl3.dll",
        "regex2.dll",
    ],
    "power": [
        "meoboost.pow",
    ],
    "misc": [
        "NSudo.exe",
        "restart64.exe",
        "sed.exe",
        "meoboost.usf",
        "Driverinstall.bat",
        "version.txt",
    ],
    "ddu": [
        "DDU.zip",  # Already compressed
    ],
}


def compress_files():
    """Compress Files/ into grouped zip archives."""
    
    # Create output directory
    if os.path.exists(COMPRESSED_DIR):
        shutil.rmtree(COMPRESSED_DIR)
    os.makedirs(COMPRESSED_DIR)
    
    total_original = 0
    total_compressed = 0
    
    for group_name, files in FILE_GROUPS.items():
        zip_path = os.path.join(COMPRESSED_DIR, f"{group_name}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for filename in files:
                file_path = os.path.join(FILES_DIR, filename)
                if os.path.exists(file_path):
                    original_size = os.path.getsize(file_path)
                    total_original += original_size
                    zf.write(file_path, filename)
                    print(f"  Added: {filename} ({original_size:,} bytes)")
                else:
                    print(f"  [SKIP] {filename} not found")
        
        compressed_size = os.path.getsize(zip_path)
        total_compressed += compressed_size
        ratio = (1 - compressed_size / max(1, sum(
            os.path.getsize(os.path.join(FILES_DIR, f)) 
            for f in files if os.path.exists(os.path.join(FILES_DIR, f))
        ))) * 100
        print(f"Created: {group_name}.zip ({compressed_size:,} bytes, {ratio:.1f}% smaller)")
        print()
    
    # Copy directories (Aesthetics, FPS, GpuTest, Vibrant)
    for dirname in ["Aesthetics", "FPS", "GpuTest", "Vibrant"]:
        src_dir = os.path.join(FILES_DIR, dirname)
        if os.path.exists(src_dir):
            zip_path = os.path.join(COMPRESSED_DIR, f"{dirname.lower()}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
                for root, dirs, files in os.walk(src_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, FILES_DIR)
                        original_size = os.path.getsize(file_path)
                        total_original += original_size
                        zf.write(file_path, arcname)
            
            compressed_size = os.path.getsize(zip_path)
            total_compressed += compressed_size
            print(f"Created: {dirname.lower()}.zip ({compressed_size:,} bytes)")
    
    print()
    print("=" * 50)
    print(f"Original total:   {total_original:,} bytes ({total_original/1024/1024:.2f} MB)")
    print(f"Compressed total: {total_compressed:,} bytes ({total_compressed/1024/1024:.2f} MB)")
    print(f"Reduction:        {(1 - total_compressed/total_original)*100:.1f}%")
    print("=" * 50)


if __name__ == "__main__":
    print("Compressing Files/ directory...")
    print()
    compress_files()
    print()
    print("Done! Use FilesCompressed/ for building.")
