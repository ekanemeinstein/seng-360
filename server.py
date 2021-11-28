import socket, select
from _thread import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import binascii

users = {}
connections = []
in_session = True

# Create server public/private keys
keyPairServer = RSA.generate(3072)
server_pubKey = keyPairServer.publickey()

# Create stream socket and bind to server IP
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ('localhost', 10000)
server_socket.bind(server_address)
server_socket.listen(5)
print("Server socket created and listening for connections on localhost:10000\n")
print("listening...\n")

def decrypt_server_message(message):
    dcr_message = PKCS1_OAEP.new(keyPairServer).decrypt(message)
    return dcr_message

def encrypt_user_message(message, key):
    enc_message = PKCS1_OAEP.new(key).encrypt(message.encode())
    return enc_message

def client_handler(connection, client_address):
    user_pubKey= ""
    while True:
            try:
                message = connection.recv(4096)
                text = decrypt_server_message(message)
                #print(f"{client_address}: {text}\n")

                if text.startswith(b"@"):
                    dest_client_name = text[1:text.index(b':')].decode()
                    enc_chat = text[text.index(b':')+2:]
                    private(enc_chat,users[dest_client_name])

                elif text.startswith(b"^"):
                    text = text.decode()
                    # Extract username and password
                    client_name = text[1:text.index(':')].lower()
                    client_pwd = text[text.index(':')+1:text.index(';')]
                    user_pubKey = RSA.importKey(text[text.index(';')+1:].encode())
                    # Store user
                    # TODO: Do user auth here and store in db if authenticated
                    users[client_name] = [connection, user_pubKey]

                    # Send login confirmation
                    #connection.send(b"Logged in as " + client_name.encode())

                    # Inform users that new user is online
                    # broadcast((f"{client_name} is online.").encode())
                    # print(f"{client_name} is online.")

                # Share the dest_user_client public key if they exist
                elif text.startswith(b"~"):
                    text = text.decode()
                    dest_client_name = text[1:]
                    if dest_client_name in users:
                        connection.send(users[dest_client_name][1].export_key())
                    else:
                        connection.send(encrypt_user_message("NA", user_pubKey))

                else:
                    print("Closing conn")
                    connections.remove(connection)
            except:
                print("continuing")
                continue

def private(message, destination):
    try:
        destination[0].send(message)
    except:
        destination[0].close()
        connections.remove(destination)

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
        #Listen for and accept connections
        connection, client_address = server_socket.accept()
        connections.append(connection)
        connection.send(server_pubKey.export_key())
        print(f"{client_address} is connected.\n")
        
        start_new_thread(client_handler,(connection,client_address))  
    except:
        in_session = False

connection.close()
server_socket.close()