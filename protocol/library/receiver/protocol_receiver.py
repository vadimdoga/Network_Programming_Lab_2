from protocol.library.protocol_header import Header
from protocol.library.protocol_crypto import decrypt_json
from protocol.library.protocol_general import convert_json_el_to_byte, json_bytes_dumps, json_bytes_loads, BUFFER_SIZE
from protocol.library.receiver.protocol_receiver_header import establish_connection, add_senders_to_array, get_connected_senders, remove_sender_from_array
import os, sys
import hashlib, socket

T_RECEIVER_SYN = 3000
RECEIVER_ADDRESS = ("127.0.0.1", int(sys.argv[2]))
x = ' '
i = 0

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
      #broadcast to all that somebody connected
      client_conn = {
        'SENDER_ADDRESS': connection_result['SENDER_ADDRESS'],
        'type': 'client_conn'
      }
      client_conn = json_bytes_dumps(client_conn)
      broadcast(sock, client_conn)
      #add sender to array
      add_senders_to_array(connection_result['SENDER_ADDRESS'])
      return connection_result
    
    #if nr of connected clients is max
    else:
      print(x * 15 + "MAXIMUM LIMIT")
      max_limit = {
        'type': 'max limit'
      }
      max_limit = json_bytes_dumps(max_limit)
      sock.sendto(max_limit, SENDER_ADDRESS)
      return 'nothing'

  # 2.if already connected send recv from buffer to recv_and_verify method for future process
  else:
    return {
      'recv': recv
    }

#verify checksum on receiver side
def verify_chksm(sock, MSG_FROM_SENDER, chksm, SENDER_ADDRESS, type_of_sending, send_to_address):
  global i
  #error msg-s depending on type
  if type_of_sending == 'broadcast':
    ERROR_MSG = json_bytes_dumps({
      'msg': MSG_FROM_SENDER,
      'type': 'invalid_msg',
      'type_of_sending': type_of_sending
    })
  elif type_of_sending == 'send':
    ERROR_MSG = json_bytes_dumps({
      'msg': MSG_FROM_SENDER,
      'type': 'invalid_msg',
      'type_of_sending': type_of_sending,
      'send_to_address': send_to_address
    })
  
  #hash msg and verify if it's equal with checksum
  hashed_msg = str.encode(MSG_FROM_SENDER)
  i = i + 1
  if i > 5:
    hashed_msg = hashlib.sha1(hashed_msg).hexdigest()
  else:
    hashed_msg = hashlib.sha1(b'hashed_msg').hexdigest()

  if chksm != hashed_msg:
    #if not valid send to sender error msg
    sock.sendto(ERROR_MSG, SENDER_ADDRESS)
    print("Invalid Message, waiting for retransmission.")
    return False
  else:
    #if valid return true
    print("Valid Message")
    print("Message from {}: ".format(SENDER_ADDRESS), MSG_FROM_SENDER)
    return True

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
    type_of_sending = json_from_sender['type_of_sending']
    send_to_address = json_from_sender['send_to_address']

    return {
      'msg': msg,
      'chksm': chksm,
      'SENDER_ADDRESS': SENDER_ADDRESS,
      'type_of_sending': type_of_sending,
      'send_to_address': send_to_address
    }
  #get connected clients method
  elif json_from_sender['type'] == 'get clients':
    conn_clients = {
      'clients': get_connected_senders(),
      'type': 'get clients'
    }
    conn_clients = json_bytes_dumps(conn_clients)
    sock.sendto(conn_clients, SENDER_ADDRESS)
  #if type is fin then receiver acknowledges that it's terminate command(server terminates)
  elif json_from_sender['type'] == 'fin':
    #all the ACK SYN process
    termination = terminate_receiver_connection(sock, json_from_sender, SENDER_ADDRESS)
    if termination:
      # if true make a copy of array and delete all connection from it
      senders = get_connected_senders()
      #broadcast to all that server is closed and they need to disconnect
      server_disc = {
        'type': 'server_disc'
      }
      server_disc = json_bytes_dumps(server_disc)
      #broadcast to all
      broadcast(sock, server_disc)

      senders_array_copy = []
      for sender in senders:
        senders_array_copy.append(sender)
      for sender in senders_array_copy:
        terminate_sender_connection(sender)

      os._exit(0)
  # sender terminates connection
  elif json_from_sender['type'] == 'fin sender':
    termination = terminate_sender_connection(SENDER_ADDRESS)
    print("CONNECTED CLIENTS: ", get_connected_senders())
    if termination:
      client_disc = {
        'SENDER_ADDRESS': SENDER_ADDRESS,
        'type': 'client_disc'
      }
      client_disc = json_bytes_dumps(client_disc)
      broadcast(sock, client_disc)
 
def recv_from_sender_and_verify(sock, RSA_PRIVATE_KEY, recv_object):
  #recv from sender
  recv = receive_from_sender(sock, RSA_PRIVATE_KEY, recv_object)
  if 'msg' in recv:
    #verify the cheksum
    #if chksm not valid retransmit
    verification = verify_chksm(sock, recv['msg'], recv['chksm'], recv['SENDER_ADDRESS'], recv['type_of_sending'], recv['send_to_address'])
    if verification:
      #broadcast
      if recv['type_of_sending'] == 'broadcast':
        valid_msg = recv['msg']
        valid_json = {
          'msg': valid_msg,
          'type': 'msg',
          'sender': recv['SENDER_ADDRESS']
        }
        valid_json = json_bytes_dumps(valid_json)
        broadcast(sock, valid_json)
      #send to specific client
      elif recv['type_of_sending'] == 'send':
        ADDRESS = recv['send_to_address'][0]
        PORT = recv['send_to_address'][1]
        SEND_TO_ADDRESS = (ADDRESS, PORT)
        if SEND_TO_ADDRESS in get_connected_senders():
          valid_msg = recv['msg']
          valid_json = {
            'msg': valid_msg,
            'type': 'msg',
            'sender': recv['SENDER_ADDRESS']
          }
          valid_json = json_bytes_dumps(valid_json)
          sock.sendto(valid_json, SEND_TO_ADDRESS)
        #if in send method the port was invalid
        else:
          valid_json = {
            'type': 'invalid port'
          }
          valid_json = json_bytes_dumps(valid_json)
          print("Such address does not exist!")
          sock.sendto(valid_json, recv['SENDER_ADDRESS'])

#broadcast method
def broadcast(sock, msg):
  connected_clients = get_connected_senders()
  for client in connected_clients:
    sock.sendto(msg, client)

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
