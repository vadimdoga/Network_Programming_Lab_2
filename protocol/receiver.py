from protocol.library.receiver.protocol_receiver import socket_init
from protocol.library.protocol_crypto import generate_RSA_keys
x = ' '

class Receiver:
  def __init__(self):
    #initiate socket
    self.sock = socket_init()
    #generate rsa keys
    self.RSA_PUBLIC_KEY, self.RSA_PRIVATE_KEY = generate_RSA_keys()
    
    print(x * 10 + "Server is up and listening.")



    