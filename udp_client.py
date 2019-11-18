import socket

msg_from_client = "hello from client"
bytes_to_send = str.encode(msg_from_client)
server_ip = "127.0.0.1"
server_port = 8080
server_address = (server_ip, server_port)
buffer_size = 1024

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
  sock.sendto(bytes_to_send, server_address)

  msg_from_server = sock.recvfrom(buffer_size)

  msg = "Message from Server {}".format(msg_from_server[0])
  print(msg)