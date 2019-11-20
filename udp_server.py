import socket 
import pickle, hashlib
import protocol_library

local_ip = "127.0.0.1"
local_port = 8080
buffer_size = 30000
msg_from_server = b"hello from server"
ACK = 5320

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
  sock.bind((local_ip, local_port))
  print("UDP server up and listening.")

  while True:
    recv_from_client = sock.recvfrom(buffer_size)
    client_address = recv_from_client[1]
    server_header = recv_from_client[0]
    server_header = pickle.loads(server_header)
    print(server_header)
    server_header = protocol_library.Header(server_header['SYN'], ACK)
    server_header.change_SYN_with_ACK()
    server_header.increment_ACK()
    server_header = server_header.get_header_data()
    print(server_header)
    server_header = pickle.dumps(server_header)
    sock.sendto(server_header, client_address)

    recv_from_client = sock.recvfrom(buffer_size)
    server_header = recv_from_client[0]
    server_header = pickle.loads(server_header)
    if server_header['ACK'] == (ACK + 1):
      print("Connection established")

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


    