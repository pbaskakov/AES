import Sbox, InvSbox, numpy as np
from random import getrandbits


def string_expansion(byte_str): # осуществляет расширение строки
    while len(byte_str) % 16 != 0:
        byte_str += b'\x00'
    return byte_str


def rot_word(word): # сдвиг слова влево на 1 байт
    byte_word = '{:08X}'.format(word)
    new_word = (byte_word + byte_word[:2])[2:]
    return int(new_word, 16)


def sub_word(word): # замена байт в слове по таблице замен
    byte_word = '{:08X}'.format(word)
    byte_list = [byte_word[2*i:2*(i+1)] for i in range(4)]
    for i in range(4):
        row, column = map(lambda x: int(x, 16), byte_list[0])
        byte_list.append('{:02X}'.format(Sbox.sbox[row][column]))
        byte_list.pop(0)
    return int(''.join(byte_list), 16)


def key_expansion(key, n): # расширение ключа
    rcon = (0x01000000, 0x02000000, 0x04000000, 0x08000000, 0x10000000, 0x20000000, 0x40000000, 0x80000000, 0x1b000000, 0x36000000)
    if n == 128:
        for i in range(4, 44):
            if i % 4 != 0:
               key.append(key[i-1] ^ key[i-4])
            else:
                t = sub_word(rot_word(key[i-1])) ^ rcon[i//4 - 1]
                key.append(t ^ key[i-4])
    elif n == 192:
        for i in range(6, 52):
            if i % 6 != 0:
                key.append(key[i-1] ^ key[i-6])
            else:
                t = sub_word(rot_word(key[i-1])) ^ rcon[i//6 - 1]
                key.append(t ^ key[i-6])
    else:
        for i in range(8, 60):
            if i % 8 != 0:
                if i % 4 != 0:
                    key.append(key[i-1] ^ key[i-8])
                else:
                    key.append(sub_word(key[i-1]) ^ key[i-8])
            else:
                t = sub_word(rot_word(key[i-1])) ^ rcon[i//8 - 1]
                key.append(t ^ key[i-8])


def add_round_key(block, RoundKey): # сложение с раундовым ключом
    for i in range(4):
        for j in range(4):
            block[i][j] ^= RoundKey[i][j]

            
def get_input_block(byte_str, i): # получение входного блока
    input_block = []
    for k in range(4):
        new_line = []
        start = 16 * i + k
        for j in range(4):
            new_line.append(byte_str[start + j * 4])
        input_block.append(new_line)
    return input_block


def sub_bytes(block): # замена байт в блоке по таблице замен
    for i in range(4):
        for j in range(4):
            row, column = map(lambda x: int(x, 16), '{:02X}'.format(block[i][j]))
            block[i][j] = Sbox.sbox[row][column]


def shift_rows(block): # сдвиг строк блока
    for i in range(1, 4):
        for k in range(i):
            block[i].append(block[i].pop(0))


def mix_columns(block): # перемешивание столбцов
    for j in range(4):
        s = [block[i][j] for i in range(4)]
        block[0][j] = mul_table[2, s[0]] ^ mul_table[3, s[1]] ^ s[2] ^ s[3]
        block[1][j] = s[0] ^ mul_table[2, s[1]] ^ mul_table[3, s[2]] ^ s[3]
        block[2][j] = s[0] ^ s[1] ^ mul_table[2, s[2]] ^ mul_table[3, s[3]]
        block[3][j] = mul_table[3, s[0]] ^ s[1] ^ s[2] ^ mul_table[2, s[3]]


def get_round_key(key, round): # получение раундового ключа
    RoundKey = []
    words = ['{:08X}'.format(key[i]) for i in range(4*round, 4*(round+1))]
    for i in range(4):
        new_line = [int(word[2*i : 2*(i+1)], 16) for word in words]
        RoundKey.append(new_line)
    return RoundKey


def inv_shift_rows(block): # сдвиг строк state вправо
    for i in range(1, 4):
        for j in range(i):
            block[i].insert(0, block[i].pop())


def inv_sub_bytes(block): # замена байт по инвертированной таблице замен
    for i in range(4):
        for j in range(4):
            row, column = map(lambda x: int(x, 16), '{:02X}'.format(block[i][j]))
            block[i][j] = InvSbox.inv_sbox[row][column]


def inv_mix_columns(block): # перемешивание столбцов
    for j in range(4):
        s = [block[i][j] for i in range(4)]
        block[0][j] = mul_table[0x0e, s[0]] ^ mul_table[0x0b, s[1]] ^ mul_table[0x0d, s[2]] ^ mul_table[0x09, s[3]]
        block[1][j] = mul_table[0x09, s[0]] ^ mul_table[0x0e, s[1]] ^ mul_table[0x0b, s[2]] ^ mul_table[0x0d, s[3]]
        block[2][j] = mul_table[0x0d, s[0]] ^ mul_table[0x09, s[1]] ^ mul_table[0x0e, s[2]] ^ mul_table[0x0b, s[3]]
        block[3][j] = mul_table[0x0b, s[0]] ^ mul_table[0x0d, s[1]] ^ mul_table[0x09, s[2]] ^ mul_table[0x0e, s[3]]


def keygen(n): # генерация ключа
    key = []
    for i in range(n // 32):
        key.append(getrandbits(32))
    return key


def encrypt(opentext, key): # функция шифрования
    nr = (len(key) - 4) // 4
    cipherbytes = []
    for i in range(len(opentext) // 16):
        input_block = get_input_block(opentext, i)
        add_round_key(input_block, get_round_key(key, 0))
        for round in range(1, nr):
            sub_bytes(input_block)
            shift_rows(input_block)
            mix_columns(input_block)
            add_round_key(input_block, get_round_key(key, round))
        sub_bytes(input_block)
        shift_rows(input_block)
        add_round_key(input_block, get_round_key(key, nr))
        cipherbytes += list(np.reshape(input_block, (16,), order='F'))
    return bytes(cipherbytes)


def decrypt(ciphertext, key): # функция дешифрования
    nr = (len(key) - 4) // 4
    openbytes = []
    for i in range(len(ciphertext) // 16):
        input_block = get_input_block(ciphertext, i)
        add_round_key(input_block, get_round_key(key, nr))
        for round in range(nr - 1, 0, -1):
            inv_shift_rows(input_block)
            inv_sub_bytes(input_block)
            add_round_key(input_block, get_round_key(key, round))
            inv_mix_columns(input_block)
        inv_shift_rows(input_block)
        inv_sub_bytes(input_block)
        add_round_key(input_block, get_round_key(key, 0))
        openbytes += list(np.reshape(input_block, (16, ), order='F'))
    return bytes(openbytes).rstrip(b'\x00')


mul_table = np.load('mul_table_AES.npy')


if __name__ == '__main__':
    # Пример работы программы #
    n = 128
    key = keygen(n)
    key_expansion(key, n)
    opentext = string_expansion(input('Enter opentext: ').encode('cp1251'))
    ciphertext = encrypt(opentext, key)
    print('A bytes-like ciphertext:', ciphertext)
    decrypted_text = decrypt(ciphertext, key).decode('cp1251')
    print('Decrypted text:', decrypted_text)