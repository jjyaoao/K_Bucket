import operator
import hashlib
def shared_prefix(args):
    """
    Find the shared prefix between the strings.

    For instance:

        sharedPrefix(['blahblah', 'blahwhat'])

    returns 'blah'.
    """
    i = 0
    while i < min(map(len, args)):
        if len(set(map(operator.itemgetter(i), args))) != 1:
            break
        i += 1
    return args[0][:i]


def bytes_to_bit_string(bites):
    bits = [bin(bite)[2:].rjust(8, '0') for bite in bites]
    return "".join(bits)

# def node_id_to_long_id(nodeId):
#     # 使用SHA-1哈希函数生成160位摘要
#     hash_object = hashlib.sha1(nodeId.encode())
#     hex_dig = hash_object.hexdigest()
#     long_id = int(hex_dig, 16)
#     return long_id

def node_id_to_long_id(nodeId):
    hash_object = hashlib.sha1(nodeId)
    hex_dig = hash_object.hexdigest()  # 获取十六进制字符串
    long_id = int(hex_dig, 16)  # 转换为整数
    return long_id