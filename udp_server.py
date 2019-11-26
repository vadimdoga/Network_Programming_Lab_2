import socket 
import library.protocol_library_server

local_ip = "127.0.0.1"
local_port = 8080
<<<<<<< HEAD
msg_from_server = b"Successful packet transmission"

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
  sock.bind((local_ip, local_port))
  print("UDP server up and listening.")

  protocol_library.establish_connection(sock)

  while True:
    
    #recv dict from client
    recv = protocol_library.recv_from_client(sock)
    #verify the cheksum
    verify_chksm = protocol_library.server_verify_chksm(sock, msg_from_server, recv['msg'], recv['chksm'], recv['address'])
      
    if verify_chksm:
      print("Message from Client: ", recv['msg'])
      break

=======
>>>>>>> dev

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

    