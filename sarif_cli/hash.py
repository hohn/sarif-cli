from hashlib import blake2b

# takes a bytes object and outputs an 8 byte hash
def hash_unique(item_to_hash):
    h = blake2b(digest_size = 8)
    h.update(item_to_hash)
    return int.from_bytes(h.digest(), byteorder='big')
