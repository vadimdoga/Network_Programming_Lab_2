import hashlib
import library.protocol_library, library.protocol_header

json_bytes_dumps = library.protocol_library.json_bytes_dumps
json_bytes_loads = library.protocol_library.json_bytes_loads

BUFFER_SIZE = library.protocol_library.BUFFER_SIZE
SERVER_ADDRESS = library.protocol_library.SERVER_ADDRESS
CLIENT_SYN = library.protocol_library.CLIENT_SYN
T_CLIENT_SYN = library.protocol_library.T_CLIENT_SYN

i = 0
MSG_FROM_CLIENT = "hello from client"


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
  #encrypt json

  return json_to_send

#verify server response on validity of checksum
def verify_chksum(sock):
  msg_from_server = sock.recvfrom(BUFFER_SIZE)
  if msg_from_server[0] == b'invalid_msg':
    #retransmission
    return "invalid_msg"
  else:
    #send msg from server
    return msg_from_server[0]


#client handshake
#send client SYN to server side
def initial_SYN():
  client_header = library.protocol_header.Header(CLIENT_SYN, None).get_header_data()
  client_header = json_bytes_dumps(client_header)
  return client_header
#receive server SYN and updated ACK and send client updated client ACK
def process_header(client_header):
  client_header = library.protocol_header.Header(client_header['SYN'], client_header['ACK'])
  client_header.change_SYN_with_ACK()
  client_header.increment_ACK()
  client_header = client_header.get_header_data()

  client_header = json_bytes_dumps(client_header)
  return client_header
#receive from server SYN and ACK and verify ACK
def verify_connection(sock):
  recv_from_server = sock.recvfrom(BUFFER_SIZE)
  client_header = recv_from_server[0]
  client_header = json_bytes_loads(client_header)

  #if true, connection established
  if client_header['ACK'] == (CLIENT_SYN + 1):
    client_header = process_header(client_header)
    sock.sendto(client_header, SERVER_ADDRESS)
    return True
  else:
    return False
#client handshake
def establish_connection(sock):
  client_header = initial_SYN()
  sock.sendto(client_header, SERVER_ADDRESS)

  verify = verify_connection(sock)
  if verify:
    print("Connection established")
    return True
  else:
    print("Connection failed")
    return False
#send to server to stop connection by sending a SYN and waiting for and updated ACK
def terminate_connection(sock):
  while True:
    #send a json with type fin
    t_client_header = library.protocol_header.Header(T_CLIENT_SYN, None)
    t_client_header = t_client_header.get_header_data()
    t_client_header['type'] = 'fin'

    t_client_header = json_bytes_dumps(t_client_header)
    sock.sendto(t_client_header, SERVER_ADDRESS)
    #receive and updated ACK
    t_recv = sock.recvfrom(BUFFER_SIZE)[0]
    t_recv = json_bytes_loads(t_recv)
    
    if t_recv['ACK'] == T_CLIENT_SYN + 1:
      t_client_header = library.protocol_header.Header(t_recv['SYN'], t_recv['ACK'])
      t_client_header.change_SYN_with_ACK()
      t_client_header.increment_ACK()
      t_client_header = t_client_header.get_header_data()
      t_client_header = json_bytes_dumps(t_client_header)
      sock.sendto(t_client_header, SERVER_ADDRESS)
      print("Connection terminated")
      break
    else:
      print("Error during stopping connection.")

def send_recv_msg(client):
  global i
  #create dict with msg and cheksum
  json_to_send = library.protocol_library_client.create_json(MSG_FROM_CLIENT, True)
  #udp connection
  if client.handshake:
    while True:
      if i == 5:
        json_to_send = library.protocol_library_client.create_json(MSG_FROM_CLIENT, False)
      #send to server
      client.sock.sendto(json_to_send, library.protocol_library_client.SERVER_ADDRESS)
      #based on recv from server, check if data is valid
      recv_msg = library.protocol_library_client.verify_chksum(client.sock)
      if recv_msg == "invalid_msg":
        print("Invalid msg, retransmitting message.")
      else:
        #print msg form server
        print("Message from Server: ", recv_msg)
        break
      i = i + 1
