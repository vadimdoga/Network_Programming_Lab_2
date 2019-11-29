from library.protocol_header import Header
from library.protocol_library_crypto import decrypt_json
from library.protocol_library import convert_json_el_to_byte, json_bytes_dumps, json_bytes_loads, BUFFER_SIZE
import hashlib

ERROR_MSG = b"invalid_msg"
SERVER_ACK = 5320
T_SERVER_SYN = 3000
MSG_FROM_SERVER = b"Successful packet transmission"
RSA_PUBLIC_KEY = b""
RSA_PRIVATE_KEY = b""

#verify checksum on server side
def verify_chksm(sock, MSG_FROM_CLIENT, chksm, address):
  print(MSG_FROM_CLIENT)
  #hash msg and verify if it's equal with checksum
  hashed_msg = str.encode(MSG_FROM_CLIENT)
  hashed_msg = hashlib.sha1(hashed_msg).hexdigest()
  if chksm != hashed_msg:
    #if not valid send to client error msg
    sock.sendto(ERROR_MSG, address)
    print("Invalid Message, waiting for retransmission.")
  else:
    #if valid send to client msg from server
    sock.sendto(MSG_FROM_SERVER, address)
    print("Valid Message")
    print("Message from Client: ", MSG_FROM_CLIENT)
#receive on server side
def receive_from_client(sock):
  global RSA_PRIVATE_KEY
  recv_from_client = sock.recvfrom(BUFFER_SIZE)
  client_address = recv_from_client[1]

  json_from_client = recv_from_client[0]
  json_from_client = json_bytes_loads(json_from_client)
  
  #if type is msg_checksum then server receives a dict with msg,chksm,address
  if json_from_client['type'] == 'msg_checksum':
    #convert json el from str to byte
    json_from_client = convert_json_el_to_byte(json_from_client)
    #decrypt json
    json_from_client = decrypt_json(json_from_client, RSA_PRIVATE_KEY)

    msg = json_from_client["msg"]
    chksm = json_from_client['chksm']

    return {
      'msg': msg,
      'chksm': chksm,
      'address': client_address
    }
  #if type is fin then server acknowledges that it's terminate command
  elif json_from_client['type'] == 'fin':
    while True:
      t_recv = json_from_client
      #receives SYN from client and send updated ACK to client for it to stop
      t_send_header = Header(t_recv['SYN'], T_SERVER_SYN)
      t_send_header.change_SYN_with_ACK()
      t_send_header.increment_ACK()
      t_send_header = t_send_header.get_header_data()
      t_send_header = json_bytes_dumps(t_send_header)
      sock.sendto(t_send_header, client_address)

      t_recv = sock.recvfrom(BUFFER_SIZE)[0]
      t_recv = json_bytes_loads(t_recv)

      if t_recv['ACK'] == T_SERVER_SYN + 1: 
        print("Connection terminated")
        return 'fin'
      else:
        print("Error during stopping connection.")


#server handshake
#receive from client SYN. Change SYN with ACK and send update ACK with server SYN
def process_header(server_header, client_address):
  global RSA_PUBLIC_KEY
  print("Client ", client_address, " connected")
  server_header = json_bytes_loads(server_header)
  #header class
  server_header = Header(server_header['SYN'], SERVER_ACK)
  server_header.change_SYN_with_ACK()
  server_header.increment_ACK()
  server_header.add_rsa_public_key(RSA_PUBLIC_KEY)
  server_header = server_header.get_header_data()

  server_header = json_bytes_dumps(server_header)
  return server_header
#receive updated ACK from client to confirm connection
def verify_connection(server_header):
  server_header = json_bytes_loads(server_header)

  if server_header['ACK'] == (SERVER_ACK + 1):
    print("Connection established")
    return True
  else:
    return False
def establish_connection(sock, PUBLIC_KEY, PRIVATE_KEY):
  global RSA_PUBLIC_KEY
  global RSA_PRIVATE_KEY
  RSA_PUBLIC_KEY = PUBLIC_KEY
  RSA_PRIVATE_KEY = PRIVATE_KEY
  while True:
    server_header, client_address = sock.recvfrom(BUFFER_SIZE)
    #recv SYN send server SYN and updated ACK
    server_header = process_header(server_header, client_address)
    sock.sendto(server_header, client_address)

    recv_from_client = sock.recvfrom(BUFFER_SIZE)
    server_header = recv_from_client[0]
    #recv updated ACK and based on it decide if connection established
    verify = verify_connection(server_header)
    if verify:
      break

    
def wait_from_client(server):
  while True:
    #recv dict from client
    recv = receive_from_client(server.sock)
    if recv == 'fin':
      break
    else:
      #verify the cheksum
      #if chksm not valid retransmit
      verify_chksm(server.sock, recv['msg'], recv['chksm'], recv['address'])
        


