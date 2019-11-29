from library.protocol_library_server import establish_connection, wait_from_client
from library.protocol_library_crypto import generate_RSA_keys
from library.protocol_header import Header
import socket 

SERVER_ADDRESS = ("127.0.0.1", 8080)

class Server:
  def __init__(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.bind(SERVER_ADDRESS)
    #generate rsa keys
    self.RSA_PUBLIC_KEY, self.RSA_PRIVATE_KEY = generate_RSA_keys()
    print("UDP server up and listening.")
    #handshake
    establish_connection(self.sock, self.RSA_PUBLIC_KEY, self.RSA_PRIVATE_KEY)

  
if __name__ == "__main__":
  server = Server()
  #wait recv from client
  wait_from_client(server)

    