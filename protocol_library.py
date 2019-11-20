import hashlib, pickle, json

buffer_size = 30000
error_msg = b"invalid_msg"


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
    return msg_from_server

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
