import socket
import library.protocol_library_client

class Client:
  def __init__(self):
    # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.handshake = library.protocol_library_client.establish_connection(self.sock)

if __name__ == "__main__":
  client = Client()
  #send json to server and receive it
  library.protocol_library_client.send_recv_msg(client)
  #stop connection with server
  library.protocol_library_client.terminate_connection(client.sock)


  

