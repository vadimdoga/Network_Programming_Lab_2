import socket 
import library.protocol_library_server
from library.protocol_library_crypto import generate_RSA_keys
from library.protocol_header import Header
local_ip = "127.0.0.1"
local_port = 8080
RSA_PRIVATE_KEY = 0

class Server:
  def __init__(self):
    global RSA_PRIVATE_KEY

    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.bind((local_ip, local_port))
    #generate rsa keys
    self.RSA_PUBLIC_KEY, RSA_PRIVATE_KEY = generate_RSA_keys()
    print("UDP server up and listening.")
    #handshake
    library.protocol_library_server.establish_connection(self.sock, self.RSA_PUBLIC_KEY)

  
if __name__ == "__main__":
  server = Server()
  #wait recv from client
  library.protocol_library_server.wait_from_client(server)

    