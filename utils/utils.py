import re

def sanitize_key(key: str) -> str:
    return key.strip().lower().replace("#", "").replace(" ", "_")

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\-.]', '_', name)