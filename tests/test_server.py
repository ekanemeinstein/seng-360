import socket
import os
import sqlite3

# Create stream socket and connect to server IP
server_address = ('localhost', 10000)
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
status = client_socket.connect(server_address)
server_message = client_socket.recv(4096)

def test_socket_connection():
    assert client_socket.getpeername()[0] == '127.0.0.1'
    assert client_socket.getpeername()[1] == 10000
    assert client_socket.type.name == "SOCK_STREAM"

def test_recv_public_key():
    print (client_socket, server_message.decode(), status)
    client_socket.close()
    assert server_message.decode()[:26] == "-----BEGIN PUBLIC KEY-----", "not a pk"
    assert server_message.decode()[-24:] == "-----END PUBLIC KEY-----", "not a pk"

def test_db_created():
    assert os.path.isfile('./test.db') == True

def test_db_tables():
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    query = "select name from sqlite_master where type='table';"
    cursor.execute(query)
    tables = cursor.fetchall()
    assert tables[0][0] == "accounts"
    assert tables[1][0] == "chatroom"
    assert tables[2][0] == "chatnames"
    assert tables[3][0] == "message"
