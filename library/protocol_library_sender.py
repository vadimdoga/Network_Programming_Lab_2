from library.protocol_header import Header
from library.protocol_library_crypto import encrypt_json
from library.protocol_library import json_bytes_dumps, json_bytes_loads, convert_json_el_to_str
from library.protocol_library import BUFFER_SIZE
import hashlib, socket

i = 0
RECEIVER_ADDRESS = ("127.0.0.1", 8080)
# MSG_FROM_SENDER = "sdasdjadfkasdashdjasdJASDNosajshfASJDsdoADSoajsdOADHOahdoihwdoaehfjkasdkjashdkjashdkjahdkjhaskdjhkasjhdkajsdkjaskjdaskjdhkajshdkajsdhkjashdkahakjsdhkassa,dnbaskdbkhaskhasdkassdadasdadaadasasaasdasdasmasdasdasdaasdas"
MSG_FROM_SENDER = "hello from sender"
T_SENDER_SYN = 2000
SENDER_SYN = 4320
RSA_PUBLIC_KEY = b''
AES_KEY = b''

#init socket
def socket_init():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  return sock
  
#generate a json with msg and it's checksum
def create_json(msg_from_sender, bool):
  encoded_msg_from_sender = str.encode(msg_from_sender)
  #false cheksum and true checksum
  if bool:
    chksm = hashlib.sha1(encoded_msg_from_sender).hexdigest()
  else:
    chksm = hashlib.sha1(b"encoded_msg_from_sender").hexdigest()
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
def send_recv_msg(sender):
  global i
  #create dict with msg and cheksum
  json_to_send = create_json(MSG_FROM_SENDER, False)
  #udp connection
  if sender.handshake:
    while True:
      if i == 5:
        json_to_send = create_json(MSG_FROM_SENDER, True)
      #send to receiver
      sender.sock.sendto(json_to_send, RECEIVER_ADDRESS)
      #based on recv from receiver, check if data is valid
      recv_msg = verify_chksum(sender.sock)
      if recv_msg == "invalid_msg":
        print("Invalid msg, retransmitting message.")
      else:
        #print msg form receiver
        print("Valid msg.")
        print("Message from Receiver: ", recv_msg)
        break
      i = i + 1

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
  global RSA_PUBLIC_KEY
  recv_from_receiver = sock.recvfrom(BUFFER_SIZE)
  sender_header = recv_from_receiver[0]
  sender_header = json_bytes_loads(sender_header)
  #get public key
  if 'RSA_PUBLIC_KEY' in sender_header:
    RSA_PUBLIC_KEY = sender_header['RSA_PUBLIC_KEY']
    RSA_PUBLIC_KEY = str.encode(RSA_PUBLIC_KEY)
  #if true, connection established
  if sender_header['ACK'] == (SENDER_SYN + 1):
    sender_header = process_header(sender_header)
    sock.sendto(sender_header, RECEIVER_ADDRESS)
    return True
  else:
    return False
#sender handshake
def establish_connection(sock, key):
  global AES_KEY
  AES_KEY = key

  sender_header = initial_SYN()
  sock.sendto(sender_header, RECEIVER_ADDRESS)

  verify = verify_connection(sock)
  if verify:
    print("Connection established")
    return True
  else:
    print("Connection failed")
    return False
#send to receiver to stop connection by sending a SYN and waiting for and updated ACK
def terminate_connection(sock):
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
      print("Connection terminated")
      break
    else:
      print("Error during canceling connection.")


