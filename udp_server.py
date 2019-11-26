import socket 
import library.protocol_library_server

local_ip = "127.0.0.1"
local_port = 8080

class Server:
  def __init__(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.bind((local_ip, local_port))
    print("UDP server up and listening.")
    #handshake
    library.protocol_library_server.establish_connection(self.sock)

  
if __name__ == "__main__":
  server = Server()
  #wait recv from client
  library.protocol_library_server.wait_from_client(server)
