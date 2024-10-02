from hashlib import sha256


def generate_id(*args) -> str:
    args = [str(arg) for arg in args]
    hash_object = sha256(('+'.join(args)).encode())
    return hash_object.hexdigest()
