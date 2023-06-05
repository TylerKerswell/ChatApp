import socket
import random

# prime number used in the key exchange
PRIME = 14260171
# primitive root mod PRIME
BASE = 14260075

# this file contains the methods that perform the key exchange on a given active socket connection
# the key exchange needs to be seperated into two seperate functions in order to stagger receiving/sending


def ClientExchange(connection):
    print("waiting for the server...")
    # wait for the server to send its bit
    bytesRecvd = connection.recv(4096)
    publicNum = int.from_bytes(bytesRecvd, "little")

    print("got num")
    
    # choose our own secret and send it, hiding it with the proper math
    secret = random.randint(1, 100000)

    print(f"secret: {secret}")

    modifiedSecret = FastPow(BASE, secret) % PRIME

    print(f"send: {modifiedSecret}")
    connection.send(modifiedSecret.to_bytes(4096, byteorder = "little"))

    # do the proper math with the servers response
    key = FastPow(publicNum, secret) % PRIME

    print("finished")
    # return the generated key and the secret that we used
    return key, secret





def ServerExchange(connection):
        
    # choose our own secret number and do the math to send it to the client
    secret = random.randrange(1, 100000)

    print(f"chose {secret}")

    # perform the algorithm to hide the chosen secret number and then send it
    modifiedSecret = FastPow(BASE, secret) % PRIME

    print(f"send: {modifiedSecret}")
    connection.send(modifiedSecret.to_bytes(4096, byteorder = "little"))

    print("waiting for client")
    # get the key from what the client sent us
    bytesRecvd = connection.recv(4096)
    publicNum = int.from_bytes(bytesRecvd, "little")

    # do the proper math with the clients response
    key = FastPow(publicNum, secret) % PRIME
    
    print("finished")
    # return the generated key and the secret that we used
    return key, secret


# function to raise base to an exponent using exponentiation by squaring
# much faster than the pow() function
def FastPow(base, exp):
    powers = [base]
    final = 1
    exp = exp >> 1

    while exp != 0:
        powers.append(powers[-1] * powers[-1])
        if exp & 1:
            final *= powers[-1]
        exp = exp >> 1

    return final