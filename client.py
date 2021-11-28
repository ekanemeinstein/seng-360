import socket, select 
from sys import stdin, stdout
from _thread import *
from os import system
from PIL import Image

# Create stream socket and connect to server IP
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_address = ('localhost', 10000)
client_socket.connect(server_address)

server_message = client_socket.recv(2048)
print(server_message.decode())

print("Please enter your username:")
username = stdin.readline()
print("Please enter your password:")
password = stdin.readline()
login = f"^{username.strip()}:{password.strip()}"
client_socket.send(login.encode())
print("Send message to?")
dest_user = stdin.readline()

_ = system('clear')
print(f"Starting chat with {dest_user}\n\n")
# Incoming messages/images
def handle_incoming(client_socket):
    while True:
        try:
            server_message = client_socket.recv(5000)
            text = server_message.decode()
            if text.startswith("#"): receive_image(text[1:], client_socket)
            else: print(text)
        except:
            continue

def receive_image(name, socket):
    output = f"{name[:-4]}_out.{name[-3:]}"
    f = open(output,'wb')
    print ("-----Receiving image-----")
    image = socket.recv(5000)
    bytes_rcvd = len(image)
    while (bytes_rcvd>=5000):
        #print ("Receiving image...")
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
        client_socket.send(message.encode())        
        image_handler(chat[1:].strip())
    # Send Message
    else:
        message = f"@{dest_user.strip()}: {chat.strip()}"
        client_socket.send(message.encode())

client_socket.close()