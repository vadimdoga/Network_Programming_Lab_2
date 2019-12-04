from library.receiver.protocol_receiver import recv_from_sender_and_verify, socket_init
from library.receiver.protocol_receiver_header import establish_connection
from library.protocol_crypto import generate_RSA_keys

class Receiver:
  def __init__(self):
    #initiate socket
    self.sock = socket_init()
    #generate rsa keys
    self.RSA_PUBLIC_KEY, self.RSA_PRIVATE_KEY = generate_RSA_keys()
    print("Server is up and listening.")
    #handshake
    establish_connection(self.sock, self.RSA_PUBLIC_KEY)

  
if __name__ == "__main__":
  receiver = Receiver()
  #wait recv from client
  recv_from_sender_and_verify(receiver, receiver.RSA_PRIVATE_KEY)

    