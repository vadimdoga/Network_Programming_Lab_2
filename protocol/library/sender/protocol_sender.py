from protocol.library.protocol_header import Header
from protocol.library.protocol_crypto import encrypt_json
from protocol.library.protocol_general import json_bytes_dumps, json_bytes_loads, convert_json_el_to_str, BUFFER_SIZE
import hashlib, socket, os, sys

RECEIVER_ADDRESS = ("127.0.0.1", int(sys.argv[2]))
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

def get_connected_clients(sock):
  get_clients_json = {'type':'get clients'}
  get_clients_json = json_bytes_dumps(get_clients_json)
  sock.sendto(get_clients_json, RECEIVER_ADDRESS)
  
#generate a json with msg and it's checksum
def create_json(msg_from_sender, type_of_sending, send_to_address):
  encoded_msg_from_sender = str.encode(msg_from_sender)
  #checksum
  chksm = hashlib.sha1(encoded_msg_from_sender).hexdigest()
  #return dict with msg, checksum and type that cand be msg_checksum either fin(terminate connection)
  #encrypt json
  json_to_send = encrypt_json(msg_from_sender, chksm, 'msg_checksum', RSA_PUBLIC_KEY, AES_KEY, type_of_sending, send_to_address)
  #convert json el from bytes to str
  json_to_send = convert_json_el_to_str(json_to_send)
  #convert to json and bytes
  json_to_send = json_bytes_dumps(json_to_send)

  return json_to_send
     
#broadcast json to receiver 
def send_msg(sender, MSG_FROM_SENDER, type_of_sending, PORT):
  if type_of_sending == 'broadcast':
    send_to_address = ''
  else:
    send_to_address = ("127.0.0.1", PORT)
  #create dict with msg and cheksum
  json_to_send = create_json(MSG_FROM_SENDER, type_of_sending, send_to_address)

  #udp connection
  if sender.handshake:
    #send to receiver
    sender.sock.sendto(json_to_send, RECEIVER_ADDRESS)
      
#verify receiver response on validity of checksum
def verify_chksum(msg_from_receiver, sender):
  if 'type' in msg_from_receiver:
    if msg_from_receiver['type'] == 'msg':
      #print message in console
      print("\n{} ".format(msg_from_receiver['sender']), msg_from_receiver['msg'])
    elif msg_from_receiver['type'] == 'client_disc':
      #when client disconnects
      print(x * 15 + "{} DISCONNECTED".format(msg_from_receiver['SENDER_ADDRESS']))
    elif msg_from_receiver['type'] == 'client_conn':
      #when client connects to server
      print(x * 15 + "{} CONNECTED".format(msg_from_receiver['SENDER_ADDRESS']))
    elif msg_from_receiver['type'] == 'server_disc':
      #when client stops server
      print(x * 15 + "CONNECTION TERMINATED")
      os._exit(0)
    elif msg_from_receiver['type'] == 'get clients':
      print("\nCONNECTED CLIENTS: {}".format(msg_from_receiver['clients']))
    elif msg_from_receiver['type'] == 'invalid port':
      print(x * 15 + "INVALID PORT. THE MESSAGE WAS NOT SENT.")
    
    #if invalid message retransmit
    elif msg_from_receiver['type'] == 'invalid_msg':
      #retransmission
      print(x * 10 + "Invalid msg, retransmitting message.")
      #retransimssion based on type of sending
      if msg_from_receiver['type_of_sending'] == 'broadcast':
        #send msg with type broadcast
        send_msg(sender, msg_from_receiver['msg'], msg_from_receiver['type_of_sending'], '')
      elif msg_from_receiver['type_of_sending'] == 'send':
        #send msg with type send
        r_PORT = msg_from_receiver['send_to_address'][1]
        send_msg(sender, msg_from_receiver['msg'], msg_from_receiver['type_of_sending'], r_PORT)

def recv_msg(sender):
  if sender.handshake:
    print("||===================================MESSAGES====================================||")
    while True:
      msg_from_receiver = sender.sock.recvfrom(BUFFER_SIZE)
      msg_from_receiver = json_bytes_loads(msg_from_receiver[0])

      #based on recv from receiver, check if data is valid
      verify_chksum(msg_from_receiver, sender)
      
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
#exits client server still wokring
def terminate_sender_connection(sock):
  t_sender_conn = {'type':'fin sender'}
  t_sender_conn = json_bytes_dumps(t_sender_conn)
  sock.sendto(t_sender_conn, RECEIVER_ADDRESS)
