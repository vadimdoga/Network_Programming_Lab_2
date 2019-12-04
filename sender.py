from library.sender.protocol_sender import send_recv_msg, terminate_connection, socket_init
from library.sender.protocol_sender_header import establish_connection
from library.protocol_crypto import generate_AES_key

MSG_FROM_SENDER = "hello from sender"
# MSG_FROM_SENDER = "sdasdjadfkasdashdjasdJASDNosajshfASJDsdoADSoajsdOADHOahdoihwdoaehfjkasdkjashdkjashdkjahdkjhaskdjhkasjhdkajsdkjaskjdaskjdhkajshdkajsdhkjashdkahakjsdhkassa,dnbaskdbkhaskhasdkassdadasdadaadasasaasdasdasmasdasdasdaasdas"

class Sender:
  def __init__(self):
    #initiate socket
    self.sock = socket_init()
    #generate aes key
    self.AES_KEY = generate_AES_key()
    # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    self.handshake = establish_connection(self.sock, self.AES_KEY)

if __name__ == "__main__":
  sender = Sender()
  #send json to server and receive it
  send_recv_msg(sender, MSG_FROM_SENDER)
  #stop connection with server
  terminate_connection(sender.sock)


  

