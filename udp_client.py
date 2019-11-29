import socket
from library.protocol_library_client import establish_connection, send_recv_msg, terminate_connection
from library.protocol_library_crypto import generate_AES_key

class Client:
  def __init__(self):
    #generate aes key
    self.AES_KEY = generate_AES_key()
    # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.handshake = establish_connection(self.sock, self.AES_KEY)

if __name__ == "__main__":
  client = Client()
  #send json to server and receive it
  send_recv_msg(client)
  #stop connection with server
  terminate_connection(client.sock)


  

