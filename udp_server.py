import socket 
import pickle, hashlib
import protocol_library

local_ip = "127.0.0.1"
local_port = 8080
buffer_size = 30000
msg_from_server = b"hello from server"

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
  sock.bind((local_ip, local_port))
  print("UDP server up and listening.")

  protocol_library.establish_connection(sock)

  # while True:
    

    # #recv dict from client
    # recv = protocol_library.recv_from_client(sock)
    # #verify the cheksum
    # verify_chksm = protocol_library.server_verify_chksm(sock, msg_from_server, recv['msg'], recv['chksm'], recv['address'])
      
    # client_ip  = "Client IP Address:{}".format(recv['address'])
    # client_msg = "Message from Client:{}".format(recv['msg'])

    # print(client_msg)
    # print(client_ip)

    # if verify_chksm:
    #   break



    