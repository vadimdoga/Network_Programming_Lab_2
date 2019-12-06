from protocol.receiver import Receiver
from protocol.library.receiver.protocol_receiver import recv_from_sender_and_verify, accept_incoming
from threading import Thread

x = ' '

def join_clients(receiver):
  while True:
    print(0)
    connection_result = accept_incoming(receiver.sock, receiver.RSA_PUBLIC_KEY)
    if 'sender_address' in connection_result:
      sender_address = connection_result['sender_address']
      print(x * 10 + "SENDER CONNECTED WITH ADDRESS:", sender_address)
    elif 'recv' in connection_result:
      print(1)
      Thread(target=recv_from_sender_and_verify, args=(receiver.sock, receiver.RSA_PRIVATE_KEY, connection_result['recv'])).start()


if __name__ == "__main__":
  receiver = Receiver()
  # todo: a listen method witch has a parameter of how many clients/threads will be
  # join_clients(receiver)
  Thread(target=join_clients, args=(receiver,)).start()