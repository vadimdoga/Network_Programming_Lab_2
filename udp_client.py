import socket
import hashlib, json, pickle
import protocol_library

msg_from_client = "hello from client"
server_ip = "127.0.0.1"
server_port = 8080
server_address = (server_ip, server_port)
#create dict with msg and cheksum
json_to_send = protocol_library.create_json(msg_from_client)
#udp connection
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
  #send to server
  sock.sendto(json_to_send, server_address)
  #based on recv from server check if data is valid
  recv_msg = protocol_library.client_verify_chksum(sock)
  #print msg form server
  msg_from_server = "Message from Server {}".format(recv_msg)
  print(msg_from_server)