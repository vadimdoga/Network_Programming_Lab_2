import hashlib
import protocol_library, protocol_header

json_bytes_dumps = protocol_library.json_bytes_dumps
json_bytes_loads = protocol_library.json_bytes_loads

BUFFER_SIZE = protocol_library.BUFFER_SIZE
SERVER_ADDRESS = protocol_library.SERVER_ADDRESS
CLIENT_SYN = protocol_library.CLIENT_SYN
T_CLIENT_SYN = protocol_library.T_CLIENT_SYN


#generate a json with msg and it's checksum
def create_json(msg_from_client, bool):
  encoded_msg_from_client = str.encode(msg_from_client)
  #false cheksum and true checksum
  if bool:
    chksm = hashlib.sha1(b"encoded_msg_from_client").hexdigest()
  else:
    chksm = hashlib.sha1(encoded_msg_from_client).hexdigest()
  #return dict with msg, checksum and type that cand be msg_checksum either fin(terminate connection)
  dict_to_send = {
    'msg': msg_from_client,
    'chksm': chksm,
    'type': 'msg_checksum'
  }
  json_to_send = json_bytes_dumps(dict_to_send)
  return json_to_send

#verify server response on validity of checksum
def client_verify_chksum(sock):
  msg_from_server = sock.recvfrom(BUFFER_SIZE)
  if msg_from_server[0] == b'invalid_msg':
    #retransmission
    return "invalid_msg"
  else:
    #send msg from server
    return msg_from_server[0]


#client handshake
#send client SYN to server side
def initial_CLIENT_SYN():
  client_header = protocol_header.Header(CLIENT_SYN, None).get_header_data()
  client_header = json_bytes_dumps(client_header)
  return client_header
#receive server SYN and updated ACK and send client updated client ACK
def process_client_header(client_header):
  client_header = protocol_header.Header(client_header['SYN'], client_header['ACK'])
  client_header.change_SYN_with_ACK()
  client_header.increment_ACK()
  client_header = client_header.get_header_data()

  client_header = json_bytes_dumps(client_header)
  return client_header
#receive from server SYN and ACK and verify ACK
def verify_client_connection(sock):
  recv_from_server = sock.recvfrom(BUFFER_SIZE)
  client_header = recv_from_server[0]
  client_header = json_bytes_loads(client_header)

  #if true, connection established
  if client_header['ACK'] == (CLIENT_SYN + 1):
    client_header = process_client_header(client_header)
    sock.sendto(client_header, SERVER_ADDRESS)
    return True
  else:
    return False
#client handshake
def client_establish_connection(sock):
  client_header = initial_CLIENT_SYN()
  sock.sendto(client_header, SERVER_ADDRESS)

  verify_connection = verify_client_connection(sock)
  if verify_connection:
    print("Connection established")
    return True
  else:
    print("Connection failed")
    return False
#send to server to stop connection by sending a SYN and waiting for and updated ACK
def terminate_connection(sock):
  while True:
    #send a json with type fin
    t_client_header = protocol_header.Header(T_CLIENT_SYN, None)
    t_client_header = t_client_header.get_header_data()
    t_client_header['type'] = 'fin'

    t_client_header = json_bytes_dumps(t_client_header)
    sock.sendto(t_client_header, SERVER_ADDRESS)
    #receive and updated ACK
    t_recv = sock.recvfrom(BUFFER_SIZE)[0]
    t_recv = json_bytes_loads(t_recv)
    
    if t_recv['ACK'] == T_CLIENT_SYN + 1:
      t_client_header = protocol_header.Header(t_recv['SYN'], t_recv['ACK'])
      t_client_header.change_SYN_with_ACK()
      t_client_header.increment_ACK()
      t_client_header = t_client_header.get_header_data()
      t_client_header = json_bytes_dumps(t_client_header)
      sock.sendto(t_client_header, SERVER_ADDRESS)
      print("Connection terminated")
      break
    else:
      print("Error during stopping connection.")

   
