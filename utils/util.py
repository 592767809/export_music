
import base64


def popcount(number):
    return len(bin(number).split('1')) - 1


def decrypt_spade_a(spade):
    spade = base64.b64decode(spade.encode())
    slat = spade[0] ^ spade[1] ^ spade[2]
    key_len = len(spade) - slat + 47
    xor_list = bytes([250, 85]) + spade[1: 1 + key_len]
    key = bytearray()
    for i in range(key_len):
        key.append((xor_list[i] ^ xor_list[i + 2]) - 21 - popcount(i))
    return key[1:-1].decode()
