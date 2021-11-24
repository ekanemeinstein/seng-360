import socket, select 
from sys import stdin, stdout
from _thread import *
from os import system

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
def handle_incoming(client_socket):
    while True:
        try:
            server_message = client_socket.recv(2048)
            print(server_message.decode())
        except:
            continue

start_new_thread(handle_incoming, (client_socket,))        
while True:
    chat = stdin.readline()
    if (chat[:4] == 'exit'):
        print("Logging out...")
        break
    else:
        message = f"@{dest_user.strip()}: {chat.strip()}"
        client_socket.send(message.encode())

client_socket.close()