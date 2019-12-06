from protocol.library.protocol_header import Header
from protocol.library.protocol_crypto import encrypt_json
from protocol.library.protocol_general import json_bytes_dumps, json_bytes_loads, convert_json_el_to_str, BUFFER_SIZE
import hashlib, socket

RECEIVER_ADDRESS = ("127.0.0.1", 8080)
T_SENDER_SYN = 2000
AES_KEY = b''
RSA_PUBLIC_KEY = b''
x = ' '

#init socket
def socket_init():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  return sock

#get rsa public key
def get_RSA_PUBLIC_KEY(key):
  global RSA_PUBLIC_KEY
  RSA_PUBLIC_KEY = key
#get aes key
def get_AES_KEY(key):
  global AES_KEY
  AES_KEY = key
  
#generate a json with msg and it's checksum
def create_json(msg_from_sender):
  encoded_msg_from_sender = str.encode(msg_from_sender)
  #checksum
  chksm = hashlib.sha1(encoded_msg_from_sender).hexdigest()
  #return dict with msg, checksum and type that cand be msg_checksum either fin(terminate connection)
  #encrypt json
  json_to_send = encrypt_json(msg_from_sender, chksm, 'msg_checksum', RSA_PUBLIC_KEY, AES_KEY)
  #convert json el from bytes to str
  json_to_send = convert_json_el_to_str(json_to_send)
  #convert to json and bytes
  json_to_send = json_bytes_dumps(json_to_send)

  return json_to_send

#verify receiver response on validity of checksum
def verify_chksum(sock):
  msg_from_receiver = sock.recvfrom(BUFFER_SIZE)
  if msg_from_receiver[0] == b'invalid_msg':
    #retransmission
    return "invalid_msg"
  else:
    #send msg from receiver
    return msg_from_receiver[0]

#send json to receiver and verify chksm
def send_recv_msg(sender, MSG_FROM_SENDER):
  #create dict with msg and cheksum
  json_to_send = create_json(MSG_FROM_SENDER)
  #udp connection
  if sender.handshake:
    while True:
      #send to receiver
      sender.sock.sendto(json_to_send, RECEIVER_ADDRESS)
      #based on recv from receiver, check if data is valid
      recv_msg = verify_chksum(sender.sock)
      if recv_msg == "invalid_msg":
        print(x * 10 + "Invalid msg, retransmitting message.")
      else:
        #print msg form receiver
        print("Valid msg.")
        print("Message from Receiver: ", recv_msg)
        break

#send to receiver to stop connection by sending a SYN and waiting for and updated ACK
def terminate_receiver_connection(sock):
  while True:
    #send a json with type fin
    t_sender_header = Header(T_SENDER_SYN, None)
    t_sender_header = t_sender_header.get_header_data()
    t_sender_header['type'] = 'fin'

    t_sender_header = json_bytes_dumps(t_sender_header)
    sock.sendto(t_sender_header, RECEIVER_ADDRESS)
    #receive and updated ACK
    t_recv = sock.recvfrom(BUFFER_SIZE)[0]
    t_recv = json_bytes_loads(t_recv)
    
    if t_recv['ACK'] == T_SENDER_SYN + 1:
      t_sender_header = Header(t_recv['SYN'], t_recv['ACK'])
      t_sender_header.change_SYN_with_ACK()
      t_sender_header.increment_ACK()
      t_sender_header = t_sender_header.get_header_data()
      t_sender_header = json_bytes_dumps(t_sender_header)
      sock.sendto(t_sender_header, RECEIVER_ADDRESS)
      print(x * 10 + "Connection terminated")
      break
    else:
      print(x * 10 + "Error during canceling connection.")

def terminate_sender_connection(sock):
  t_sender_conn = {'type':'fin sender'}
  t_sender_conn = json_bytes_dumps(t_sender_conn)
  sock.sendto(t_sender_conn, RECEIVER_ADDRESS)
