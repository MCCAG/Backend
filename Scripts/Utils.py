from hashlib import sha256


def generate_id(*args) -> str:
    hash_object = sha256(('+'.join(args)).encode())
    return hash_object.hexdigest()
