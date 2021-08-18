import hashlib

def generate_sign(secret_key, **params):
    sorted_keys = sorted(list(params.keys()))

    joined_str = ":".join([params[key] for key in sorted_keys]) + secret_key
    h = hashlib.sha256(joined_str.encode())

    return h.hexdigest()
