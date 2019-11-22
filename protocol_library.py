import hashlib, pickle, json

buffer_size = 30000
server_address = ("127.0.0.1", 8080)
error_msg = b"invalid_msg"
server_ACK = 5320
client_SYN = 4320

#cheksum error checking + retransmission
def create_json(msg_from_client):
  encoded_msg_from_client = str.encode(msg_from_client)
  chksm = hashlib.sha1(encoded_msg_from_client).hexdigest()

  dict_to_send = {
    'msg': msg_from_client,
    'chksm': chksm
  }
  json_to_send = json.dumps(dict_to_send)
  json_to_send = pickle.dumps(json_to_send)
  return json_to_send

def client_verify_chksum(sock):
  msg_from_server = sock.recvfrom(buffer_size)
  if msg_from_server[0] == b'invalid_msg':
    return False
  else:
    return msg_from_server[0]

def server_verify_chksm(sock, msg_from_server, msg_from_client, chksm, address):
  msg_from_client = str.encode(msg_from_client)
  hashed_msg = hashlib.sha1(msg_from_client).hexdigest()
  if chksm != hashed_msg:
    sock.sendto(error_msg, address)
    print("Invalid Message")
    return False
  else:
    sock.sendto(msg_from_server, address)
    print("Valid Message")
    return True

def recv_from_client(sock):
  recv_from_client = sock.recvfrom(buffer_size)

  address = recv_from_client[1]
  json_from_client = recv_from_client[0]
  json_from_client = pickle.loads(json_from_client)
  #convert to dict
  json_from_client = json.loads(json_from_client)

  msg = json_from_client["msg"]
  chksm = json_from_client['chksm']

  return {
    'msg': msg,
    'chksm': chksm,
    'address': address
  }
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
  server_header = pickle.loads(server_header)
  server_header = Header(server_header['SYN'], server_ACK)
  server_header.change_SYN_with_ACK()
  server_header.increment_ACK()
  server_header = server_header.get_header_data()
  server_header = pickle.dumps(server_header)
  return server_header
def verify_server_connection(server_header):
  server_header = pickle.loads(server_header)
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
  client_header = pickle.dumps(client_header)
  return client_header
def process_client_header(client_header):
  client_header = Header(client_header['SYN'], client_header['ACK'])
  client_header.change_SYN_with_ACK()
  client_header.increment_ACK()
  client_header = client_header.get_header_data()
  client_header = pickle.dumps(client_header)
  return client_header
def verify_client_connection(sock):
  recv_from_server = sock.recvfrom(buffer_size)
  client_header = recv_from_server[0]
  client_header = pickle.loads(client_header)
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