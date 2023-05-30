import socket
import random

# default port to listen on to synchronize the app
DEFAULT_PORT = 5720
# prime number used in the key exchange
PRIME = 31
# primitive root mod PRIME
BASE = 21


# function to encrypt a message given a key value
def encrypt(string, key):
    pass

# function to decrypt a message given a key value
def decrypt(string, key):
    pass

# function to handle the client side key exchange, returns the private key
def ClientConnect():

    # get a private IP to connect to
    connectIp = input("Input a private ip address to connect to: ")

    # establish the connection
    s.connect((connectIp, DEFAULT_PORT))

    print("Connection established")

    # do the key exchange, client goes first

    # choose a random number and then perform the math on it (see Wikipedia page on Diffie-Hellman key exchange for more information)
    secret = random.randrange(1, 20)

    print(f"secret number chosen: {secret}")

    send = pow(BASE, secret) % PRIME

    # send and wait for servers response
    s.send(int.to_bytes(send))
    bytesRecvd = s.recv(4096)
    publicNum = int.from_bytes(bytesRecvd, "little")

    # do the proper math with the servers response and print the key to show that it worked
    key = pow(publicNum, secret) % PRIME

    print(f"key: {key}")

    return key


# function to handle the server side key exchange, returns the private key
def ServerConnect():

    # listen for the clients connection
    s.bind((IP, DEFAULT_PORT))

    print("Waiting for a connection...")
    s.listen()

    # when a new connection is established
    con, addr = s.accept()

    print(f"connection established with {addr[0]}")

    # do the key exchange, client goes first

    # receive the clients secret
    bytesRecvd = con.recv(4096)

    # choose our own secret number and do the math to send it to the client
    secret = random.randrange(1, 20)
    send = pow(BASE, secret) % PRIME
    con.send(int.to_bytes(send))

    print(f"secret number chosen: {secret}")

    # get the key from what the client sent us
    publicNum = int.from_bytes(bytesRecvd, "little")

    # do the proper math with the servers response and print the key to show that it worked
    key = pow(publicNum, secret) % PRIME

    print(f"key: {key}")

    return key










# set up inital values such as getting this computers IP address and initalizing the socket
IP = socket.gethostbyname(socket.gethostname())
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# let the user decide if this should be a server or a client
start = input("Would you like to wait to recieve a connection? [Y/N] ")

# if no, this device is a client, if anything else, its a server
if start.lower() == "n" or start.lower() == "no":
    key = ClientConnect()
else:
    key = ServerConnect()



