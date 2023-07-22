import base64


def decode_base36(c: int) -> int:
    if c >= ord("0") and c <= ord("9"):
        return c - ord("0")
    if c >= ord("a") and c <= ord("z"):
        return c - ord("a") + 0x0A
    return 0xFF


def decrypt_spade_inner(spade_key: bytes) -> bytearray:
    result = bytearray(spade_key)
    buff = b"\xFA\x55" + spade_key

    for i in range(len(result)):
        v = (spade_key[i] ^ buff[i]) - i.bit_count() - 21
        while v < 0:
            v += 0xFF
        result[i] = v

    return result


def decrypt_spade(spade_key: bytes) -> str:
    spade_key_len = len(spade_key)
    if spade_key_len < 3:
        return ""  # spade too short

    padding_len = (spade_key[0] ^ spade_key[1] ^ spade_key[2]) - b"0"[0]
    if spade_key_len < padding_len + 2:
        return ""  # overflow, invalid spade

    decoded_message_len = spade_key_len - padding_len - 2
    tmp_buff = decrypt_spade_inner(spade_key[1: spade_key_len - padding_len])
    skip_bytes = decode_base36(tmp_buff[0])
    return tmp_buff[1: 1 + decoded_message_len - skip_bytes].decode("utf-8")


def decrypt_spade_a(spade_a: str) -> str:
    return decrypt_spade(base64.b64decode(spade_a))


if __name__ == "__main__":
    print("testing...")
    assert (
        decrypt_spade_a("kLwe+la9BvZLvwzvcaI97HOnPO9ClAroRbgK8Xa5CPBCuAqDgw==")
        == "5011945309e6465581fd0d6971c0e002"
    )
    print("test ok!")
