from protocol.library.sender.protocol_sender import socket_init
from protocol.library.sender.protocol_sender_header import establish_connection
from protocol.library.protocol_crypto import generate_AES_key

class Sender:
  def __init__(self):
    #initiate socket
    self.sock = socket_init()
    #generate aes key
    self.AES_KEY = generate_AES_key()
    # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    self.handshake = establish_connection(self.sock, self.AES_KEY)



  

