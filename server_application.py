from protocol.receiver import Receiver
from protocol.library.receiver.protocol_receiver import recv_from_sender_and_verify

if __name__ == "__main__":
  receiver = Receiver()
  #wait recv from client
  recv_from_sender_and_verify(receiver)