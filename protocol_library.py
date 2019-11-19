import hashlib, pickle

buffer_size = 30000
error_msg = b"invalid_msg"


def create_dict(msg_from_client):
  encoded_msg_from_client = str.encode(msg_from_client)
  chksm = hashlib.sha1(encoded_msg_from_client).digest()

  dict_to_send = {
    'msg': msg_from_client,
    'chksm': chksm
  }

  dict_to_send = pickle.dumps(dict_to_send)
  return dict_to_send

def client_verify_chksum(sock):
  msg_from_server = sock.recvfrom(buffer_size)
  if msg_from_server[0] == b'invalid_msg':
    return False
  else:
    return msg_from_server

def server_verify_chksm(sock, msg_from_server, msg_from_client, chksm, address):
  msg_from_client = str.encode(msg_from_client)
  hashed_msg = hashlib.sha1(msg_from_client).digest()
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
  dict_from_client = recv_from_client[0]
  dict_from_client = pickle.loads(dict_from_client)

  msg = dict_from_client['msg']
  chksm = dict_from_client['chksm']

  return {
    'msg': msg,
    'chksm': chksm,
    'address': address
  }
