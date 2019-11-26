import json, pickle

SERVER_ADDRESS = ("127.0.0.1", 8080)
ERROR_MSG = b"invalid_msg"
SERVER_ACK = 5320
CLIENT_SYN = 4320
T_CLIENT_SYN = 2000
T_SERVER_SYN = 3000
BUFFER_SIZE = 30000

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




