#handshake header
class Header:
  def __init__(self, SYN, ACK):
    self.SYN = SYN
    self.ACK = ACK
  def get_header_data(self):
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
