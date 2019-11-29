from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
import json, base64
#generate aes key
def generate_AES_key():
  AES_KEY = get_random_bytes(16)

  return AES_KEY

#generate public & private key used in init
def generate_RSA_keys():
  keys = RSA.generate(2048)

  PRIVATE_KEY = keys.export_key().decode()
  PUBLIC_KEY = keys.publickey().export_key().decode()

  return PUBLIC_KEY, PRIVATE_KEY

#encrypt json with RSA and AES
def encrypt_json(data, chksm, type, PUBLIC_KEY, AES_KEY):
  print("Message length: ", len(data))
  print("AES Key length: ", len(AES_KEY))

  data = data.encode('utf-8')
  PUBLIC_KEY = RSA.import_key(PUBLIC_KEY)

  #encrypt aes key with public rsa key
  cipher_rsa = PKCS1_OAEP.new(PUBLIC_KEY)
  enc_aes_key = cipher_rsa.encrypt(AES_KEY)
  #encrypt data with aes 
  cipher_aes = AES.new(AES_KEY, AES.MODE_EAX)
  ciphertext, tag = cipher_aes.encrypt_and_digest(data)
  nonce = cipher_aes.nonce

  print({
    'msg': {
      'enc_aes_key': enc_aes_key,
      'nonce': nonce,
      'tag': tag,
      'ciphertext': ciphertext
    },
    'chksm': chksm,
    'type': 'msg_checksum'
  })
  
  enc_aes_key = enc_aes_key.decode("ISO-8859-1")
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
    'type': 'msg_checksum'
  }

#decrypt json with RSA and AES
def decrypt_json(encrypted_json, PRIVATE_KEY):

  #extract data from json
  enc_aes_key = encrypted_json['msg']['enc_aes_key']
  nonce = encrypted_json['msg']['nonce']
  tag = encrypted_json['msg']['tag']
  ciphertext = encrypted_json['msg']['ciphertext']
  chksm = encrypted_json['chksm']
  msg_type = encrypted_json['type']
  #decrypt aes_key with rsa pv key
  PRIVATE_KEY = RSA.import_key(PRIVATE_KEY)

  cipher_rsa = PKCS1_OAEP.new(PRIVATE_KEY)
  aes_key = cipher_rsa.decrypt(enc_aes_key)
  #decrypt data with aes
  cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce)
  data = cipher_aes.decrypt_and_verify(ciphertext, tag)
  data = data.decode("utf-8")

  return {
    'msg': data,
    'chksm': chksm,
    'type': msg_type
  }