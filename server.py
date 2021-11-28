import socket, select
from _thread import *

users = {}
connections = []
in_session = True

# Create stream socket and bind to server IP
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ('localhost', 10000)
server_socket.bind(server_address)
server_socket.listen(5)
print("Server socket created and listening for connections on localhost:10000\n")
print("listening...\n")

def image_handler(dest, connection):
    image = connection.recv(5000)
    bytes_rcvd = len(image)
    print(f"{bytes_rcvd} bytes sent")
    while (bytes_rcvd>=5000):
        print ("Receiving...")
        dest.send(image)
        image = connection.recv(5000)
        bytes_rcvd = len(image)
        print(f"{bytes_rcvd} bytes sent")
    dest.send(image)
    print ("Done Receiving")

def client_handler(connection, client_address):
    while True:
            try:
                message = connection.recv(5000)
                text = message.decode()
                print(f"{client_address}: {text}\n")
                # Login
                if text.startswith("^"):
                    # Extract username and password
                    client_name = text[1:text.index(':')].lower()
                    client_pwd = text[text.index(':')+1:]
                    # Store user
                    users[client_name] = connection
                    # Send login confirmation
                    connection.send(b"Logged in as " + client_name)
                    # Inform users that new user is online
                    broadcast((f"{client_name} is online.").encode())
                    print(f"{client_name} is online.")
                # Messaging    
                elif text.startswith("@"):
                    dest_client_name, chat = text[1:].split(":")
                    m = f"{client_name}:{chat}"
                    private(m.encode(), users[dest_client_name]) 
                # Images
                elif text.startswith("#"):
                    name, dest_client_name = text.split(":")
                    print(f"{client_name} wants to send image {name[1:]} to {dest_client_name}")
                    private(name.encode(), users[dest_client_name])
                    image_handler(users[dest_client_name], connection)
                else:
                    connections.remove(connection)
            except:
                continue
# Direct Message
def private(message, destination):
    try:
        destination.send(message)
    except:
        destination.close()
        connections.remove(destination)
# Broadcast Message
def broadcast(message, source):    
    for connection in connections:
        if connection!=source:
            try:
                connection.send(message)
            except:
                connection.close()
                connections.remove(connection)
while in_session:
    try:
        # Listen for and accept connections
        connection, client_address = server_socket.accept()
        connections.append(connection)
        connection.send(b"You are connected")
        print(f"{client_address} is connected.\n")
        
        # Start each new client connection as a thread
        start_new_thread(client_handler,(connection,client_address))  
    except:
        in_session = False
connection.close()        
server_socket.close()