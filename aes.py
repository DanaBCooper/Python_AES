"""
An implentation of 128 bit AES that takes a 128 bit key + a 128 bit message (in hex byte arrays), and encrypts them.
States/Keys are stored in column major
"""

def round_constant(round, prev_rc):
    """Given the round number + previous round constant, calculates the new round constant"""
    if round == 1:
        return 1
    if round > 1 and prev_rc < 80:
        return 2 * prev_rc
    if round > 1 and prev_rc >= 80:
        return mod_256(((2 * prev_rc) ^ 0x1B))


def next_key(round_key, const):
    """Given a round key + a round constant, returns the next round key"""
    rk = []
    buff = bytearray(3)

    buff[0:3] = const ^ s_box(round_key[3][1]) ^ round_key[0][0], s_box(round_key[3][2]) ^ round_key[0][
1], \
                     s_box(round_key[3][3]) ^ round_key[0][2], s_box(round_key[3][0]) ^ round_key[0][3]

    rk.append(buff)

    for b in range(1, 4):
        col = bytearray(3)
        col[0:3] = buff[0] ^ round_key[b][0], buff[1] ^ round_key[b][1], buff[2] ^ round_key[b][2], buff[3] ^ \
                   round_key[b][3]
        rk.append(col)
        buff = col
    return rk


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
    """Could be inlined but left as a function for readability
       Adds two F_28 numbers, which is equivelent to XORing them"""
    return left ^ right


def mod_256(a):
    """Calculates a number mod 256"""
    rem = a // 256
    a = a - rem * 256
    return a


def mul_f28_by_x(a):
    """Multiplies an F_2^8 element by x, reducing as appropriate"""
    if (a & 0x80) == 0x80:
        return 0x1B ^ mod_256(a << 1)
    return mod_256(a << 1)


def mul_f28(a, b):
    """ Multiples two F_2^8 elements.
        The only place degree is increased is in the multiplication of t, which reduces already"""
    t = 0
    for i in range(7, -1, -1):
        t = mul_f28_by_x(t)
        if (b & pow(2, i)) == pow(2, i):
            t ^= a
    return t


def inverse(a):
    """ Inverts an F_2^8 element. By Fermats Little Theorem,
    a^254 is an inverse (
print(array[2][3])as a ^ 255 = 1)"""

    b = mul_f28(a, a)  # b = a^2
    c = mul_f28(a, b)  # c = a^3
    b = mul_f28(b, b)  # b = a^4
    c = mul_f28(b, c)  # c = a^7
    b = mul_f28(b, b)  # b = a^8
    b = mul_f28(b, c)  # b = a^15
    b = mul_f28(b, b)  # b = a^30
    b = mul_f28(b, b)  # b = a^60
    c = mul_f28(b, c)  # c = a^67

    c = mul_f28(b, c)  # c = a^127
    c = mul_f28(c, c)  # c = a^254

    return c




def shift_rows(s):
    """Given a state, shifts rows around and returns a new state"""
    a = bytearray(3)
    b = bytearray(3)
    c = bytearray(3)
    d = bytearray(3)
    a[0:3] = s[0][0], s[1][1], s[2][2], s[3][3]
    b[0:3] = s[1][0], s[2][1], s[3][2], s[0][3]
    c[0:3] = s[2][0], s[3][1], s[0][2], s[1][3]
    d[0:3] = s[3][0], s[0][1], s[1][2], s[2][3]

    new = [a, b, c, d]

    return new


def mix_columns(s):
    """Given a state, manipulates and calculates the new state"""
    matrix = [[2, 3, 1, 1], [1, 2, 3, 1], [1, 1, 2, 3], [3, 1, 1, 2]]

    a = bytearray(4)
    b = bytearray(4)
    c = bytearray(4)
    d = bytearray(4)
    new = [a, b, c, d]

    for a in range(4):
        # Per Column
        for b in range(4):
            new[a][b] = add_f28(mul_f28(matrix[b][0], s[a][0]), add_f28(mul_f28(matrix[b][1], s[a][1]),
                                                                        add_f28(mul_f28(matrix[b][2], s[a][2]),
                                                                                mul_f28(matrix[b][3], s[a][3]))))
    return new


def s_box(element):
    """ Invert + reallign coefficients and adding a constant"""
    element = inverse(element)
    element = 99 ^ element ^ mod_256(element << 1) ^ mod_256(element << 2) ^ mod_256(element << 3) \
              ^ mod_256(element << 4) ^ mod_256(element >> 4) ^ mod_256(element >> 5) \
              ^ mod_256(element >> 6) ^ mod_256(element >> 7)
    return element


def sub_bytes(s):
    """Applies an S-BOX to every element in a state"""
    for a in range(0, 4):
        for b in range(0, 4):
            s[a][b] = s_box(s[a][b])
    return s


def aes_enc(key, message):
    round_key = key
    state = message
    state = key_add(state, round_key)
    constant = 0

    for round_count in range(1, 10):
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state)
        constant = round_constant(round_count, constant)
        round_key = next_key(round_key, constant)
        state = key_add(state, round_key)

    state = sub_bytes(state)
    state = shift_rows(state)
    constant = round_constant(10, constant)
    round_key = next_key(round_key, constant)
    state = key_add(state, round_key)
    cipher = state
    return cipher


b = bytearray(5)
a = bytearray.fromhex('2B7E1516')
b = bytearray.fromhex('28AED2A6')
c = bytearray.fromhex('ABF71588')
d = bytearray.fromhex('09CF4F3C')
key = [a, b, c, d]

a = bytearray.fromhex('3243F6A8')
b = bytearray.fromhex('885A308D')
c = bytearray.fromhex('313198A2')
d = bytearray.fromhex('E0370734')
message = [a, b, c, d]
c = aes_enc(key, message)

print(c)
for a in c:
    print(bytearray.hex(a))
# k=〈2B,7E,15,16,28,AE,D2,A6,AB,F7,15,88,09,CF,4F,3C〉(28)
# m=〈32,43,F6,A8,88,5A,30,8D,31,31,98,A2,E0,37,07,34〉
