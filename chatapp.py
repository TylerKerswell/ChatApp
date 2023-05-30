import socket

# function to encrypt a message given a key value
def encrypt(string, key):
    pass

# function to decrypt a message given a key value
def decrypt(string, key):
    pass

def ClientConnect():

    # get a private IP to connect to
    connectIp = input("Input a private ip address to connect to: ")

    # establish the connection
    s.connect(connectIp + DEFAULT_PORT)

    # do the key exchange




def ServerConnect():

    # listen for the clients connection
    s.bind((IP, DEFAULT_PORT))
    s.listen()

    # when a new connection is established
    con, addr = s.accept()

    # do the key exchange



# set up inital values such as getting this computers IP address and initalizing the socket
DEFAULT_PORT = 5720
IP = socket.gethostbyname(socket.gethostname())
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# let the user decide if this should be a server or a client
start = input("Would you like to wait to recieve a connection? [Y/N] ")

# if no, this device is a client, if anything else, its a server
if start.lower() == "n" or start.lower() == "no":
    ClientConnect()
else:
    ServerConnect()

