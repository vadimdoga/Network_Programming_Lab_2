import socket
import hashlib, json, pickle
import protocol_library

msg_from_client = "hello from client"
server_ip = "127.0.0.1"
server_port = 8080
server_address = (server_ip, server_port)
buffer_size = 30000
SYN = 4320
#create dict with msg and cheksum
# json_to_send = protocol_library.create_json(msg_from_client)
#udp connection
client_header = protocol_library.Header(SYN, None).get_header_data()
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
  # #send to server
  # sock.sendto(json_to_send, server_address)
  # #based on recv from server check if data is valid
  # recv_msg = protocol_library.client_verify_chksum(sock)
  # #print msg form server
  # msg_from_server = "Message from Server {}".format(recv_msg)
  # print(msg_from_server)
  client_header = pickle.dumps(client_header)
  sock.sendto(client_header, server_address)

  recv_from_server = sock.recvfrom(buffer_size)
  client_header = recv_from_server[0]
  client_header = pickle.loads(client_header)
  print(client_header)
  if client_header['ACK'] == (SYN + 1):
    print("Connection established")
    client_header = protocol_library.Header(client_header['SYN'], client_header['ACK'])
    client_header.change_SYN_with_ACK()
    client_header.increment_ACK()
    client_header = client_header.get_header_data()
    print(client_header)
    client_header = pickle.dumps(client_header)
    sock.sendto(client_header, server_address)
# class Client:
#   def __init__(self):
#     self.client_state = CLOSED
#     self.handshake()

  #def handshake:

  #def terminate

  #update state(closed, listening)
  #header with SYN,ACK

  #state
