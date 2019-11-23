import hashlib, pickle, json

buffer_size = 30000
server_address = ("127.0.0.1", 8080)
error_msg = b"invalid_msg"
server_ACK = 5320
client_SYN = 4320
t_client_SYN = 2000
t_server_SYN = 3000

#convert to json and byte format
def json_bytes_dumps(dumping):
  dumping = json.dumps(dumping)
  dumping = pickle.dumps(dumping)
  return dumping
#convert from json and bytes
def json_bytes_loads(loading):
  loading = pickle.loads(loading)
  loading = json.loads(loading)
  return loading

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
  msg_from_server = sock.recvfrom(buffer_size)
  if msg_from_server[0] == b'invalid_msg':
    #retransmission
    return "invalid_msg"
  else:
    #send msg from server
    return msg_from_server[0]
#verify checksum on server side
def server_verify_chksm(sock, msg_from_server, msg_from_client, chksm, address):
  #hash msg and verify if it's equal with checksum
  hashed_msg = str.encode(msg_from_client)
  hashed_msg = hashlib.sha1(hashed_msg).hexdigest()
  if chksm != hashed_msg:
    #if not valid send to client error msg
    sock.sendto(error_msg, address)
    print("Invalid Message, waiting for retransmission.")
  else:
    #if valid send to client msg from server
    sock.sendto(msg_from_server, address)
    print("Valid Message")
    print("Message from Client: ", msg_from_client)
#receive on server side
def server_receive(sock):
  recv_from_client = sock.recvfrom(buffer_size)

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
      t_send_header = Header(t_recv['SYN'], t_server_SYN)
      t_send_header.change_SYN_with_ACK()
      t_send_header.increment_ACK()
      t_send_header = t_send_header.get_header_data()
      t_send_header = json_bytes_dumps(t_send_header)
      sock.sendto(t_send_header, client_address)

      t_recv = sock.recvfrom(buffer_size)[0]
      t_recv = json_bytes_loads(t_recv)

      if t_recv['ACK'] == t_server_SYN + 1: 
        print("Connection terminated")
        return 'fin'
      else:
        print("Error during stopping connection.")

#handshake header
class Header:
  def __init__(self, SYN, ACK):
    self.SYN = SYN
    self.ACK = ACK
  def get_header_data(self):
    return {
      'SYN': self.SYN,
      'ACK': self.ACK
    }
  def increment_ACK(self):
    self.ACK = self.ACK + 1
  def change_SYN_with_ACK(self):
    temp = self.ACK
    self.ACK = self.SYN
    self.SYN = temp

#server handshake
#receive from client SYN. Change SYN with ACK and send update ACK with server SYN
def process_server_header(server_header, client_address):
  print("Client ", client_address, " connected")
  server_header = json_bytes_loads(server_header)
  #header class
  server_header = Header(server_header['SYN'], server_ACK)
  server_header.change_SYN_with_ACK()
  server_header.increment_ACK()
  server_header = server_header.get_header_data()

  server_header = json_bytes_dumps(server_header)
  return server_header
#receive updated ACK from client to confirm connection
def verify_server_connection(server_header):
  server_header = json_bytes_loads(server_header)

  if server_header['ACK'] == (server_ACK + 1):
    print("Connection established")
    return True
  else:
    return False
def server_establish_connection(sock):
  while True:
    server_header, client_address = sock.recvfrom(buffer_size)
    #recv SYN send server SYN and updated ACK
    server_header = process_server_header(server_header, client_address)
    sock.sendto(server_header, client_address)

    recv_from_client = sock.recvfrom(buffer_size)
    server_header = recv_from_client[0]
    #recv updated ACK and based on it decide if connection established
    verify_connection = verify_server_connection(server_header)
    if verify_connection:
      break

#client handshake
#send client SYN to server side
def initial_client_SYN():
  client_header = Header(client_SYN, None).get_header_data()
  client_header = json_bytes_dumps(client_header)
  return client_header
#receive server SYN and updated ACK and send client updated client ACK
def process_client_header(client_header):
  client_header = Header(client_header['SYN'], client_header['ACK'])
  client_header.change_SYN_with_ACK()
  client_header.increment_ACK()
  client_header = client_header.get_header_data()

  client_header = json_bytes_dumps(client_header)
  return client_header
#receive from server SYN and ACK and verify ACK
def verify_client_connection(sock):
  recv_from_server = sock.recvfrom(buffer_size)
  client_header = recv_from_server[0]
  client_header = json_bytes_loads(client_header)

  #if true, connection established
  if client_header['ACK'] == (client_SYN + 1):
    client_header = process_client_header(client_header)
    sock.sendto(client_header, server_address)
    return True
  else:
    return False
#client handshake
def client_establish_connection(sock):
  client_header = initial_client_SYN()
  sock.sendto(client_header, server_address)

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
    t_client_header = Header(t_client_SYN, None)
    t_client_header = t_client_header.get_header_data()
    t_client_header['type'] = 'fin'

    t_client_header = json_bytes_dumps(t_client_header)
    sock.sendto(t_client_header, server_address)
    #receive and updated ACK
    t_recv = sock.recvfrom(buffer_size)[0]
    t_recv = json_bytes_loads(t_recv)
    
    if t_recv['ACK'] == t_client_SYN + 1:
      t_client_header = Header(t_recv['SYN'], t_recv['ACK'])
      t_client_header.change_SYN_with_ACK()
      t_client_header.increment_ACK()
      t_client_header = t_client_header.get_header_data()
      t_client_header = json_bytes_dumps(t_client_header)
      sock.sendto(t_client_header, server_address)
      print("Connection terminated")
      break
    else:
      print("Error during stopping connection.")

   
