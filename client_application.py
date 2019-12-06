from protocol.sender import Sender
from protocol.library.sender.protocol_sender import send_recv_msg, terminate_receiver_connection, terminate_sender_connection

MSG_FROM_SENDER = "hello from sender"
i = 0

if __name__ == "__main__":
  #send json to server and receive it
  while True:
    val = input("$>")
    if val == "connect":
      sender = Sender() 
    elif val == "send":
      # todo: need to change this method to send to single person
      send_recv_msg(sender, MSG_FROM_SENDER)
    elif val == "broadcast":
      print("broadcast")
      # todo: need to add broadcast method to protocol which sends msg to all connected clients
    elif val == "stop":
      #stop connection with server
      terminate_sender_connection(sender.sock)
    elif val == "stop server":
      # todo: when someone send stop server, server must broadcast that it stopped
      terminate_receiver_connection(sender.sock)
    else:
      print('This command does not exist!')