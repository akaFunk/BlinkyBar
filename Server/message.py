from enum import Enum
import numpy as np

MESSAGE_MAX_DATA_SIZE        = 256
MESSAGE_MAGIC                = 0xab

#class MessageAddr(Enum):
MESSAGE_ADDR_BROADCAST   = 0xff
MESSAGE_ADDR_HOST        = 0xfe

#class MessageType(Enum):
MESSAGE_TYPE_RET_RST     = 0x00
MESSAGE_TYPE_ADDR        = 0x02
MESSAGE_TYPE_RET_SET     = 0x01
MESSAGE_TYPE_PING        = 0x10
MESSAGE_TYPE_STAT        = 0x20
MESSAGE_TYPE_DEL         = 0x30
MESSAGE_TYPE_DATA        = 0x31
MESSAGE_TYPE_PREP        = 0x40
MESSAGE_TYPE_ACK         = 0xf0
MESSAGE_TYPE_NACK        = 0xf1

class Message:
    def __init__(self, type = MESSAGE_TYPE_NACK, data = np.array([], dtype=np.uint8), dst = MESSAGE_ADDR_HOST):
        self.magic = MESSAGE_MAGIC
        self.type = type
        self.src = MESSAGE_ADDR_HOST
        self.dst = 0
        self.data = np.array([], dtype=np.uint8)

    def to_bytes(self):
        ret = b''
        ret += bytes([self.magic])
        ret += bytes([self.type])
        ret += bytes([self.src])
        ret += bytes([self.dst])
        ret += bytes([len(self.data)%256])
        ret += bytes([round(len(self.data)/256)])
        ret += bytes(self.data.tobytes())
        return ret
