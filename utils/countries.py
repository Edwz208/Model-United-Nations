def sanitize_key(key: str) -> str:
    return key.strip().lower().replace("#", "").replace(" ", "_")
