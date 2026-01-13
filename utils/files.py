"""
File utilities with on-demand extraction from compressed archives.
Extracts files quickly when needed to minimize EXE size.
"""

import os
import zipfile
import tempfile
import shutil
from config import FILES_DIR, DATA_DIR

# Cache directory for extracted files
CACHE_DIR = os.path.join(DATA_DIR, "cache")

# Compressed files directory (used when running from EXE)
COMPRESSED_DIR = os.path.join(os.path.dirname(FILES_DIR), "FilesCompressed")


def _ensure_cache_dir():
    """Create cache directory if it doesn't exist."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)


def _find_in_zip(filename):
    """Find which zip archive contains the file."""
    
    # Check compressed directory
    compressed_dir = COMPRESSED_DIR
    if not os.path.exists(compressed_dir):
        # Fallback to same directory as FILES_DIR
        compressed_dir = os.path.join(os.path.dirname(FILES_DIR), "FilesCompressed")
    
    if not os.path.exists(compressed_dir):
        return None, None
    
    for zip_name in os.listdir(compressed_dir):
        if not zip_name.endswith('.zip'):
            continue
        
        zip_path = os.path.join(compressed_dir, zip_name)
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                names = zf.namelist()
                # Check direct match
                if filename in names:
                    return zip_path, filename
                # Check in subdirectories
                for name in names:
                    if name.endswith('/' + filename) or name == filename:
                        return zip_path, name
        except:
            continue
    
    return None, None


def _extract_file(zip_path, arcname, target_path):
    """Extract a single file from zip archive."""
    _ensure_cache_dir()
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Extract to cache directory
            extracted_path = zf.extract(arcname, CACHE_DIR)
            
            # Move to target location if different
            if extracted_path != target_path:
                target_dir = os.path.dirname(target_path)
                if target_dir and not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
                if os.path.exists(target_path):
                    os.remove(target_path)
                shutil.move(extracted_path, target_path)
            
            return target_path
    except Exception as e:
        print(f"Extract error: {e}")
        return None


def get_file(filename):
    """
    Get path to a file, extracting from compressed archive if needed.
    Returns the full path to the file, or None if not found.
    """
    
    # First check if file exists directly in FILES_DIR
    direct_path = os.path.join(FILES_DIR, filename)
    if os.path.exists(direct_path):
        return direct_path
    
    # Check if already cached
    cached_path = os.path.join(CACHE_DIR, filename)
    if os.path.exists(cached_path):
        return cached_path
    
    # Try to find and extract from compressed archives
    zip_path, arcname = _find_in_zip(filename)
    if zip_path and arcname:
        extracted = _extract_file(zip_path, arcname, cached_path)
        if extracted and os.path.exists(extracted):
            return extracted
    
    return None


def file_exists(filename):
    """Check if a file exists (in FILES_DIR, cache, or compressed archives)."""
    
    # Check direct path
    if os.path.exists(os.path.join(FILES_DIR, filename)):
        return True
    
    # Check cache
    if os.path.exists(os.path.join(CACHE_DIR, filename)):
        return True
    
    # Check compressed archives
    zip_path, arcname = _find_in_zip(filename)
    return zip_path is not None


def list_files():
    """List all available files (from FILES_DIR and compressed archives)."""
    
    files = set()
    
    # List from FILES_DIR
    if os.path.exists(FILES_DIR):
        for item in os.listdir(FILES_DIR):
            if os.path.isfile(os.path.join(FILES_DIR, item)):
                files.add(item)
    
    # List from compressed archives
    compressed_dir = COMPRESSED_DIR
    if not os.path.exists(compressed_dir):
        compressed_dir = os.path.join(os.path.dirname(FILES_DIR), "FilesCompressed")
    
    if os.path.exists(compressed_dir):
        for zip_name in os.listdir(compressed_dir):
            if not zip_name.endswith('.zip'):
                continue
            try:
                zip_path = os.path.join(compressed_dir, zip_name)
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    for name in zf.namelist():
                        if not name.endswith('/'):
                            files.add(os.path.basename(name))
            except:
                continue
    
    return list(files)


def extract_all(group=None):
    """Extract all files from compressed archives to cache."""
    
    _ensure_cache_dir()
    
    compressed_dir = COMPRESSED_DIR
    if not os.path.exists(compressed_dir):
        compressed_dir = os.path.join(os.path.dirname(FILES_DIR), "FilesCompressed")
    
    if not os.path.exists(compressed_dir):
        return False
    
    for zip_name in os.listdir(compressed_dir):
        if not zip_name.endswith('.zip'):
            continue
        
        # Filter by group if specified
        if group and not zip_name.startswith(group):
            continue
        
        try:
            zip_path = os.path.join(compressed_dir, zip_name)
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(CACHE_DIR)
        except Exception as e:
            print(f"Error extracting {zip_name}: {e}")
            continue
    
    return True


def clear_cache():
    """Clear the extracted files cache."""
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)
        return True
    return False


def get_cache_size():
    """Get the size of the cache directory in bytes."""
    if not os.path.exists(CACHE_DIR):
        return 0
    
    total = 0
    for root, dirs, files in os.walk(CACHE_DIR):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    return total
