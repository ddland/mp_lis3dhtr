import machine
from lis3dhtr import LIS3DHTR
import time

if __name__ == "__main__":
    i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1))
    LIS = LIS3DHTR(i2c, FS=2)
    N = 50 # 50 measurements
    dt = 0.01 # delay between samples
    base_fh = 'fs_'

    for ii in [2,4,8,16]:
        fn = base_fh + '%dG.csv' %(ii)
        print('working on: ', fn)
        LIS.setFS(ii) # set gain
        time.sleep(1)
        fh = open(fn, 'a')
        for ii in range(N):
            fh.write("%4.4f,%4.4f,%4.4f\n" %tuple(LIS.read_all_acc()))
            time.sleep(dt)
        fh.close()
    print('done')
