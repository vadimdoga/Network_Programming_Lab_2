from protocol.library.protocol_header import Header
from protocol.library.protocol_crypto import decrypt_json
from protocol.library.protocol_general import convert_json_el_to_byte, json_bytes_dumps, json_bytes_loads, BUFFER_SIZE
from protocol.library.receiver.protocol_receiver_header import establish_connection
import hashlib, socket

ERROR_MSG = b"invalid_msg"
T_RECEIVER_SYN = 3000
MSG_FROM_RECEIVER = b"Successful message transmission"
RECEIVER_ADDRESS = ("127.0.0.1", 8080)
x = ' '

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
def receive_from_sender(sock, RSA_PRIVATE_KEY, RSA_PUBLIC_KEY):
  #general recv
  recv_from_sender = sock.recvfrom(BUFFER_SIZE)
  sender_address = recv_from_sender[1]

  json_from_sender = recv_from_sender[0]
  json_from_sender = json_bytes_loads(json_from_sender)
  #if there is type in json then it must decide either it's msg or terminate connection
  if 'type' in json_from_sender:
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
      termination = terminate_connection(sock, json_from_sender, sender_address)
      if termination:
        return 'fin'
  #if in json is SYN then receiver is establishing connection
  elif 'SYN' in json_from_sender:
    #handshake
    establish_connection(sock, RSA_PUBLIC_KEY, json_from_sender, sender_address)
    return 'connection established'
    
#recv fin and terminate connection
def terminate_connection(sock, t_recv, sender_address):
  while True:
    #receives SYN from sender and send updated ACK to sender for it to stop
    t_send_header = Header(t_recv['SYN'], T_RECEIVER_SYN)
    t_send_header.change_SYN_with_ACK()
    t_send_header.increment_ACK()
    t_send_header = t_send_header.get_header_data()
    t_send_header = json_bytes_dumps(t_send_header)
    sock.sendto(t_send_header, sender_address)

    t_recv = sock.recvfrom(BUFFER_SIZE)[0]
    t_recv = json_bytes_loads(t_recv)

    if t_recv['ACK'] == T_RECEIVER_SYN + 1: 
      print(x * 10 + "Connection terminated")
      return True
    else:
      print(x * 10 + "Error during stopping connection.")
      return False

def recv_from_sender_and_verify(receiver):
  #extract keys from receiver
  RSA_PRIVATE_KEY = receiver.RSA_PRIVATE_KEY
  RSA_PUBLIC_KEY = receiver.RSA_PUBLIC_KEY
  while True:
    #recv from sender
    recv = receive_from_sender(receiver.sock, RSA_PRIVATE_KEY, RSA_PUBLIC_KEY)
    if recv == 'fin':
      break
    elif 'msg' in recv:
      #verify the cheksum
      #if chksm not valid retransmit
      verify_chksm(receiver.sock, recv['msg'], recv['chksm'], recv['address'])
        


