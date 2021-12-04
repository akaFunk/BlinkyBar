from enum import Enum
import numpy as np
import math

MESSAGE_MAX_DATA_SIZE    = 256
MESSAGE_MAGIC            = 0xab

#class MessageAddr(Enum):
MESSAGE_ADDR_BROADCAST   = 0xff
MESSAGE_ADDR_HOST        = 0xfe

#class MessageType(Enum):
MESSAGE_TYPE_ADDR_SET    = 0x00
MESSAGE_TYPE_RET_DISABLE = 0x10
MESSAGE_TYPE_RET_ENABLE  = 0x11
MESSAGE_TYPE_PING        = 0x20
MESSAGE_TYPE_STAT        = 0x30
MESSAGE_TYPE_IMG_NEW     = 0x40
MESSAGE_TYPE_IMG_APP     = 0x41
MESSAGE_TYPE_PREP        = 0x50
MESSAGE_TYPE_TRIG        = 0x51
MESSAGE_TYPE_PIXEL_MODE  = 0x60
MESSAGE_TYPE_ACK         = 0xf0
MESSAGE_TYPE_NACK        = 0xf1

class Message:
    def __init__(self, type = MESSAGE_TYPE_NACK, data = None, dst = MESSAGE_ADDR_HOST):
        self.magic = MESSAGE_MAGIC
        self.type = type
        self.src = MESSAGE_ADDR_HOST
        self.dst = dst
        if data is None:
            self.data = np.array([], dtype=np.uint8)
        else:
            self.data = np.array(data, dtype=np.uint8)

    def to_bytes(self):
        ret = b''
        ret += bytes([self.magic])
        ret += bytes([self.type])
        ret += bytes([self.src])
        ret += bytes([self.dst])
        ret += bytes([len(self.data)%256])
        ret += bytes([math.floor(len(self.data)/256)])
        ret += bytes(self.data.tobytes())
        return ret
