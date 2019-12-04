from library.protocol_general import extract_data_from_json
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
import json, base64

MAX_RSA_LENGTH = 214

#generate aes key
def generate_AES_key():
  AES_KEY = get_random_bytes(32)
  print("AES_KEY Generated")
  return AES_KEY

#generate public & private key used in init
def generate_RSA_keys():
  keys = RSA.generate(2048)

  PRIVATE_KEY = keys.export_key().decode()
  PUBLIC_KEY = keys.publickey().export_key().decode()
  print("RSA_KEYS Generated")
  return PUBLIC_KEY, PRIVATE_KEY

#encrypt json with RSA and AES
def encrypt_json(msg, chksm, type, PUBLIC_KEY, AES_KEY):
  print("Message length: ", len(msg))
  print("AES Key length: ", len(AES_KEY))

  if len(msg) > MAX_RSA_LENGTH:
    len_msg_bool = True
  else:
    len_msg_bool = False

  msg = msg.encode('utf-8')
  PUBLIC_KEY = RSA.import_key(PUBLIC_KEY)

  #generate aes and rsa ciphers
  cipher_rsa = PKCS1_OAEP.new(PUBLIC_KEY)
  cipher_aes = AES.new(AES_KEY, AES.MODE_EAX)

  if len(msg) > MAX_RSA_LENGTH:
    print("MSG LENGTH TO LARGE. ENCRYPTING ONLY AES_KEY WITH RSA")
    #encrypt aes key with public rsa key
    enc_aes_key = cipher_rsa.encrypt(AES_KEY)
    #encrypt msg with aes 
    ciphertext, tag = cipher_aes.encrypt_and_digest(msg)
    nonce = cipher_aes.nonce
    
  else:
    print("ENCRYPTING MSG & AES_KEY WITH RSA")
    #encrypt aes key with public rsa key
    enc_aes_key = cipher_rsa.encrypt(AES_KEY)
    #encrypt msg with aes and rsa
    ciphertext, tag = cipher_aes.encrypt_and_digest(msg)
    enc_ciphertext = cipher_rsa.encrypt(ciphertext)
    ciphertext = enc_ciphertext
    nonce = cipher_aes.nonce
    
  return {
    'msg': {
      'enc_aes_key': enc_aes_key,
      'nonce': nonce,
      'tag': tag,
      'ciphertext': ciphertext
    },
    'chksm': chksm,
    'type': 'msg_checksum',
    'len_msg_bool': len_msg_bool
  }

#decrypt json with RSA and AES
def decrypt_json(encrypted_json, PRIVATE_KEY):
  enc_aes_key, nonce, tag, ciphertext, chksm, msg_type, len_msg_bool = extract_data_from_json(encrypted_json)
  #assign
  enc_ciphertext = ciphertext
  PRIVATE_KEY = RSA.import_key(PRIVATE_KEY)

  #generate rsa cipher
  cipher_rsa = PKCS1_OAEP.new(PRIVATE_KEY)

  #decrypt aes_key with rsa pv key
  aes_key = cipher_rsa.decrypt(enc_aes_key)

  #generate aes cipher
  cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce)

  if len_msg_bool:
    print("DECRYPTING ONLY AES_KEY WITH RSA")
    #decrypt msg with aes
    msg = cipher_aes.decrypt_and_verify(ciphertext, tag)
  else:
    print("DECRYPTING MSG & AES_KEY WITH RSA")
    #decrypt msg with rsa
    ciphertext = cipher_rsa.decrypt(enc_ciphertext)
    #decrypt msg with aes
    msg = cipher_aes.decrypt_and_verify(ciphertext, tag)

  msg = msg.decode("utf-8")
  return {
    'msg': msg,
    'chksm': chksm,
    'type': msg_type
  }