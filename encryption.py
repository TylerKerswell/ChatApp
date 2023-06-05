# this file stores the functions used to encrypt/decrypt using TEA
# to learn how TEA works: https://en.wikipedia.org/wiki/Tiny_Encryption_Algorithm


# function to encrypt a message given a key value, takes a string and a key, returns a byte array
def Encrypt(string, key):

    # turn the inputted string into a byte array and turn the key into a byte array in order to use byte operations for the algorithm
    crypt = bytearray(string, "utf-8")
    byteKey = key.to_bytes(16, "little")
    
    # TEA works on 64 bit blocks, we will do this to ensure our input is in 64 bit incriments
    while len(crypt) % 8 != 0:
        crypt.append(0x00)

    # seperate the crypt byte array in to 8 byte chunks and encrypt them individually with TEA block cipher
    i = 0
    while len(crypt) - i != 0:
        crypt[i:i+4], crypt[i+4:i+8] = EncryptCycles(crypt[i:i+4], crypt[i+4:i+8], byteKey)
        i += 8

    # return the byte array
    return crypt


# helper function for TEA, left and right are 4 bytes to encrypt and key is a 16 byte key, returns 2, 4-byte encrypted bytes
def EncryptCycles(left, right, key):

    # we must convert all our inputs to integers, because python can't perform bitwise operators on non-integer types -_-
    left = int.from_bytes(left, "little")
    right = int.from_bytes(right, "little")
    k0 = int.from_bytes(key[0:4])
    k1 = int.from_bytes(key[4:8])
    k2 = int.from_bytes(key[8:12])
    k3 = int.from_bytes(key[12:16])

    # constant and sum for the TEA
    delta = 0x9E3779B9
    sum = 0

    # basic cycles
    for i in range(32):
        sum += delta

        left += ((right<<4) + k0) ^ (right + sum) ^ ((right>>5) + k1)

        # we must do this to ensure the output is 4 bytes long
        left = 0xFFFFFFFF & left

        right += ((left<<4) + k2) ^ (left + sum) ^ ((left>>5) + k3)

        # we must do this to ensure the output is 4 bytes long
        right = 0xFFFFFFFF & right

    # returns 2, 4 byte numbers
    return left.to_bytes(4, "little"), right.to_bytes(4, "little")


# function to decrypt a message given a key value, takes bytes as the input and an integer as the key, returns a string, inverse of Encrypt
def Decrypt(crypt, key):

    crypt = bytearray(crypt)
    byteKey = key.to_bytes(16, "little")

    # seperate the crypt byte array in to 8 byte chunks and encrypt them individually with TEA block cipher
    i = 0
    while i != len(crypt):
        crypt[i:i+4], crypt[i+4:i+8] = DecryptCycles(crypt[i:i+4], crypt[i+4:i+8], byteKey)
        i += 8

    # remove all appended 0x00 from the encryption step, there can only be a max of 7 appended 0x00
    for i in range(0, 8):
        try:
            crypt.remove(0x00)
        except:
            break

    # convert from byte array to string and return
    return crypt.decode("utf-8")


# inverse of EncryptCycles
def DecryptCycles(left, right, key):
    # setup initial values and convert inputs to integers, like in EncryptCycles
    delta = 0x9E3779B9
    sum = (delta << 5) & 0xFFFFFFFF

    left = int.from_bytes(left, "little")
    right = int.from_bytes(right, "little")
    k0 = int.from_bytes(key[0:4])
    k1 = int.from_bytes(key[4:8])
    k2 = int.from_bytes(key[8:12])
    k3 = int.from_bytes(key[12:16])


    # perform the cycles
    for i in range(32):
        right -= ((left<<4) + k2) ^ (left + sum) ^ ((left>>5) + k3)

        # make sure right is alwasy 4 bytes long
        right = 0xFFFFFFFF & right

        left -= ((right<<4) + k0) ^ (right + sum) ^ ((right>>5) + k1)

        # make sure left is alwasy 4 bytes long
        left = 0xFFFFFFFF & left

        sum -= delta
    
    # return the 2, 4-byte long bytes types
    return left.to_bytes(4, "little"), right.to_bytes(4, "little")