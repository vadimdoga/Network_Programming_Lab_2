import hashlib
import protocol_library, protocol_header

json_bytes_dumps = protocol_library.json_bytes_dumps
json_bytes_loads = protocol_library.json_bytes_loads

BUFFER_SIZE = protocol_library.BUFFER_SIZE
T_SERVER_SYN = protocol_library.T_SERVER_SYN
SERVER_ACK = protocol_library.SERVER_ACK
ERROR_MSG = protocol_library.ERROR_MSG


#verify checksum on server side
def server_verify_chksm(sock, msg_from_server, msg_from_client, chksm, address):
  #hash msg and verify if it's equal with checksum
  hashed_msg = str.encode(msg_from_client)
  hashed_msg = hashlib.sha1(hashed_msg).hexdigest()
  if chksm != hashed_msg:
    #if not valid send to client error msg
    sock.sendto(ERROR_MSG, address)
    print("Invalid Message, waiting for retransmission.")
  else:
    #if valid send to client msg from server
    sock.sendto(msg_from_server, address)
    print("Valid Message")
    print("Message from Client: ", msg_from_client)
#receive on server side
def server_receive(sock):
  recv_from_client = sock.recvfrom(BUFFER_SIZE)

  client_address = recv_from_client[1]
  json_from_client = recv_from_client[0]

  json_from_client = json_bytes_loads(json_from_client)
  #if type is msg_checksum then server receives a dict with msg,chksm,address
  if json_from_client['type'] == 'msg_checksum':
    msg = json_from_client["msg"]
    chksm = json_from_client['chksm']

    return {
      'msg': msg,
      'chksm': chksm,
      'address': client_address
    }
  #if type is fin then server acknowledges that it's terminate command
  elif json_from_client['type'] == 'fin':
    while True:
      t_recv = json_from_client
      #receives SYN from client and send updated ACK to client for it to stop
      t_send_header = protocol_header.Header(t_recv['SYN'], T_SERVER_SYN)
      t_send_header.change_SYN_with_ACK()
      t_send_header.increment_ACK()
      t_send_header = t_send_header.get_header_data()
      t_send_header = json_bytes_dumps(t_send_header)
      sock.sendto(t_send_header, client_address)

      t_recv = sock.recvfrom(BUFFER_SIZE)[0]
      t_recv = json_bytes_loads(t_recv)

      if t_recv['ACK'] == T_SERVER_SYN + 1: 
        print("Connection terminated")
        return 'fin'
      else:
        print("Error during stopping connection.")


#server handshake
#receive from client SYN. Change SYN with ACK and send update ACK with server SYN
def process_server_header(server_header, client_address):
  print("Client ", client_address, " connected")
  server_header = json_bytes_loads(server_header)
  #header class
  server_header = protocol_header.Header(server_header['SYN'], SERVER_ACK)
  server_header.change_SYN_with_ACK()
  server_header.increment_ACK()
  server_header = server_header.get_header_data()

  server_header = json_bytes_dumps(server_header)
  return server_header
#receive updated ACK from client to confirm connection
def verify_server_connection(server_header):
  server_header = json_bytes_loads(server_header)

  if server_header['ACK'] == (SERVER_ACK + 1):
    print("Connection established")
    return True
  else:
    return False
def server_establish_connection(sock):
  while True:
    server_header, client_address = sock.recvfrom(BUFFER_SIZE)
    #recv SYN send server SYN and updated ACK
    server_header = process_server_header(server_header, client_address)
    sock.sendto(server_header, client_address)

    recv_from_client = sock.recvfrom(BUFFER_SIZE)
    server_header = recv_from_client[0]
    #recv updated ACK and based on it decide if connection established
    verify_connection = verify_server_connection(server_header)
    if verify_connection:
      break

