import machine
import time

# LIS3DHTR
# work in progress
class LIS3DHTR:
    address = 0x19
    accRange = {2:16000, 4:7282, 8:3968, 16:1280}
    
    def __init__(self, i2c, FS=2):
        ''' Read LIS3DHTR sensor with configurable Full Scale setting.

        Give the full scale (2,4,8,16g) option either at initialisation or
        change it during measurements.
        '''
        self.i2c = i2c
        i2cbus = self.i2c.scan()
        if not ((self.address in i2cbus) and len(i2cbus) < 5):
            msg = "Device 0x%02x not in i2cbus: [" %(self.address) \
                  + ' '.join(str(x) for x in i2cbus) + "]" 
            raise OSError(msg)
        if FS in [2,4,8,16]:
            self.FS = FS
        else:
            self.FS = 2
        self.setup()
        
    def setup(self):
        self.write(0x20, int('01110111',2)) # 400 Hz, high resolution, x,yz enabled
        self.setFS()
        
    def setFS(self, FS=None):
        if (not FS) and (FS in [2,4,8,16]):
            self.FS=FS
        if self.FS == 2:
            self.write(0x23, int('10001000',2)) # BDU=1, LSB@lower, FS=2g, HR=1
        elif self.FS == 4:
            self.write(0x23, int('10011000',2))
        elif self.FS == 8:
            self.write(0x23, int('10101000',2))
        elif self.FS == 16:
            self.write(0x23, int('10111000',2))
            
    def enable_temp(self):
        print("Temperature not working. No reasanable output expected")
        self.write(0x1F, 0x80 | 0x40) # enable ADC & temperature
        
    def read_temp(self):
        val = self.i2c.readfrom_mem(self.address, 0x0c, 2)
        val = int.from_bytes(val, "big") / 256
        return val + 25
    
    def write(self, reg, msg):
        if not isinstance(msg, bytes):
            if not isinstance(msg, list):
                msg = [msg]
            msg = bytes(msg)
        self.i2c.writeto_mem(self.address, reg, msg)
        
    def read_acc_raw(self, reg):
        lo = self.i2c.readfrom_mem(self.address, reg, 1)[0]
        hi = self.i2c.readfrom_mem(self.address, reg+1, 1)[0]
        val = hi << 8 | lo # 256 * hi + lo
        if val > (2**15-1):
            val -= 2**16
        return val 
        
    def read_acc(self, reg):
        return self.read_acc_raw(reg) / self.accRange[self.FS]

    def read_all_acc(self, raw=False):
        func = self.read_acc
        if raw:
            func = self.read_acc_raw
        acc = [0,0,0]
        base = 0x28
        for ii in range(3):
            acc[ii] = func(base + 2*ii)
        return acc
       
        
