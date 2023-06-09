import socket
import threading
import tkinter
import encryption
import key_exchg

# default port to listen on to synchronize the app
DEFAULT_PORT = 5720
# list that contains every connection, connections are represented by a list of [connection, address, key, connectionHasListener, username], where:
# connection = the socket connection
# address = the IP address that the socket connects to
# key = the key that encrypts/decrypts messages for that socket
# connectionHasListener = boolean value that represents wheather or not that connection has a listener
# username = username of client
connections = []
# this devices ip address
IP = socket.gethostbyname(socket.gethostname())
# start the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# semaphore for the server to use for incoming connections, we're basically just using it as a pre-made counter, but more efficently as we don't have to poll
connectionSem = threading.Semaphore(0)
# list of all currently active threads to be used for shutdown
activeThreads = []

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

    # once we've established the connection, give the server our username
    sock.send(username.encode("utf-8"))

    # do the key exchange
    key, secret = key_exchg.ClientExchange(sock)
    PrintMessage(f"Secret used: {secret}\nKey aquired: {key}")

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

        # recieve the clients username
        name = con.recv(4096)
        PrintMessage(f"Their username is: {name}")

        # do the key exchange
        key, secret = key_exchg.ServerExchange(con)
        PrintMessage(f"Secret used: {secret}\nKey: {key}")

        # now we add this connection to the list of connections that the server has, and then listen for another one
        connections.append([con, addr, key, False, name])

        # lastly, we notify the semaphore to start the listening connection in the handler
        connectionSem.release(1)


#  easily prints a message to the main gui
def PrintMessage(msg):
    messageDisplay.configure(state = "normal")
    messageDisplay.insert(tkinter.END, msg + '\n')
    messageDisplay.configure(state = "disabled")


# only used in send message button, 
# sends the message to all connections, prints it to the screen, then deletes whatevers inside the message entry box
def SendMsg():
    Broadcast(messageEntry.get())
    PrintMessage("You: " + messageEntry.get())
    messageEntry.delete(0, tkinter.END)

#  broadcasts a single message to all connections
def Broadcast(msg):
    msg = username + ": " + msg
    for connection in connections:
        crypticMessage = encryption.Encrypt(msg, connection[2])
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
        message = encryption.Decrypt(message, key)

        # print it to the server's screen and broadcast the message to all other connections
        # depending on how long this step takes, the thread might miss receiving the next message which is a bug to deal with later
        PrintMessage(message)
        for connection in connections:
            if connection[0] != con:
                msg = encryption.Encrypt(message, connection[2])
                connection[0].send(msg)



# this function listens on the clients only connection and decrypts, then prints to the screen when something is sent. simple.
def ClientReceiver():
    while True:
        message = connections[0][0].recv(4096)
        message = encryption.Decrypt(message, connections[0][2])
        PrintMessage(message)



# behaviour for when the user clicks the confirm button
def ConfirmButton():
    global username
    username = usernameInput.get()
    startMenu.destroy()





# START MENU
# we use a start menu to let the user determine if they want a server or a client application to run and also for the user to choose their username
startMenu = tkinter.Tk()
startMenu.title("choose an mode for this application and a username")
startMenu.geometry("300x150+50+50")

# text prompt for username
usernameLabel = tkinter.Label(startMenu, text = "Username:")
usernameLabel.pack()

# entrybox for username
usernameInput = tkinter.Entry(startMenu)
usernameInput.pack()


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
confirmButton = tkinter.Button(startMenu, text = "Confirm", command = ConfirmButton)
confirmButton.pack()


startMenu.mainloop()






# MAIN WINDOW
root = tkinter.Tk()
root.title(f"Logged in as {username}")
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