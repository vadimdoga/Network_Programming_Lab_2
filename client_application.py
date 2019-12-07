from protocol.sender import Sender
from protocol.library.sender.protocol_sender import get_connected_clients, recv_msg, send_msg, terminate_receiver_connection, terminate_sender_connection
from threading import Thread
import os
x = " "
def main_menu():
  while True:
    conn_val = input("$>")
    if conn_val == "connect":
      sender = Sender()
      msg_thread = Thread(target=recv_msg, args=(sender,))
      msg_thread.start()
      while True: 
        val = input(x * 15)
        if val == "send":
          PORT = int(input(x * 15 + "PORT: "))
          msg = input(x * 15 + "MESSAGE: ")
          send_msg(sender, msg, 'send', PORT)
        elif val == "broadcast":
          msg = input(x * 15 + "MESSAGE: ")
          send_msg(sender, msg, 'broadcast', '')
        elif val == "stop":
          #stop client connection with server
          terminate_sender_connection(sender.sock)
          break
        elif val == "stop server":
          #close server
          terminate_receiver_connection(sender.sock)
          break
        elif val == "clients":
          get_connected_clients(sender.sock)
        elif val == "exit":
          terminate_sender_connection(sender.sock)
          os._exit(0)
        else:
          print(x * 15 + 'This command does not exist!')
    elif (conn_val == "send" or conn_val == "broadcast" or conn_val == "stop" or conn_val == "stop server"):
      print(x * 15 + 'You need to type `connect` first!')
    else:
      print(x * 15 + 'This command does not exist!')


if __name__ == "__main__":
  Thread(target=main_menu).start()
  # get_always_msg()
  # main_menu()