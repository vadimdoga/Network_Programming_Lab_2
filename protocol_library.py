import hashlib, pickle, json

buffer_size = 30000
server_address = ("127.0.0.1", 8080)
error_msg = b"invalid_msg"
server_ACK = 5320
client_SYN = 4320
t_SYN = 2000

#convert
def json_bytes_dumps(dumping):
  dumping = json.dumps(dumping)
  dumping = pickle.dumps(dumping)
  return dumping
def json_bytes_loads(loading):
  loading = pickle.loads(loading)
  loading = json.loads(loading)
  return loading

#cheksum error checking + retransmission
def create_json(msg_from_client, bool):
  encoded_msg_from_client = str.encode(msg_from_client)
  if bool:
    chksm = hashlib.sha1(b"encoded_msg_from_client").hexdigest()
  else:
    chksm = hashlib.sha1(encoded_msg_from_client).hexdigest()

  dict_to_send = {
    'msg': msg_from_client,
    'chksm': chksm,
    'type': 'msg_checksum'
  }
  json_to_send = json_bytes_dumps(dict_to_send)
  return json_to_send

def client_verify_chksum(sock):
  msg_from_server = sock.recvfrom(buffer_size)
  if msg_from_server[0] == b'invalid_msg':
    #retransmission
    return "invalid_msg"
  else:
    return msg_from_server[0]

def server_verify_chksm(sock, msg_from_server, msg_from_client, chksm, address):
  hashed_msg = str.encode(msg_from_client)
  hashed_msg = hashlib.sha1(hashed_msg).hexdigest()
  if chksm != hashed_msg:
    sock.sendto(error_msg, address)
    print("Invalid Message")
    return False
  else:
    sock.sendto(msg_from_server, address)
    print("Valid Message")
    print("Message from Client: ", msg_from_client)
    return True

def recv_from_client(sock):
  recv_from_client = sock.recvfrom(buffer_size)

  client_address = recv_from_client[1]
  json_from_client = recv_from_client[0]

  json_from_client = json_bytes_loads(json_from_client)

  if json_from_client['type'] == 'msg_checksum':
    msg = json_from_client["msg"]
    chksm = json_from_client['chksm']

    return {
      'msg': msg,
      'chksm': chksm,
      'address': client_address
    }
  elif json_from_client['type'] == 'fin':
    t_recv_header = Header(json_from_client['SYN'], json_from_client['ACK'])
    t_recv_header.change_SYN_with_ACK()
    t_recv_header.increment_ACK()
    t_recv_header = t_recv_header.get_header_data()
    t_recv_header = json_bytes_dumps(t_recv_header)
    sock.sendto(t_recv_header, client_address)
    print("Connection terminated")
    return 'fin'
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
def process_server_header(server_header, client_address):
  print("Client ", client_address, " connected")
  server_header = json_bytes_loads(server_header)
  server_header = Header(server_header['SYN'], server_ACK)
  server_header.change_SYN_with_ACK()
  server_header.increment_ACK()
  server_header = server_header.get_header_data()

  server_header = json_bytes_dumps(server_header)
  return server_header
def verify_server_connection(server_header):
  server_header = json_bytes_loads(server_header)

  if server_header['ACK'] == (server_ACK + 1):
    print("Connection established")
    return True
  else:
    return False
def establish_connection(sock):
  while True:
    server_header, client_address = sock.recvfrom(buffer_size)
      
    server_header = process_server_header(server_header, client_address)
    sock.sendto(server_header, client_address)

    recv_from_client = sock.recvfrom(buffer_size)
    server_header = recv_from_client[0]
    
    verify_connection = verify_server_connection(server_header)
    if verify_connection:
      break

#client handshake
def initial_client_SYN():
  client_header = Header(client_SYN, None).get_header_data()
  client_header = json_bytes_dumps(client_header)
  return client_header
def process_client_header(client_header):
  client_header = Header(client_header['SYN'], client_header['ACK'])
  client_header.change_SYN_with_ACK()
  client_header.increment_ACK()
  client_header = client_header.get_header_data()

  client_header = json_bytes_dumps(client_header)
  return client_header
def verify_client_connection(sock):
  recv_from_server = sock.recvfrom(buffer_size)
  client_header = recv_from_server[0]
  client_header = json_bytes_loads(client_header)

  if client_header['ACK'] == (client_SYN + 1):
    client_header = process_client_header(client_header)
    sock.sendto(client_header, server_address)
    return True
  else:
    return False
def handshake(sock):
  client_header = initial_client_SYN()
  sock.sendto(client_header, server_address)

  verify_connection = verify_client_connection(sock)
  if verify_connection:
    print("Connection established")
    return True
  else:
    print("Connection failed")
    return False

def terminate_connection(sock):
  t_client_header = Header(t_SYN, None)
  t_client_header = t_client_header.get_header_data()
  t_client_header['type'] = 'fin'

  t_client_header = json_bytes_dumps(t_client_header)
  sock.sendto(t_client_header, server_address)

  t_recv = sock.recvfrom(buffer_size)[0]
  t_recv = json_bytes_loads(t_recv)
  if t_recv['ACK'] == t_SYN + 1:
    print("Connection terminated")