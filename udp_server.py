import socket 

local_ip = "127.0.0.1"
local_port = 8080
buffer_size = 1024

msg_from_server = "hello from server"
bytes_to_send = str.encode(msg_from_server)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
  sock.bind((local_ip, local_port))
  print("UDP server up and listening.")

  while True:
    recv_from_client = sock.recvfrom(buffer_size)

    message = recv_from_client[0]
    address = recv_from_client[1]

    client_msg = "Message from Client:{}".format(message)
    client_ip  = "Client IP Address:{}".format(address)

    print(client_msg)
    print(client_ip)

    sock.sendto(bytes_to_send, address)