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

# Encrypt the message contents with the public key of the reciever
encrypted_sender_reciever = PKCS1_OAEP.new(keyPairServer.publickey()).encrypt(sender_reciever)

# Encrypt the sender/reciever with the public key of the server
encrypted_message = PKCS1_OAEP.new(keyPairReciever.publickey()).encrypt(message)

# Here we would send both encrypted messages to the server
print("Encrypted sender/reciver:", binascii.hexlify(encrypted_sender_reciever))
print("Encrypted message:", binascii.hexlify(encrypted_message))

### Server
# Decrypt the sender/reciever with the server private key
decrypted_sender_reciver = PKCS1_OAEP.new(keyPairServer).decrypt(encrypted_sender_reciever)
print("Decrypted sender/reciever:", decrypted_sender_reciver)

# Here we would store the encrypted message in the database and send the message to the reciever

### Reciever
# Decrypt the message with the reciever private key
decrypted_message = PKCS1_OAEP.new(keyPairReciever).decrypt(encrypted_message)
print("Decrypted message:", decrypted_message)


# Testing multiple encryptions
keyPair1 = RSA.generate(1024)
keyPair2 = RSA.generate(3072)

message1 = "sender message"
enc_message1 = PKCS1_OAEP.new(keyPair1.publickey()).encrypt(message1.encode())
message2 = b"destination: " + enc_message1
enc_message2 = PKCS1_OAEP.new(keyPair2.publickey()).encrypt(message2)
dcr_message2 = PKCS1_OAEP.new(keyPair2).decrypt(enc_message2)
print(dcr_message2)
enc_message1 = dcr_message2[dcr_message2.index(b':')+2:]
print(enc_message1)
dcr_message1 = PKCS1_OAEP.new(keyPair1).decrypt(enc_message1)
print(dcr_message1)