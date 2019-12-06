from protocol.library.protocol_header import Header
from protocol.library.protocol_general import json_bytes_dumps, json_bytes_loads, BUFFER_SIZE

RECEIVER_ACK = 5320
x = ' '
#receiver handshake
#receive from sender SYN. Change SYN with ACK and send update ACK with receiver SYN
def process_header(receiver_header, RSA_PUBLIC_KEY):
  # receiver_header = json_bytes_loads(receiver_header)
  #header class
  receiver_header = Header(receiver_header['SYN'], RECEIVER_ACK)
  receiver_header.change_SYN_with_ACK()
  receiver_header.increment_ACK()
  receiver_header.add_rsa_public_key(RSA_PUBLIC_KEY)
  receiver_header = receiver_header.get_header_data()

  receiver_header = json_bytes_dumps(receiver_header)
  return receiver_header
#receive updated ACK from sender to confirm connection
def verify_connection(receiver_header):
  receiver_header = json_bytes_loads(receiver_header)
  if receiver_header['ACK'] == (RECEIVER_ACK + 1):
    print(x * 10 + "Connection established")
    return True
  else:
    return False
def establish_connection(sock, RSA_PUBLIC_KEY):
  # while True:
  recv = sock.recvfrom(BUFFER_SIZE)
  sender_address = recv[1]
  receiver_header = recv[0]
  receiver_header = json_bytes_loads(receiver_header)
  #recv SYN send receiver SYN and updated ACK
  receiver_header = process_header(receiver_header, RSA_PUBLIC_KEY)
  sock.sendto(receiver_header, sender_address)

  recv_from_sender = sock.recvfrom(BUFFER_SIZE)
  receiver_header = recv_from_sender[0]
  #recv updated ACK and based on it decide if connection established
  verify = verify_connection(receiver_header)
  if verify:
    return sender_address
  else:
    return False
 