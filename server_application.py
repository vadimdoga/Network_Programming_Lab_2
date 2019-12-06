from protocol.receiver import Receiver
from protocol.library.receiver.protocol_receiver import recv_from_sender_and_verify, accept_incoming, get_connected_senders
from concurrent.futures import ThreadPoolExecutor

x = ' '

def join_clients(receiver, max_nr_of_clients):
  while True:
    connection_result = accept_incoming(receiver.sock, receiver.RSA_PUBLIC_KEY, max_nr_of_clients)
    if 'SENDER_ADDRESS' in connection_result:
      SENDER_ADDRESS = connection_result['SENDER_ADDRESS']
      print(x * 10 + "SENDER CONNECTED WITH ADDRESS:", SENDER_ADDRESS)
      print("CONNECTED CLIENTS: ", get_connected_senders())
    elif 'recv' in connection_result:
      with ThreadPoolExecutor(max_workers=5) as executor:
        executor.submit(recv_from_sender_and_verify, receiver.sock, receiver.RSA_PRIVATE_KEY, connection_result['recv'])

if __name__ == "__main__":
  receiver = Receiver()
  #parameters receiver and max nr of clients that can connect
  join_clients(receiver, 3)