import socket
from _thread import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import a3DB
import sqlite3
import os
import sys

users = {}
connections = []
rooms = {}
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
    image = b""
    message = connection.recv(4096)
    print(len(message))
    chunk = decrypt_server_message(message)

    while chunk != b"--done":
        image = image + chunk
        message = connection.recv(4096)
        send_to_dest(chunk, dest)
        print(len(message))
        chunk = decrypt_server_message(message)

    message = encrypt_user_message(chunk,dest[1])
    send_to_dest(message, dest)
    return image

# Decrpt messages recieved from users
def decrypt_server_message(message):
    dcr_message = PKCS1_OAEP.new(keyPairServer).decrypt(message)
    return dcr_message

# Encrypt messages to send to other users
def encrypt_user_message(message, key):
    if isinstance(message, bytes):
        return PKCS1_OAEP.new(key).encrypt(message)
    else:
        return PKCS1_OAEP.new(key).encrypt(message.encode())

# Handle all messages recieved from the client
def client_handler(connection, client_address):
    user_pubKey= ""
    dest_client_name = ""
    my_name = ""
    current_chat_num = -1
    while True:
            #try:
            message = connection.recv(4096)
            text = decrypt_server_message(message)
            print(f"{client_address}: {text}\n")

            # Store encrypted message and send to destination
            if text.startswith(b"@"):
                enc_chat = text[1:]

                # Store in db
                a3DB.create(my_name, current_chat_num, enc_chat, interface)

                # Send to destination user
                send_to_dest(enc_chat,users[dest_client_name])
            # Register/Sign in user
            elif text.startswith(b"^"):
                text = text.decode()

                # Extract username and password
                operation = text[1:7]
                client_name = text[7:text.index(':')].lower()
                client_pwd = text[text.index(':')+1:text.index(';')]
                user_pubKey = RSA.importKey(text[text.index(';')+1:].encode())
                
                # For register, add the user to the database if they dont already exist
                # For sign in, check if the username and password match an entry in the db
                result = False
                if operation == "--regi":
                    result = a3DB.register(client_name, client_pwd, interface)
                else:
                    result = a3DB.signin(client_name, client_pwd, interface)
                
                # Respond to the client
                if result == True:
                    my_name = client_name
                    connection.send(encrypt_user_message("--success", user_pubKey))

                    users[client_name] = [connection, user_pubKey]
                else:
                    connection.send(encrypt_user_message("--failed", user_pubKey))
            # Share the dest_user_client public key if they are online
            elif text.startswith(b"~"):
                text = text.decode()
                dest_client_name = text[1:]

                # Respond to the client
                if dest_client_name in users:
                    connection.send(users[dest_client_name][1].export_key())
                else:
                    connection.send(encrypt_user_message("NA", user_pubKey))
            # Get list of users
            elif text.startswith(b"--find"):
                list = a3DB.find(my_name, interface)
                user_list = ",".join(list)

                # Respond to the client
                if user_list == "":
                    connection.send(encrypt_user_message("--none", user_pubKey))
                else:
                    connection.send(encrypt_user_message(user_list, user_pubKey))
            # Create new chatroom
            elif text.startswith(b"--newchat"):
                text = text.decode()
                dest_user = text[9:]
                result = a3DB.new_chat(my_name, dest_user, interface)

                # Respond to the client
                if result == -1:
                    connection.send(encrypt_user_message("--notfound", user_pubKey))
                    continue
                else:
                    chat_id = result
                    connection.send(encrypt_user_message("id: " + str(chat_id), user_pubKey))
                    message = connection.recv(4096)
                    chat_name = decrypt_server_message(message).decode()
                    a3DB.name_new_chat(chat_name,result, interface)
                    rooms[chat_id] = [my_name, dest_user]

            # View chat rooms
            elif text.startswith(b"--viewchats"):
                list = a3DB.view_chat(my_name, interface)
                chatrooms = "".join(list)

                # Respond to the client
                if chatrooms == "":
                    connection.send(encrypt_user_message("--none", user_pubKey))
                else:
                    connection.send(encrypt_user_message(chatrooms, user_pubKey))
            # Join chatroom
            elif text.startswith(b"--joinchat"):
                text = text.decode()
                chat_num = int(text[10:])
                res = a3DB.join_chat(my_name, chat_num, interface)

                # Respond to the client
                if res == False:
                    connection.send(encrypt_user_message("--failure", user_pubKey))
                else:
                    # Set the current destination
                    if rooms[chat_num][0] == my_name:
                        dest_client_name = rooms[chat_num][1]
                    else:
                        dest_client_name = rooms[chat_num][0]
                    current_chat_num = chat_num
                    connection.send(encrypt_user_message("--success" + dest_client_name, user_pubKey))
                    # Share the other dest user's public key
                    connection.send(users[dest_client_name][1].export_key())
            # Terminate the handle_incoming thread
            elif text.startswith(b"--return"):
                connection.send(encrypt_user_message("--exit", user_pubKey))
            # Delete my messages in the current chat
            elif text.startswith(b"--purge"):
                a3DB.purge(my_name, current_chat_num, interface)
            # Delete my account
            elif text.startswith(b"--delete"):
                a3DB.delete_acc(my_name, interface)
            # Handle image
            elif text.startswith(b"--image"):
                # Tell the dest to get ready to recieve the image
                message = encrypt_user_message(text,users[dest_client_name][1])
                send_to_dest(message, users[dest_client_name])
                
                # Recieve image
                image = image_handler(users[dest_client_name], connection)

                # Store in db
                a3DB.create(my_name, current_chat_num, image, interface)
            else:
                connections.remove(connection)
                del users[dest_client_name]
            #except Exception as e:
                #print(e)
                #continue
# Direct Message
def send_to_dest(message, destination):
    try:
        destination[0].send(message)
    except Exception as e:
        print(e)
        destination[0].close()
        connections.remove(destination)

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
