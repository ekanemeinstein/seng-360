import socket, select 
from sys import stdin, stdout
from _thread import *
from os import system
from PIL import Image
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import binascii

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
dest_user_pubKey = ""

def encrypt_server_message(message):
    enc_message = PKCS1_OAEP.new(server_pubKey).encrypt(message)
    return enc_message

def decrypt_my_message(message):
    dcr_message = PKCS1_OAEP.new(my_key_pair).decrypt(message)
    return dcr_message

def encrypt_user_message(message):
    enc_message = PKCS1_OAEP.new(dest_user_pubKey).encrypt(message.encode())
    return enc_message


print("Please enter your username:")
username = stdin.readline().strip()
print("Please enter your password:")
password = stdin.readline().strip()

login = f"^{username}:{password};{my_pub_key.export_key().decode()}"
enc_login = encrypt_server_message(login.encode())
client_socket.send(enc_login)

# TODO: Setup handle auth here


# Start session with another user
dest_user = ""
while True:
    try:
        print("Send message to?")
        dest_user = stdin.readline().strip()
        message = f"~{dest_user}"
        client_socket.send(encrypt_server_message(message.encode()))
        message_from_server = client_socket.recv(4096)
        if message_from_server.startswith(b'-----'):
            dest_user_pubKey = RSA.importKey(message_from_server)
            break
        else:
            print("User does not exist or is not online, try again")
            continue
    except:
        client_socket.close()
        # continue

_ = system('clear')
print(f"Starting chat with {dest_user}\n")
# Incoming messages/images
def handle_incoming(client_socket):
    while True:
        try:
            server_message = client_socket.recv(4096)
            if server_message.startswith(b"#"): receive_image(server_message[1:].decode(), client_socket)
            else: 
                dcr_message = decrypt_my_message(server_message).decode()
                print(f"{dest_user}: {dcr_message}".rstrip())
        except:
           continue

def receive_image(name, socket):
    output = f"{name[:-4]}_out.{name[-3:]}"
    f = open(output,'wb')
    print ("-----Receiving image-----")
    image = socket.recv(5000)
    bytes_rcvd = len(image)
    # print(f"{bytes_rcvd} bytes sent")
    while (bytes_rcvd>=5000):
        # print ("Receiving image...")
        f.write(image)
        image = socket.recv(5000)
        bytes_rcvd = len(image)
        #print(f"{bytes_rcvd} bytes sent")
    f.write(image)    
    f.close()
    print (f"-----Image saved as {output}-----")
    with open(output, 'rb') as f:
        im = Image.open(f)
        im.show()

# Send Image
def image_handler(image):
    f = open(image,'rb')
    print(f"-----uploading {image}-----")
    message = f.read(5000)
    while (message):
        client_socket.send(message)
        message = f.read(5000)
    f.close()
    print (f"-----uploaded {image}-----")     

# Handle incoming messages as separate thread
start_new_thread(handle_incoming, (client_socket,))        

# Client commands/outgoing messages
while True:
    chat = stdin.readline()
    # Abort session
    if (chat[:4] == 'exit'):
        print("Logging out...")
        break
    # Upload Image
    elif (chat.startswith("#")):
        message = f"{chat.strip()}:{dest_user.strip()}"
        client_socket.send(encrypt_server_message(message.encode()))        
        image_handler(chat[1:].strip())
    # Send Message
    else:
        enc_chat = encrypt_user_message(chat)
        message = b"@" + dest_user.strip().encode() + b": " + enc_chat
        client_socket.send(encrypt_server_message(message))

client_socket.close()