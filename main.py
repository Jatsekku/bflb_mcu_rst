from pylibftdi import BitBangDevice
import time
import argparse

class FtGPIO:
    def __init__(self,
                 device_id = 'A10KMJP6',
                 dts_logic = True,
                 rts_logic = True,
                 hold_boot = True):

        self._pins = {'TXD' : 0,
                      'RXD' : 1,
                      'RTS' : 2,
                      'CTS' : 3,
                      'DTR' : 4,
                      'DSR' : 5,
                      'DCD' : 6,
                      'RI'  : 7}

        self._bb_device = BitBangDevice(device_id)
        self._bb_device.direction = 0xFF
        self._boot_pin = 'DCD'
        self._en_pin = 'RI'
        self._hold_boot = hold_boot

        self.setBOOT(False)  #Low state at BOOT pin
        self.setRST(True)   #High state at RST pin
        time.sleep(0.5)

    def setGPIO(self, pin, pin_state):
        pin_state_str = ('High' if pin_state else 'Low')
        print(f"setGPIO({pin}, {pin_state_str})")
        if pin_state:
            self._bb_device.port |= (1<<self._pins[pin])
        else:
            self._bb_device.port &= ~(1<<self._pins[pin])

    def setBOOT(self, pin_state):
        pin_state_str = ('High' if pin_state else 'Low')
        print(f"setBOOT({pin_state_str})")
        self.setGPIO(self._boot_pin, pin_state)

    def setRST(self, pin_state):
        pin_state_str = ('High' if pin_state else 'Low')
        print(f"setRST({pin_state_str})")
        self.setGPIO(self._en_pin, not pin_state)

    def pulseRST(self):
        print('pulseRST()')
        self.setRST(False)
        time.sleep(1)
        self.setRST(True)
        time.sleep(0.1)

    def reset(self):
        self.setBOOT(False);
        self.pulseRST()

    def enterBootMode(self):
        print('enterBootMode()')
        self.setBOOT(True)  #High state at BOOT pin
        time.sleep(0.1)    #Wait for 10ms

        self.pulseRST()     #Actual reset of mcu

        if self._hold_boot is False:
            self.setBOOT(False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description =
                                     'Program written to enter boot mode\
                                      and reset BL702 MCU')
    parser.add_argument('-a',
                       '--action',
                       required = True,
                       help = 'Perform action: enterBoot (boot) or reset (rst)')

    parser.add_argument('-d',
                        '--device',
                        default= 'A10KMJP6',
                        type = str,
                        help = 'FT232\'s ID to connect')

    args = parser.parse_args()

    device = FtGPIO(args.device)

    if args.action == 'boot':
        device.enterBootMode()

    if args.action == 'en':
        device.reset()
