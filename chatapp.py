import socket
import random
import threading
import tkinter

# default port to listen on to synchronize the app
DEFAULT_PORT = 5720
# prime number used in the key exchange
PRIME = 31
# primitive root mod PRIME
BASE = 21
# list that contains every connection, connections are represented by a list of [connection, address, key, connectionHasListener], where:
# connection = the socket connection
# address = the IP address that the socket connects to
# key = the key that encrypts/decrypts messages for that socket
# connectionHasListener = boolean value that represents wheather or not that connection has a listener
connections = []
# this devices ip address
IP = socket.gethostbyname(socket.gethostname())
# start the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# semaphore for the server to use for incoming connections, we're basically just using it as a pre-made counter, but more efficently as we don't have to poll
connectionSem = threading.Semaphore(0)
# list of all currently active threads to be used for shutdown
activeThreads = []


# for now, this application uses the caesar cipher to encrypt/decrypt, 
# this will be updated as this application gets further developed

# function to encrypt a message given a key value, takes a string and a key, returns bytes
def Encrypt(string, key):

    crypt = bytearray(string, "utf-8")

    for bite in crypt:
        bite = ((int(bite) + key) % 256).to_bytes()

    return crypt

# function to decrypt a message given a key value, takes bytes and a key, returns a string
def Decrypt(crypt, key):

    for bite in crypt:
        bite = ((int(bite) - key) % 256).to_bytes()

    return crypt.decode("utf-8")




# function to handle the client side key exchange
def ClientConnect(ipAddr):

    # we will close every connection and delete any knowledge of them before connecting to a new server
    for connection in connections:
        connection[0].close()
    connections.clear()

    PrintMessage(f"Trying to connect to {ipAddr}...")
    # establish the connection
    sock.connect((ipAddr, DEFAULT_PORT))

    PrintMessage(f"Connection established with {ipAddr}")

    # do the key exchange, client goes first

    # choose a random number and then perform the math on it (see Wikipedia page on Diffie-Hellman key exchange for more information)
    secret = random.randrange(1, 20)
    PrintMessage(f"secret number chosen: {secret}")

    send = pow(BASE, secret) % PRIME

    # send and wait for servers response
    sock.send(int.to_bytes(send))
    bytesRecvd = sock.recv(4096)

    publicNum = int.from_bytes(bytesRecvd, "little")

    # do the proper math with the servers response and print the key to show that it worked
    key = pow(publicNum, secret) % PRIME
    PrintMessage(f"key: {key}")

    # then add the connection to connections
    connections.append([sock, ipAddr, key, False])

    # then, make a thread to listen to the connection that was just created
    listeningThread = threading.Thread(target = ClientReceiver)
    listeningThread.start()



# handles the server side key exchange and constantly looks for connections
def ServerListen():

    root.unbind("<Map>")
    sock.bind((IP, DEFAULT_PORT))


    PrintMessage("Waiting for first connection...")
    
    while True:
        # start listening for a connection
        sock.listen()

        # when a new connection is established
        con, addr = sock.accept()

        PrintMessage(f"connection established with {addr[0]}")

        # do the key exchange, client goes first

        # wait to receive the clients secret
        bytesRecvd = con.recv(4096)

        # choose our own secret number and do the math to send it to the client
        secret = random.randrange(1, 20)
        PrintMessage(f"secret number chosen: {secret}")
        send = pow(BASE, secret) % PRIME

        con.send(int.to_bytes(send))

        # get the key from what the client sent us
        publicNum = int.from_bytes(bytesRecvd, "little")

        # do the proper math with the servers response and print the key to show that it worked
        key = pow(publicNum, secret) % PRIME
        PrintMessage(f"key with {addr[0]}: {key}")

        # now we add this connection to the list of connections that the server has, and then listen for another one
        connections.append([con, addr, key, False])

        # lastly, we notify the semaphore to start the listening connection in the handler
        connectionSem.release(1)


#  easily prints a message to the main gui
def PrintMessage(msg):
    messageDisplay.configure(state = "normal")
    messageDisplay.insert(tkinter.END, msg + '\n')
    messageDisplay.configure(state = "disabled")


# only used in send message button
def SendMsg():
    Broadcast(messageEntry.get())
    PrintMessage("You: " + messageEntry.get())
    messageEntry.delete(0, tkinter.END)

#  broadcasts a single message to all connections
def Broadcast(msg):
    for connection in connections:
        crypticMessage = Encrypt(msg, connection[2])
        connection[0].send(crypticMessage)

# handles receiving messages from all connected clients
def ServerConnectionHandler():
    while True:
        # when we are notified that a new connection is added, spin up a listening thread to listen to that connection
        connectionSem.acquire()
        for connection in connections:
            if connection[3] == False:
                # mark this connection as being listened on
                connection[3] = True

                # start the listening thread
                listener = threading.Thread(target = Receiver, args = [connection[0], connection[1], connection[2]])
                listener.start()


# receives messages from one connection and handles accordingly
def Receiver(con, addr, key):
    while True:
        # wait to recieve a message from this specific connection
        message = con.recv(4096)
        message = Decrypt(message, key)

        # print it to the server's screen and broadcast the message to all other connections
        # depending on how long this step takes, the thread might miss receiving the next message which is a bug to deal with later
        PrintMessage(addr[0] + ": " + message)
        for connection in connections:
            if connection[0] != con:
                msg = Encrypt(message, connection[2])
                connection[0].send(msg)



# this function listens on the clients only connection and decrypts, then prints to the screen when something is sent. simple.
def ClientReceiver():
    while True:
        message = connections[0][0].recv(4096)
        message = Decrypt(message, connections[0][2])
        PrintMessage(connections[0][1] + ": " + message)





# START MENU
# we use a start menu to let the user determine if they want a server or a client application to run
startMenu = tkinter.Tk()
startMenu.title("choose an mode for this application")
startMenu.geometry("300x150+50+50")

# variable for keeping track of wheather or not this application is a server. Defaults to client
server = tkinter.IntVar(value = 1)

# text prompt for user
startLabel = tkinter.Label(startMenu, text = "Would you like this to be a client or a server?")
startLabel.pack()

# buttons for the user to make their decision
clientButton = tkinter.Radiobutton(startMenu, text = "Client", variable = server, value = 1)
clientButton.pack()

serverButton = tkinter.Radiobutton(startMenu, text = "Server", variable = server, value = 2)
serverButton.pack()

# button destroys the start menu and moves onto the main chat GUI
confirmButton = tkinter.Button(startMenu, text = "Confirm", command = startMenu.destroy)
confirmButton.pack()


startMenu.mainloop()






# MAIN WINDOW
root = tkinter.Tk()
root.title("chat app")
root.geometry("600x400+50+50")
root.resizable(False, True)

# FRAME FOR CONNECTION, only needed if this is a client and not a server
if server.get() == 1:
    connectionFrame = tkinter.Frame(root)
    connectionFrame.place(relheight = 0.1, relwidth = 1)

    connectionEntry = tkinter.Entry(connectionFrame)
    connectionEntry.place(relwidth = 0.7, relheight = 1)

    connectionButton = tkinter.Button(connectionFrame, text = "connect", command = lambda: ClientConnect(connectionEntry.get()))
    connectionButton.place(relx = 0.7, relwidth = 0.3, relheight = 1)


# MAIN MESSGE DISPLAY
messageDisplay = tkinter.Text(root, state = "disabled")
messageDisplay.place(rely = 0.1, relheight = 0.8, relwidth = 1)

# we must start listening immediatly if this is a server, so we bind it to the first time this window becomes visible
if server.get() == 2:
    listeningThread = threading.Thread(target = ServerListen)
    listeningThread.start()
    handler = threading.Thread(target = ServerConnectionHandler)
    handler.start()



# MESSAGE INPUT DISPLAY
messageFrame = tkinter.Frame(root)
messageFrame.place(rely = 0.9, relheight = 0.1, relwidth = 1)

messageEntry = tkinter.Entry(messageFrame)
messageEntry.place(relwidth = 0.7, relheight = 1)

messageButton = tkinter.Button(messageFrame, text = "Send message", command = SendMsg)
messageButton.place(relx = 0.7, relwidth = 0.3, relheight = 1)


root.mainloop()


# let the user decide if this should be a server or a client
# start = input("Would you like to wait to recieve a connection? [Y/N] ")

# # if no, this device is a client, if anything else, its a server
# if start.lower() == "n" or start.lower() == "no":
#     key, con = ClientConnect()
# else:
#     key, con = ServerConnect()

# # now that the key exchange has been done and we are connected, we will start threads to handle sending and receiving of messages

# receThread = threading.Thread(target=receiving, args=(con, key))
# receThread.start()
# sending(con, key)