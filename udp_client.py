import socket
import protocol_library
i = 0
msg_from_client = "hello from client"
#create dict with msg and cheksum
json_to_send = protocol_library.create_json(msg_from_client, True)
#udp connection
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
  handshake = protocol_library.handshake(sock)
  if handshake:
    while True:
      if i == 5:
        json_to_send = protocol_library.create_json(msg_from_client, False)
      #send to server
      sock.sendto(json_to_send, protocol_library.server_address)
      #based on recv from server check if data is valid
      recv_msg = protocol_library.client_verify_chksum(sock)
      if recv_msg == "invalid_msg":
        print("Invalid msg, retransmitting message.")
      else:
        #print msg form server
        print("Message from Server: ", recv_msg)
        break
      i = i +1
    protocol_library.terminate_connection(sock)


  

