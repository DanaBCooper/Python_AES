"""
State/Keys = List of 4 Byte Arrays (Row - Major)
"""


def key_expansion(key):
    """
    128 bit key -> 11 128 bit keys
    """
    return None


def key_add(state, round_key):
    """
    Takes two lists of length 4 containing byte arrays.
    Will work for any list length (as long as the same)
    """
    if len(state) != len(round_key):
        raise ValueError("Lists in Key_Add not the same length")

    array = []
    for i in range(0, len(state)):
        array.append(bytearray(a ^ b for (a, b) in zip(state[i], round_key[i])))
    return array


def add_f28(left, right):
    """Trivial / Unused"""
    return left ^ right


def mul_f28_by_x(a):
    """Multiplies an F_2^8 element by x, reducing as appropriate"""
    if (a & 0x80) == 0x80:
        return 0x1B ^ (a << 1)
    return a << 1


def mul_f28(a,b):
    return None


def s_box(element):
    return None


def sub_bytes(state):
    for row in state:
        for element in row:
            element = s_box(element)


def shift_rows(state):
    return None


def aes_enc(key, message):
    return None


b = bytearray(5)
b = bytearray.fromhex('AAAA80AA')
