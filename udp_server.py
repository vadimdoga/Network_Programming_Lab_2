from library.protocol_library_server import establish_connection, recv_from_client_and_verify, socket_init
from library.protocol_library_crypto import generate_RSA_keys

class Server:
  def __init__(self):
    #initiate socket
    self.sock = socket_init()
    #generate rsa keys
    self.RSA_PUBLIC_KEY, self.RSA_PRIVATE_KEY = generate_RSA_keys()
    print("UDP server up and listening.")
    #handshake
    establish_connection(self.sock, self.RSA_PUBLIC_KEY)

  
if __name__ == "__main__":
  server = Server()
  #wait recv from client
  recv_from_client_and_verify(server, server.RSA_PRIVATE_KEY)

    