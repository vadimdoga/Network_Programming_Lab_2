from library.protocol_header import Header
from library.protocol_library_crypto import encrypt_json
from library.protocol_library import json_bytes_dumps, json_bytes_loads, convert_json_el_to_str
from library.protocol_library import BUFFER_SIZE
import hashlib, socket

i = 0
SERVER_ADDRESS = ("127.0.0.1", 8080)
# MSG_FROM_CLIENT = "sdasdjadfkasdashdjasdJASDNosajshfASJDsdoADSoajsdOADHOahdoihwdoaehfjkasdkjashdkjashdkjahdkjhaskdjhkasjhdkajsdkjaskjdaskjdhkajshdkajsdhkjashdkahakjsdhkassa,dnbaskdbkhaskhasdkassdadasdadaadasasaasdasdasmasdasdasdaasdas"
MSG_FROM_CLIENT = "hello from client"
T_CLIENT_SYN = 2000
CLIENT_SYN = 4320
RSA_PUBLIC_KEY = b''
AES_KEY = b''

#init socket
def socket_init():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  return sock
  
#generate a json with msg and it's checksum
def create_json(msg_from_client, bool):
  encoded_msg_from_client = str.encode(msg_from_client)
  #false cheksum and true checksum
  if bool:
    chksm = hashlib.sha1(encoded_msg_from_client).hexdigest()
  else:
    chksm = hashlib.sha1(b"encoded_msg_from_client").hexdigest()
  #return dict with msg, checksum and type that cand be msg_checksum either fin(terminate connection)
  #encrypt json
  json_to_send = encrypt_json(msg_from_client, chksm, 'msg_checksum', RSA_PUBLIC_KEY, AES_KEY)
  #convert json el from bytes to str
  json_to_send = convert_json_el_to_str(json_to_send)
  #convert to json and bytes
  json_to_send = json_bytes_dumps(json_to_send)

  return json_to_send

#verify server response on validity of checksum
def verify_chksum(sock):
  msg_from_server = sock.recvfrom(BUFFER_SIZE)
  if msg_from_server[0] == b'invalid_msg':
    #retransmission
    return "invalid_msg"
  else:
    #send msg from server
    return msg_from_server[0]

#send json to server and verify chksm
def send_recv_msg(client):
  global i
  #create dict with msg and cheksum
  json_to_send = create_json(MSG_FROM_CLIENT, False)
  #udp connection
  if client.handshake:
    while True:
      if i == 5:
        json_to_send = create_json(MSG_FROM_CLIENT, True)
      #send to server
      client.sock.sendto(json_to_send, SERVER_ADDRESS)
      #based on recv from server, check if data is valid
      recv_msg = verify_chksum(client.sock)
      if recv_msg == "invalid_msg":
        print("Invalid msg, retransmitting message.")
      else:
        #print msg form server
        print("Valid msg.")
        print("Message from Server: ", recv_msg)
        break
      i = i + 1

#client handshake
#send client SYN to server side
def initial_SYN():
  client_header = Header(CLIENT_SYN, None).get_header_data()
  client_header = json_bytes_dumps(client_header)
  return client_header
#receive server SYN and updated ACK and send client updated client ACK
def process_header(client_header):
  client_header = Header(client_header['SYN'], client_header['ACK'])
  client_header.change_SYN_with_ACK()
  client_header.increment_ACK()
  client_header = client_header.get_header_data()

  client_header = json_bytes_dumps(client_header)
  return client_header
#receive from server SYN and ACK and verify ACK
def verify_connection(sock):
  global RSA_PUBLIC_KEY
  recv_from_server = sock.recvfrom(BUFFER_SIZE)
  client_header = recv_from_server[0]
  client_header = json_bytes_loads(client_header)
  #get public key
  if 'RSA_PUBLIC_KEY' in client_header:
    RSA_PUBLIC_KEY = client_header['RSA_PUBLIC_KEY']
    RSA_PUBLIC_KEY = str.encode(RSA_PUBLIC_KEY)
  #if true, connection established
  if client_header['ACK'] == (CLIENT_SYN + 1):
    client_header = process_header(client_header)
    sock.sendto(client_header, SERVER_ADDRESS)
    return True
  else:
    return False
#client handshake
def establish_connection(sock, key):
  global AES_KEY
  AES_KEY = key

  client_header = initial_SYN()
  sock.sendto(client_header, SERVER_ADDRESS)

  verify = verify_connection(sock)
  if verify:
    print("Connection established")
    return True
  else:
    print("Connection failed")
    return False
#send to server to stop connection by sending a SYN and waiting for and updated ACK
def terminate_connection(sock):
  while True:
    #send a json with type fin
    t_client_header = Header(T_CLIENT_SYN, None)
    t_client_header = t_client_header.get_header_data()
    t_client_header['type'] = 'fin'

    t_client_header = json_bytes_dumps(t_client_header)
    sock.sendto(t_client_header, SERVER_ADDRESS)
    #receive and updated ACK
    t_recv = sock.recvfrom(BUFFER_SIZE)[0]
    t_recv = json_bytes_loads(t_recv)
    
    if t_recv['ACK'] == T_CLIENT_SYN + 1:
      t_client_header = Header(t_recv['SYN'], t_recv['ACK'])
      t_client_header.change_SYN_with_ACK()
      t_client_header.increment_ACK()
      t_client_header = t_client_header.get_header_data()
      t_client_header = json_bytes_dumps(t_client_header)
      sock.sendto(t_client_header, SERVER_ADDRESS)
      print("Connection terminated")
      break
    else:
      print("Error during canceling connection.")


