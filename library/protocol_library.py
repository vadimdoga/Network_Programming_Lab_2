import json, pickle
import binascii

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
#convert elements from json object from str to bytes
def json_el_to_byte(json):
  #extract
  enc_aes_key = json['msg']['enc_aes_key']
  nonce = json['msg']['nonce']
  tag = json['msg']['tag']
  ciphertext = json['msg']['ciphertext']
  #convert
  enc_aes_key = enc_aes_key.encode("raw_unicode_escape")
  nonce = nonce.encode("raw_unicode_escape")
  tag = tag.encode("raw_unicode_escape")
  ciphertext = ciphertext.encode("raw_unicode_escape")
  
  #no need for converting
  chksm = json['chksm']
  type = json['type']

  return {
    'msg': {
      'enc_aes_key': enc_aes_key,
      'nonce': nonce,
      'tag': tag,
      'ciphertext': ciphertext
    },
    'chksm': chksm,
    'type': type
  }




