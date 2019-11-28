#handshake header
class Header:
  def __init__(self, SYN, ACK):
    self.SYN = SYN
    self.ACK = ACK
    self.public_key = 0
  def get_header_data(self):
    if self.public_key != 0:
      return {
        'SYN': self.SYN,
        'ACK': self.ACK,
        'RSA_PUBLIC_KEY': self.public_key
      }
    else:
      return {
        'SYN': self.SYN,
        'ACK': self.ACK
      }
  def increment_ACK(self):
    self.ACK = self.ACK + 1
  def change_SYN_with_ACK(self):
    temp = self.ACK
    self.ACK = self.SYN
    self.SYN = temp
  def add_rsa_public_key(self, public_key):
    self.public_key = public_key

