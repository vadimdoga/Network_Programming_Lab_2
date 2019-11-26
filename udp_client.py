import socket
import library.protocol_library_client

<<<<<<< HEAD
msg_from_client = "hello from client"
#create dict with msg and cheksum
json_to_send = protocol_library.create_json(msg_from_client)
#udp connection
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
  handshake = protocol_library.handshake(sock)
  if handshake:
    #send to server
    sock.sendto(json_to_send, protocol_library.server_address)
    #based on recv from server check if data is valid
    recv_msg = protocol_library.client_verify_chksum(sock)
    #print msg form server
    print("Message from Server: ", recv_msg)
  

=======
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


  

>>>>>>> dev
