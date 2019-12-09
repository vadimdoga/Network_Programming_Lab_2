import json, pickle, sys

BUFFER_SIZE = int(sys.argv[1])

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
#convert json elements from bytes to string
def convert_json_el_to_str(json):
  #extract
  enc_aes_key, nonce, tag, ciphertext, chksm, msg_type, type_of_sending, len_msg_bool, send_to_address = extract_data_from_json(json)

  #convert
  enc_aes_key = enc_aes_key.decode('ISO-8859-1')
  nonce = nonce.decode('ISO-8859-1')
  tag = tag.decode('ISO-8859-1')
  ciphertext = ciphertext.decode('ISO-8859-1')
  
  return {
    'msg': {
      'enc_aes_key': enc_aes_key,
      'nonce': nonce,
      'tag': tag,
      'ciphertext': ciphertext
    },
    'chksm': chksm,
    'type': msg_type,
    'type_of_sending': type_of_sending,
    'len_msg_bool': len_msg_bool,
    'send_to_address': send_to_address
  }
#convert elements from json object from str to bytes
def convert_json_el_to_byte(json):
  #extract
  enc_aes_key, nonce, tag, ciphertext, chksm, msg_type, type_of_sending, len_msg_bool, send_to_address = extract_data_from_json(json)

  #convert
  enc_aes_key = enc_aes_key.encode('ISO-8859-1')
  nonce = nonce.encode('ISO-8859-1')
  tag = tag.encode('ISO-8859-1')
  ciphertext = ciphertext.encode('ISO-8859-1')

  return {
    'msg': {
      'enc_aes_key': enc_aes_key,
      'nonce': nonce,
      'tag': tag,
      'ciphertext': ciphertext
    },
    'chksm': chksm,
    'type': msg_type,
    'type_of_sending': type_of_sending,
    'len_msg_bool': len_msg_bool,
    'send_to_address': send_to_address
  }
#extract from json all data and return them 
def extract_data_from_json(json):
  #extract data from json
  enc_aes_key = json['msg']['enc_aes_key']
  nonce = json['msg']['nonce']
  tag = json['msg']['tag']
  ciphertext = json['msg']['ciphertext']
  chksm = json['chksm']
  msg_type = json['type']
  type_of_sending = json['type_of_sending']
  len_msg_bool = json['len_msg_bool']
  send_to_address = json['send_to_address']
  
  return enc_aes_key, nonce, tag, ciphertext, chksm, msg_type, type_of_sending, len_msg_bool, send_to_address
  

