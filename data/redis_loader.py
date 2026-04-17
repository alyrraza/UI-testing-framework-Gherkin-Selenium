# redis_loader.py
# Redis se test data padhna
# Redis = super fast key-value store
# Real world: Whiteboard pe sticky notes — fast access

import redis
import json

def get_redis_client():
    # Redis se connect karo
    # localhost = apna hi computer
    # port 6379 = Redis ka default port
    try:
        client = redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True
        )
        # connection test karo
        client.ping()
        return client
    except Exception:
        # Redis nahi chala — None return karo
        return None

def get_credentials_from_redis(key: str = "test:credentials"):
    # Redis se credentials lao
    client = get_redis_client()
    if client is None:
        # Redis available nahi — fallback data
        return {"username": "standard_user", "password": "secret_sauce"}

    data = client.get(key)
    if data:
        return json.loads(data)
    return {"username": "standard_user", "password": "secret_sauce"}

def seed_redis_data():
    # Redis mein test data daalo
    client = get_redis_client()
    if client is None:
        return False

    credentials = {
        "username": "standard_user",
        "password": "secret_sauce"
    }
    client.set("test:credentials", json.dumps(credentials))
    return True