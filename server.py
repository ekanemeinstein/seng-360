import socket, select
from _thread import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import binascii
import a3DB
import sqlite3
import getpass
import os
import sys

users = {}
connections = []
in_session = True

# Create server public/private keys
print("Generating Keys")
keyPairServer = RSA.generate(3072)
server_pubKey = keyPairServer.publickey()

# Set up database
# Change this to create a new database with a new name automatically
print("Setup DB")
dbname='test.db'
interface = None
not_setup= not os.path.exists(dbname)
try:
	interface = sqlite3.connect(dbname, check_same_thread=False)

	if not_setup:
		print("First time setup for database starting")
		interface.execute('''
		CREATE TABLE `accounts` (
			`username` TEXT NOT NULL,
			`password` TEXT NOT NULL,
			PRIMARY KEY (username)
		);
		''')
		interface.execute('''
		CREATE TABLE `chatroom` (
			`username` TEXT NOT NULL,
			`num` INTEGER NOT NULL
		);
		''')
		interface.execute('''
		CREATE TABLE `chatnames` (
			`num` INTEGER NOT NULL,
			`name` TEXT NOT NULL,
			PRIMARY KEY (name)
		);
		''')
		interface.execute('''
		CREATE TABLE `message` (
			`num` INTEGER NOT NULL,
			`indexnum` INTEGER NOT NULL,
			`content` TEXT NOT NULL, --filepath
			`username` TEXT NOT NULL,
			CONSTRAINT PK_message PRIMARY KEY (num, indexnum)
		);
		''')
		print("Setup Complete")
	else:
		print("Database found")

	print("Opening Server for Connections")
	#print("Enter \"help\" at any time to display available commands, or \"exit\" to shut down the program")

except sqlite3.Error as e:
    print(f"Error {e.args[0]}")
    sys.exit(1)

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
    # print(f"{bytes_rcvd} bytes sent")
    while (bytes_rcvd>=5000):
        # print ("Receiving...")
        dest.send(image)
        image = connection.recv(5000)
        bytes_rcvd = len(image)
        # print(f"{bytes_rcvd} bytes sent")
    dest.send(image)
    # print ("Done Receiving")

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
                print(f"{client_address}: {text}\n")
    
                # Store encrypted message and send to destination
                if text.startswith(b"@"):
                    dest_client_name = text[1:text.index(b':')].decode()
                    enc_chat = text[text.index(b':')+2:]
                    private(enc_chat,users[dest_client_name])
                # Register/Sign in user
                elif text.startswith(b"^"):
                    text = text.decode()

                    # Extract username and password
                    operation = text[1:7]
                    client_name = text[7:text.index(':')].lower()
                    client_pwd = text[text.index(':')+1:text.index(';')]
                    user_pubKey = RSA.importKey(text[text.index(';')+1:].encode())

                    result = False
                    if operation == "--regi":
                        result = a3DB.register(client_name, client_pwd, interface)
                    else:
                        result = a3DB.signin(client_name, client_pwd, interface)
                    
                    if result == True:
                        connection.send(encrypt_user_message("--success", user_pubKey))
                        print("Sending --success")
                    else:
                        print("Sending --failed")
                        connection.send(encrypt_user_message("--failed", user_pubKey))

                # Share the dest_user_client public key if they exist
                elif text.startswith(b"~"):
                    text = text.decode()
                    dest_client_name = text[1:]
                    if dest_client_name in users:
                        connection.send(users[dest_client_name][1].export_key())
                    else:
                        connection.send(encrypt_user_message("NA", user_pubKey))
                # Images
                elif text.startswith(b"#"):
                    text = text.decode()
                    name, dest_client_name = text.split(":")
                    print(f"{client_name} wants to send image {name[1:]} to {dest_client_name}")
                    private(name.encode(), users[dest_client_name])
                    image_handler(users[dest_client_name][0], connection)

                else:
                    print("Closing conn")
                    connections.remove(connection)
            except Exception as e:
                print(e)
                continue
# Direct Message
def private(message, destination):
    try:
        destination[0].send(message)
    except Exception as e:
        print(e)
        destination[0].close()
        connections.remove(destination)

# Broadcast Message
def broadcast(message, source):    
    for connection in connections:
        if connection!=source:
            try:
                connection.send(message)
            except Exception as e:
                print(e)
                connection.close()
                connections.remove(connection)

while in_session:
    try:
        #Listen for and accept connections
        connection, client_address = server_socket.accept()
        connections.append(connection)
        connection.send(server_pubKey.export_key())
        print(f"{client_address} is connected.\n")
        
        # Start each new client connection as a thread
        start_new_thread(client_handler,(connection,client_address))  
    except Exception as e:
        print(e)
        in_session = False

print("Closing")
interface.close()
connection.close()
server_socket.close()