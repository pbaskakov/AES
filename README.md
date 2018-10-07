# AES
To launch the program, please run AES.py. __Note__: you shoud have installed Python 3.x and a NumPy library.

Description of included files:
* AES.py - launchable file; contains general functions for encryption and decryption;
* Sbox.py - contains Sbox table needed for byte substitution in sub_bytes function;
* InvSbox.py - contains inverted Sbox table needed for byte substitution in inv_sub_bytes function;
* Gf_Mul.py - run this file to get multiplication table in GF(2^8) (although, it's already included here);
* mul_table_AES.npy - multiplication table in GF(2^8) by irreducible polynomial m(x) = x8 + x 4 + x3 + x +1 stored as a NumPy array.
