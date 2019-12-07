from protocol.sender import Sender
from protocol.library.sender.protocol_sender import recv_msg, send_msg, terminate_receiver_connection, terminate_sender_connection
from threading import Thread
import os
def main_menu():
  while True:
    conn_val = input("$>")
    if conn_val == "connect":
      sender = Sender()
      msg_thread = Thread(target=recv_msg, args=(sender,))
      msg_thread.start()
      while True: 
        val = input("$>")
        if val == "send":
          # todo: need to change this method to send to single person
          msg = input("MESSAGE: ")
          send_msg(sender, msg)
        elif val == "broadcast":
          print("broadcast")
          # todo: need to add broadcast method to protocol which sends msg to all connected clients
        elif val == "stop":
          #stop client connection with server
          terminate_sender_connection(sender.sock)
          break
        elif val == "stop server":
          #close server
          terminate_receiver_connection(sender.sock)
          break
        elif val == "exit":
          terminate_sender_connection(sender.sock)
          os._exit(0)
        else:
          print('This command does not exist!')
    elif (conn_val == "send" or conn_val == "broadcast" or conn_val == "stop" or conn_val == "stop server"):
      print('You need to type `connect` first!')
    else:
      print('This command does not exist!')


if __name__ == "__main__":
  Thread(target=main_menu).start()
  # get_always_msg()
  # main_menu()