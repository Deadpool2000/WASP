import os

try:
    # Try to read the version from a file named 'version.txt' in the same directory
    version_file = os.path.join(os.path.dirname(__file__), "version.txt")
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            VERSION = f.read().strip()
    else:
        # Fallback version
        VERSION = "1.0.0"
except Exception:
    VERSION = "1.0.0"
