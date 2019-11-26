import socket 
import library.protocol_library_server

local_ip = "127.0.0.1"
local_port = 8080
msg_from_server = b"Successful packet transmission"

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
  sock.bind((local_ip, local_port))
  print("UDP server up and listening.")

  library.protocol_library_server.server_establish_connection(sock)

  while True:
    #recv dict from client
    recv = library.protocol_library_server.server_receive(sock)
    if recv == 'fin':
      break
    else:
      #verify the cheksum
      #if chksm not valid retransmit
      library.protocol_library_server.server_verify_chksm(sock, msg_from_server, recv['msg'], recv['chksm'], recv['address'])
        


    