from protocol.receiver import Receiver
from protocol.library.receiver.protocol_receiver import recv_from_sender_and_verify, accept_incoming
from threading import Thread

x = ' '

def new_clients(receiver):
  while True:
    sender_address = accept_incoming(receiver.sock, receiver.RSA_PUBLIC_KEY)
    if sender_address is not False:
      print(x * 10 + "SENDER CONNECTED WITH ADDRESS:", sender_address)
      Thread(target=recv_from_sender_and_verify, args=(receiver.sock, receiver.RSA_PRIVATE_KEY)).start()


if __name__ == "__main__":
  receiver = Receiver()
  # todo: a listen method witch has a parameter of how many clients/threads will be
  # new_clients(receiver)
  accept_thread = Thread(target=new_clients, args=(receiver,))
  accept_thread.start()
  accept_thread.join()