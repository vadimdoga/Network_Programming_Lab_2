from protocol.library.protocol_header import Header
from protocol.library.protocol_general import json_bytes_dumps, json_bytes_loads, BUFFER_SIZE
from protocol.library.sender.protocol_sender import get_RSA_PUBLIC_KEY, get_AES_KEY

SENDER_SYN = 4320
RECEIVER_ADDRESS = ("127.0.0.1", 8080)
x = ' '

#sender handshake
#send sender SYN to receiver side
def initial_SYN():
  sender_header = Header(SENDER_SYN, None).get_header_data()
  sender_header = json_bytes_dumps(sender_header)
  return sender_header
#receive receiver SYN and updated ACK and send sender updated sender ACK
def process_header(sender_header):
  sender_header = Header(sender_header['SYN'], sender_header['ACK'])
  sender_header.change_SYN_with_ACK()
  sender_header.increment_ACK()
  sender_header = sender_header.get_header_data()

  sender_header = json_bytes_dumps(sender_header)
  return sender_header
#receive from receiver SYN and ACK and verify ACK
def verify_connection(sock):
  recv_from_receiver = sock.recvfrom(BUFFER_SIZE)
  sender_header = recv_from_receiver[0]
  sender_header = json_bytes_loads(sender_header)
  #get public key
  if 'RSA_PUBLIC_KEY' in sender_header:
    RSA_PUBLIC_KEY = sender_header['RSA_PUBLIC_KEY']
    RSA_PUBLIC_KEY = str.encode(RSA_PUBLIC_KEY)
    #give rsa pub key to protocol_sender
    get_RSA_PUBLIC_KEY(RSA_PUBLIC_KEY)
  #if true, connection established
  if sender_header['ACK'] == (SENDER_SYN + 1):
    sender_header = process_header(sender_header)
    sock.sendto(sender_header, RECEIVER_ADDRESS)
    return True
  else:
    return False
#sender handshake
def establish_connection(sock, key):
  get_AES_KEY(key)

  sender_header = initial_SYN()
  sock.sendto(sender_header, RECEIVER_ADDRESS)

  verify = verify_connection(sock)
  if verify:
    print(x * 10 + "Connection established")
    return True
  else:
    print(x * 10 + "Connection failed")
    return False