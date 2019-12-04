from library.protocol_header import Header
from library.protocol_library_crypto import decrypt_json
from library.protocol_library import convert_json_el_to_byte, json_bytes_dumps, json_bytes_loads, BUFFER_SIZE
import hashlib, socket

ERROR_MSG = b"invalid_msg"
RECEIVER_ACK = 5320
RECEIVER_SYN = 3000
MSG_FROM_RECEIVER = b"Successful message transmission"
RECEIVER_ADDRESS = ("127.0.0.1", 8080)

#sock init
def socket_init():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(RECEIVER_ADDRESS)
  return sock

#verify checksum on receiver side
def verify_chksm(sock, MSG_FROM_SENDER, chksm, address):
  #hash msg and verify if it's equal with checksum
  hashed_msg = str.encode(MSG_FROM_SENDER)
  hashed_msg = hashlib.sha1(hashed_msg).hexdigest()
  if chksm != hashed_msg:
    #if not valid send to sender error msg
    sock.sendto(ERROR_MSG, address)
    print("Invalid Message, waiting for retransmission.")
  else:
    #if valid send to sender msg from receiver
    sock.sendto(MSG_FROM_RECEIVER, address)
    print("Valid Message")
    print("Message from Sender: ", MSG_FROM_SENDER)
#receive on receiver side
def receive_from_sender(sock, RSA_PRIVATE_KEY):
  recv_from_sender = sock.recvfrom(BUFFER_SIZE)
  sender_address = recv_from_sender[1]

  json_from_sender = recv_from_sender[0]
  json_from_sender = json_bytes_loads(json_from_sender)
  
  #if type is msg_checksum then receiver receives a dict with msg,chksm,address
  if json_from_sender['type'] == 'msg_checksum':
    #convert json el from str to byte
    json_from_sender = convert_json_el_to_byte(json_from_sender)
    #decrypt json
    json_from_sender = decrypt_json(json_from_sender, RSA_PRIVATE_KEY)

    msg = json_from_sender["msg"]
    chksm = json_from_sender['chksm']

    return {
      'msg': msg,
      'chksm': chksm,
      'address': sender_address
    }
  #if type is fin then receiver acknowledges that it's terminate command
  elif json_from_sender['type'] == 'fin':
    while True:
      t_recv = json_from_sender
      #receives SYN from sender and send updated ACK to sender for it to stop
      t_send_header = Header(t_recv['SYN'], RECEIVER_SYN)
      t_send_header.change_SYN_with_ACK()
      t_send_header.increment_ACK()
      t_send_header = t_send_header.get_header_data()
      t_send_header = json_bytes_dumps(t_send_header)
      sock.sendto(t_send_header, sender_address)

      t_recv = sock.recvfrom(BUFFER_SIZE)[0]
      t_recv = json_bytes_loads(t_recv)

      if t_recv['ACK'] == RECEIVER_SYN + 1: 
        print("Connection terminated")
        return 'fin'
      else:
        print("Error during stopping connection.")


#receiver handshake
#receive from sender SYN. Change SYN with ACK and send update ACK with receiver SYN
def process_header(receiver_header, sender_address, RSA_PUBLIC_KEY):
  print("sender ", sender_address, " connected")
  receiver_header = json_bytes_loads(receiver_header)
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
    print("Connection established")
    return True
  else:
    return False
def establish_connection(sock, RSA_PUBLIC_KEY):
  while True:
    receiver_header, sender_address = sock.recvfrom(BUFFER_SIZE)
    #recv SYN send receiver SYN and updated ACK
    receiver_header = process_header(receiver_header, sender_address, RSA_PUBLIC_KEY)
    sock.sendto(receiver_header, sender_address)

    recv_from_sender = sock.recvfrom(BUFFER_SIZE)
    receiver_header = recv_from_sender[0]
    #recv updated ACK and based on it decide if connection established
    verify = verify_connection(receiver_header)
    if verify:
      break

    
def recv_from_sender_and_verify(receiver, RSA_PRIVATE_KEY):
  while True:
    #recv dict from sender
    recv = receive_from_sender(receiver.sock, RSA_PRIVATE_KEY)
    if recv == 'fin':
      break
    else:
      #verify the cheksum
      #if chksm not valid retransmit
      verify_chksm(receiver.sock, recv['msg'], recv['chksm'], recv['address'])
        


