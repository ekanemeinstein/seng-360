# Based on https://cryptobook.nakov.com/asymmetric-key-ciphers/rsa-encrypt-decrypt-examples
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import binascii


#keyPairSender = RSA.generate(1024)
keyPairServer = RSA.generate(1024)
keyPairReciever = RSA.generate(1024)

### Sender
sender_reciever = b"Client 1 -> Client 2"
message = b"Test message, hello there"
# encrypted_sender_reciever = ""
# encrypted_message = ""

def test_server_encryption():
    # Encrypt the message contents with the public key of the reciever
    encrypted_sender_reciever = PKCS1_OAEP.new(keyPairServer.publickey()).encrypt(sender_reciever)
    assert len(encrypted_sender_reciever) == 128

def test_recv_encryption():
    # Encrypt the sender/reciever with the public key of the server
    encrypted_message = PKCS1_OAEP.new(keyPairReciever.publickey()).encrypt(message)
    assert len(encrypted_message) == 128


# Here we would send both encrypted messages to the server

def test_server_decryption():
    ### Server
    # Decrypt the sender/reciever with the server private key
    encrypted_sender_reciever = PKCS1_OAEP.new(keyPairServer.publickey()).encrypt(sender_reciever)
    decrypted_sender_reciver = PKCS1_OAEP.new(keyPairServer).decrypt(encrypted_sender_reciever)
    assert decrypted_sender_reciver == sender_reciever

# Here we would store the encrypted message in the database and send the message to the reciever

def test_recv_decryption():
    ### Reciever
    # Decrypt the message with the reciever private key
    encrypted_message = PKCS1_OAEP.new(keyPairReciever.publickey()).encrypt(message)
    decrypted_message = PKCS1_OAEP.new(keyPairReciever).decrypt(encrypted_message)
    assert decrypted_message == message

def test_multi_encryption():
    # Testing multiple encryptions
    keyPair1 = RSA.generate(1024)
    keyPair2 = RSA.generate(3072)

    message1 = "sender message"
    enc_message1 = PKCS1_OAEP.new(keyPair1.publickey()).encrypt(message1.encode())
    message2 = b"destination: " + enc_message1
    enc_message2 = PKCS1_OAEP.new(keyPair2.publickey()).encrypt(message2)
    dcr_message2 = PKCS1_OAEP.new(keyPair2).decrypt(enc_message2)
    assert dcr_message2 == message2
    enc_message1 = dcr_message2[dcr_message2.index(b':')+2:]
    dcr_message1 = PKCS1_OAEP.new(keyPair1).decrypt(enc_message1)
    assert dcr_message1 == message1.encode()
    