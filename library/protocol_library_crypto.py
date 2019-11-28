from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
import json

#generate aes key
def generate_AES_key():
  AES_KEY = get_random_bytes(16)

  return AES_KEY

#generate public & private key used in init
def generate_RSA_keys():
  keys = RSA.generate(2048)

  PRIVATE_KEY = keys.export_key()
  PUBLIC_KEY = keys.publickey().export_key()

  return PRIVATE_KEY, PUBLIC_KEY

#encrypt json with RSA and AES
def encrypt_json(data, PUBLIC_KEY, AES_KEY):
  data = data.encode('utf-8')
  #encrypt aes key with public rsa key
  cipher_rsa = PKCS1_OAEP.new(PUBLIC_KEY)
  enc_aes_key = cipher_rsa.encrypt(AES_KEY)
  #encrypt data with aes 
  cipher_aes = AES.new(AES_KEY, AES.MODE_EAX)
  ciphertext, tag = cipher_aes.encrypt_and_digest(data)

  return json.dumps({
    'enc_aes_key': enc_aes_key,
    'nonce': cipher_aes.nonce,
    'tag': tag,
    'ciphertext': ciphertext
  })

#decrypt json with RSA and AES
def decrypt_json(encrypted_json, PRIVATE_KEY):
  encrypted_json = json.loads(encrypted_json)
  #extract data from json
  enc_aes_key = encrypted_json['enc_aes_key']
  nonce = encrypted_json['nonce']
  tag = encrypted_json['tag']
  ciphertext = encrypted_json['ciphertext']
  #decrypt aes_key with rsa pv key
  cipher_rsa = PKCS1_OAEP.new(PRIVATE_KEY)
  aes_key = cipher_rsa.decrypt(enc_aes_key)
  #decrypt data with aes
  cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce)
  data = cipher_aes.decrypt_and_verify(ciphertext, tag)
  data = data.decode("utf-8")
  print(data)
  return data