from protocol.sender import Sender
from protocol.library.sender.protocol_sender import send_recv_msg, terminate_connection

MSG_FROM_SENDER = "hello from sender"

if __name__ == "__main__":
  sender = Sender()
  #send json to server and receive it
  send_recv_msg(sender, MSG_FROM_SENDER)
  #stop connection with server
  terminate_connection(sender.sock)