import socket
from sys import stdin
import threading
from os import system
from PIL import Image
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from time import sleep

# Create stream socket and connect to server IP
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_address = ('localhost', 10000)
client_socket.connect(server_address)
server_message = client_socket.recv(4096)
print("Connected")

# Generate my public and private keys
my_key_pair = RSA.generate(1024)
my_pub_key = my_key_pair.publickey()

# Get server public key and define functions to encrypt/decrypt server messages
server_pubKey = RSA.importKey(server_message)
print("Server public key recieved")

# Destination user public key
dest_user = ""
dest_user_pubKey = None

# current chat room
current_chat_room = ""

# Encrypt a message to send to the server
def encrypt_server_message(message):
    if isinstance(message, bytes):
        return PKCS1_OAEP.new(server_pubKey).encrypt(message)
    else:
        return PKCS1_OAEP.new(server_pubKey).encrypt(message.encode())

# Decrypt a message recieved
def decrypt_my_message(message):
    dcr_message = PKCS1_OAEP.new(my_key_pair).decrypt(message)
    return dcr_message

# Encrypt a message to send to another user
def encrypt_user_message(message):
    if isinstance(message, bytes):
        return PKCS1_OAEP.new(dest_user_pubKey).encrypt(message)
    else:
        return PKCS1_OAEP.new(dest_user_pubKey).encrypt(message.encode())

# Incoming messages/images
def handle_incoming(client_socket):
    while True:
        try:
            server_message = client_socket.recv(4096)
            dcr_message = decrypt_my_message(server_message)
            # Handle incoming images
            if dcr_message.startswith(b"--image"):
                recieve_image(server_message[7:].decode(), client_socket)
            # Handle text
            else:
                dcr_message = decrypt_my_message(server_message).decode()
                if dcr_message == "--exit":
                    return
                else:
                    print(f"{dest_user}: {dcr_message}".rstrip())
        except:
           continue

def recieve_image(name, socket):
    #output = f"{name[:-4]}_out.{name[-3:]}"
    f = open("mort_2.png",'wb')
    print ("-----Receiving image-----")
    message = socket.recv(4096)
    chunk = decrypt_my_message(message)

    while chunk != b"--done":
        f.write(chunk.decode())
        message = socket.recv(4096)
        chunk = decrypt_my_message(message)
 
    f.close()
    print (f"-----Image saved as mort_2.png-----")
    with open("mort_2.png", 'rb') as f:
        im = Image.open(f)
        im.show()

# Send Image
def image_sender(image):
    f = open(image,'rb')
    print(f"-----uploading {image}-----")
    chunk = f.read(50)
    while (chunk):
        sleep(0.05)
        enc_chunk = encrypt_user_message(chunk)
        message = encrypt_server_message(enc_chunk)
        print("chunk sent")
        client_socket.send(message)
        chunk = f.read(50)
    f.close()
    client_socket.send(encrypt_server_message("--done"))
    print (f"-----uploaded {image}-----")

# Sign in/Register
def signin():
    try:
        while True:
            print("[R]egister, [S]ign in, [E]xit\n")
            mode = username = stdin.readline().strip()
            if mode != 'R' and mode != 'S':
                print("Invalid input, try again")
                continue

            print("Please enter your username:")
            username = stdin.readline().strip()
            print("Please enter your password:")
            password = stdin.readline().strip()

            if mode == 'R':
                login = f"^--regi{username}:{password};{my_pub_key.export_key().decode()}"
            elif mode == 'S':
                login = f"^--sign{username}:{password};{my_pub_key.export_key().decode()}"

            enc_login = encrypt_server_message(login.encode())
            client_socket.send(enc_login)
            server_message = client_socket.recv(4096)
            dcr_message = decrypt_my_message(server_message).decode()
            if dcr_message == "--failed":
                if mode == 'R':
                    print("Registration failed")
                else:
                    print("Sign in failed")
            else:
                print("Success")
                break
    except:
        client_socket.close()
        exit

# Get a list of users that can be messaged
def find():
    message = b"--find"
    enc_message = encrypt_server_message(message)
    client_socket.send(enc_message)

    server_message = client_socket.recv(4096)
    dcr_server_message = decrypt_my_message(server_message).decode()
    if dcr_server_message == "--none":
        print("There are no users to message")
    else:
        if dcr_server_message.startswith(","):
            print("Users available: " + dcr_server_message[1:])
        else:
            print("Users available: " + dcr_server_message)
    return

# Create a new chat room
def new_chat():
    # Get desired destination user and send to server
    LIST_NAME=input("Who would you like to add to the chatroom?\n")
    message = b"--newchat" + LIST_NAME.encode()
    enc_message = encrypt_server_message(message)
    client_socket.send(enc_message)

    server_message = client_socket.recv(4096)
    dcr_server_message = decrypt_my_message(server_message).decode()

    # Notify the user if the room was created or not
    if dcr_server_message == "--notfound":
        print("User not found")
    else:
        chat_id = dcr_server_message
        CHAT_NAME=input("What would you like to name the chatroom?\n")
        message = CHAT_NAME.encode()
        enc_message = encrypt_server_message(message)
        client_socket.send(enc_message)
        print("Chatroom created, you can join it with the Join command using chat " + chat_id)
    return

# Displays a list of chats the current user is able to join
def view_chat():
    message = b"--viewchats"
    enc_message = encrypt_server_message(message)
    client_socket.send(enc_message)

    server_message = client_socket.recv(4096)
    dcr_server_message = decrypt_my_message(server_message).decode()
    if dcr_server_message == "--none":
        print("There are no chat rooms for you to join, try creating one")
    else:
        print("Rooms available to join: \n" + dcr_server_message)
    return

# Manages the chat mode
def chat_mode():
    print("@ to send message, # to send an image, [P]urge, [R]eturn")
    # Start thread to handle incoming messages
    t = threading.Thread(target=handle_incoming, args = (client_socket,))
    t.start()
    
    # Handle user input
    while True:
        chat = stdin.readline().strip()
        # Handle chat inputs
        if chat.startswith("@"):
            enc_chat = encrypt_user_message(chat[1:])
            message = b"@" + enc_chat
            client_socket.send(encrypt_server_message(message))
        # Send Image
        elif chat.startswith("#"):
            client_socket.send(encrypt_server_message("--image" + chat[1:]))
            image_sender(chat[1:].strip())
        # Send Message
        elif chat == 'R':
            client_socket.send(encrypt_server_message("--return"))
            break
        elif chat == 'P':
            client_socket.send(encrypt_server_message("--purge"))
            _ = system('clear')
            print("Messages from this room have been purged")
        else:
            print("Invalid input")
    print("Returning to main menu")

def join_chat():
    # Send a message to the server requesting to join a chat room
    CHAT_NUM=input("Enter the ID of the Chatroom you wish to join\n")
    current_chat_room = CHAT_NUM
    message = "--joinchat" + str(CHAT_NUM)
    enc_message = encrypt_server_message(message.encode())
    client_socket.send(enc_message)

    # Recieve message from server
    server_message = client_socket.recv(4096)
    dcr_server_message = decrypt_my_message(server_message)

    if dcr_server_message == b"--failure":
        print("Room could not be found or you dont have permission to join it")
    else:
        global dest_user_pubKey
        global dest_user
        dcr_server_message = dcr_server_message.decode()
        dest_user = dcr_server_message[9:]
        server_message = client_socket.recv(4096)
        dest_user_pubKey = RSA.importKey(server_message)
        print("Joining " + str(current_chat_room))
        chat_mode()

def mode_console():
    userin=input("[F]ind, [N]ew, [V]iew, [J]oin, [D]elete Account, [R]eturn\n")
    if userin== 'F':
        find()
    elif userin== 'N':
        new_chat()
    elif userin== 'V':
        view_chat()
    elif userin== 'J':
        join_chat()
    elif userin=='R':
        print("Signing out") ##aka going back
        signin()
    elif userin=='D':
        print("Deleting your account")
        client_socket.send(encrypt_server_message("--delete"))
        signin()
    elif userin== 'help':
        print("[F]ind displays all users\n[N]ew allows you to create a new chatroom\n[V]iew show all the chatrooms you are in\n[J]oin lets you join a chatroom you're a member of\n[D]elete allows you to delete your account\n[R]eturn signs you out")
    else:
        print("Command not recognized, make sure it is capitalized, or try \"help\"")

_ = system('clear')

# Start code execution
signin()
while True:
    mode_console()

client_socket.close()