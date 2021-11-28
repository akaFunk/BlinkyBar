# This file represents the connection to the AVR on the main module
# The class AvrCtrl provides all function required regarding the power
# management and trigger pin control.

import time
import spidev
import ctypes

class AvrCtrl:
    class Message(ctypes.LittleEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("command", ctypes.c_ubyte),
            ("period", ctypes.c_uint16),
            ("on_time", ctypes.c_uint16),
            ("trigger_count", ctypes.c_uint16)
        ]

    class Answer(ctypes.LittleEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("magic0", ctypes.c_ubyte),
            ("voltage", ctypes.c_uint16),
            ("timer_counter", ctypes.c_uint16),
            ("shutdown", ctypes.c_ubyte),
            ("magic1", ctypes.c_ubyte)
        ]

    def __init__(self, bus:int=1, device:int=0) -> None:
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 10000  # We need a fairly low speed for the AVR to keep up
        self.spi.mode = 0

        # Default settings
        self.msg = self.Message()
        self.msg.period = 1000
        self.msg.on_time = 500
        self.msg.trigger_count = 10

    def _querry(self, start_flag:bool=False, stop_flag:bool=False) -> None:
        self.msg.command = (self.msg.command & 0x04) | (start_flag + stop_flag*2)
        data = bytearray(self.msg)
        resp = bytearray(self.spi.xfer2(data))
        ans = self.Answer.from_buffer_copy(resp)
        if ans.magic0 != 0x31 or ans.magic1 != 0x41:
            raise Exception(f"Got invalid answer from AVR: Wrong magic byte(s): 0x{ans.magic0:02x}/0x{ans.magic1:02x} instead of 0x31/0x41")
        return ans

    def set_values(self, period:int, on_time:int, trigger_count:int, infinite_repeat_flag:bool=False) -> None:
        self.msg.command = infinite_repeat_flag*4
        self.msg.period = period
        self.msg.on_time = on_time
        self.msg.trigger_count = trigger_count

    def set_period(self, period:int) -> None:
        self.msg.period = period

    def set_on_time(self, on_time:int) -> None:
        self.msg.on_time = on_time

    def set_trigger_count(self, trigger_count:int) -> None:
        self.msg.trigger_count = trigger_count

    def set_infinite_repeat(self, infinite_repeat:bool) -> None:
        self.msg.command = infinite_repeat*4

    def start_trigger(self) -> None:
        self._querry(True)

    def stop_trigger(self) -> None:
        self._querry(False, True)

    def get_voltage(self) -> float:
        ans = self._querry()
        return ans.voltage/1000.0

    def get_shutdown(self) -> bool:
        ans = self._querry()
        return bool(ans.shutdown)

    def get_timer_counter(self) -> int:
        ans = self._querry()
        return int(ans.timer_counter)

# The script can be run directly, but this is just for tests and debugging
def main():
    avrctrl = AvrCtrl(1, 0)
    #avrctrl._querry()
    print(f"Voltage: {avrctrl.get_voltage()}")
    avrctrl.set_values(2000, 500, 12, True)
    while True:
        print(avrctrl.get_shutdown())
        time.sleep(0.2)
    avrctrl.start_trigger()
    time.sleep(5)
    avrctrl.stop_trigger()


if __name__ == "__main__":
    main()
