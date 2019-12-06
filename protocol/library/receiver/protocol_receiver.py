from protocol.library.protocol_header import Header
from protocol.library.protocol_crypto import decrypt_json
from protocol.library.protocol_general import convert_json_el_to_byte, json_bytes_dumps, json_bytes_loads, BUFFER_SIZE
from protocol.library.receiver.protocol_receiver_header import establish_connection, add_senders_to_array, get_connected_senders, remove_sender_from_array
import os
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

#incoming recv which is analyzed and structured 
def accept_incoming(sock, RSA_PUBLIC_KEY, max_nr_of_clients):
  #general recv
  recv = sock.recvfrom(BUFFER_SIZE)
  SENDER_ADDRESS = recv[1]
  
  # 1.establishes the connection 
  if SENDER_ADDRESS not in get_connected_senders():
    #if nr of connected clients is not max
    if len(get_connected_senders()) < max_nr_of_clients:
      #establish connection
      connection_result = establish_connection(sock, RSA_PUBLIC_KEY, recv)
      #add sender to array
      add_senders_to_array(connection_result['SENDER_ADDRESS'])
      return connection_result
    
    #if nr of connected clients is max
    else:
      sock.sendto(b'max limit', SENDER_ADDRESS)
      return 'nothing'

  # 2.if already connected send recv from buffer to recv_and_verify method for future process
  else:
    return {
      'recv': recv
    }

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
def receive_from_sender(sock, RSA_PRIVATE_KEY, recv_object):
  #retrieve from parameters recv
  recv_from_sender = recv_object

  SENDER_ADDRESS = recv_from_sender[1]
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
      'address': SENDER_ADDRESS
    }
  #if type is fin then receiver acknowledges that it's terminate command(server terminates)
  elif json_from_sender['type'] == 'fin':
    #todo:send to all that server is closed
    #all the ACK SYN process
    termination = terminate_receiver_connection(sock, json_from_sender, SENDER_ADDRESS)
    if termination:
      # if true make a copy of array and delete all connection from it
      senders = get_connected_senders()
      senders_array_copy = []
      for sender in senders:
        senders_array_copy.append(sender)
      for sender in senders_array_copy:
        terminate_sender_connection(sender)
      os._exit(0)
  # sender terminates connection
  elif json_from_sender['type'] == 'fin sender':
    #todo: send to all that sender disconected
    termination = terminate_sender_connection(SENDER_ADDRESS)
    print("CONNECTED CLIENTS: ", get_connected_senders())
    if termination:
      return 'fin sender'
 
def recv_from_sender_and_verify(sock, RSA_PRIVATE_KEY, recv_object):
  #recv from sender
  recv = receive_from_sender(sock, RSA_PRIVATE_KEY, recv_object)
  if 'msg' in recv:
    #verify the cheksum
    #if chksm not valid retransmit
    verify_chksm(sock, recv['msg'], recv['chksm'], recv['address'])
    
#recv fin and terminate connection
def terminate_receiver_connection(sock, t_recv, SENDER_ADDRESS):
  while True:
    #receives SYN from sender and send updated ACK to sender for it to stop
    t_send_header = Header(t_recv['SYN'], T_RECEIVER_SYN)
    t_send_header.change_SYN_with_ACK()
    t_send_header.increment_ACK()
    t_send_header = t_send_header.get_header_data()
    t_send_header = json_bytes_dumps(t_send_header)
    sock.sendto(t_send_header, SENDER_ADDRESS)

    t_recv = sock.recvfrom(BUFFER_SIZE)[0]
    t_recv = json_bytes_loads(t_recv)

    if t_recv['ACK'] == T_RECEIVER_SYN + 1: 
      print(x * 10 + "Connection terminated")
      return True
    else:
      print(x * 10 + "Error during stopping connection.")
      return False

#terminate sender conenction
def terminate_sender_connection(SENDER_ADDRESS):
  if SENDER_ADDRESS in get_connected_senders():
    remove_sender_from_array(SENDER_ADDRESS)
    if SENDER_ADDRESS not in get_connected_senders():
      print(x * 10 + "SENDER DISCONNECTED FROM SERVER:", SENDER_ADDRESS)
      return True
