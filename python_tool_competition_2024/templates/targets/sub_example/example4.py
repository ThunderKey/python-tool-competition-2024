import gzip

def compress_string(s):
    """
    Compress a string using gzip.

    :param s: String to be compressed
    :type s: str
    :return: Compressed string
    :rtype: bytes
    """
    return gzip.compress(s.encode('utf-8'))

def decompress_string(compressed):
    """
    Decompress a gzipped string.

    :param compressed: Compressed string
    :type compressed: bytes
    :return: Decompressed string
    :rtype: str
    """
    return gzip.decompress(compressed).decode('utf-8')
