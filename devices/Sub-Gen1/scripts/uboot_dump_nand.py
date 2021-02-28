#dump nand with md command from uboot

import os
import serial 
import time

START = 0x00
END = 0x4000000

PER_DUMP_SIZE = 1024 * 2048
FILE_PATH = "nand.bin"

f = open(FILE_PATH, 'ab')

dumped = os.fstat(f.fileno()).st_size
if dumped > 0:
    print(f"found {dumped} bytes dumped, continuing")


ser = serial.Serial(
    port='/dev/cu.usbserial-AB0KG6J0',
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)
print(f"serial port good? {ser.isOpen()}") 
ptr = dumped

def hexstring2bin(hs):
    # print("".join([chr(c) for c in hs]))
    if len(hs) % 2 != 0: hs = hs[:-1]
    raw = [int(hs[i*2] + hs[i*2+1], 16) for i in range(len(hs) // 2)]
    return bytes(raw)

def skip2prompt(ser):
    ss = ''
    while(True):
        s = ser.readline().decode('ascii')
        ss += s
        if '=>' in s: return ss

f.close()

while ptr < END:
    chunk = PER_DUMP_SIZE
    print(f"Reading 0x{ptr:x} into mem...")
    time.sleep(0.01)
    ser.write(f"nand read 0x200000 0x{ptr:x} 0x{chunk:x}\n".encode('ascii'))
    ser.flush()

    ser.readline().decode('ascii')
    ser.readline().decode('ascii')
    ser.readline().decode('ascii')
    ser.readline().decode('ascii')



    ser.write(f"md 0x200000 0x{chunk:x}\n".encode('ascii'))
    ser.flush()
    ser.readline().decode('ascii')
    data_chunk = bytes(0)
    cnt = 0
    while chunk > 0:
        o = ser.readline().decode('ascii')
        raw = hexstring2bin(''.join(o.strip().split(' ')[1:5]))
        data_chunk += raw
        chunk -= len(raw)

        cnt += len(raw)
        print(f"got {cnt / 1024 : .2f}KB, actual size {cnt / 1024 / 2 : .2f}KB", end="\r") 

    assert(len(data_chunk) == PER_DUMP_SIZE)
    ptr += len(data_chunk)
    f = open(FILE_PATH, 'ab')
    f.write(data_chunk)
    f.flush()
    f.close()
    print("chunk saved to dump file")


