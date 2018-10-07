import numpy as np


def gf_mul(a, b):
    p = 0
    for i in range(8):
        if b & 1 == 1:
            p ^= (a << i)
        b >>= 1
    if p <= 255:
        return p
    while 1:
        k = p.bit_length() - 9
        if k <= -1:
            return p
        p ^= (0x11b << k)


if __name__ == '__main__':
    mul_table = [[gf_mul(i,j) for j in range(256)] for i in range(256)]
    mul_table = np.array(mul_table, dtype='uint8')
    np.save('mul_table_AES.npy', mul_table)