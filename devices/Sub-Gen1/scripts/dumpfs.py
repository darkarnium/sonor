import serial 
import time
ser = serial.Serial(
    port='/dev/cu.usbserial-AB0KG6J0',
    baudrate=115200,
)

def hexstring2bin(hs):
    # print("".join([chr(c) for c in hs]))
    if len(hs) % 2 != 0: hs = hs[:-1]
    raw = [int(chr(hs[i*2]) + chr(hs[i*2+1]), 16) for i in range(len(hs) // 2)]
    return bytes(raw)
    

print(ser.isOpen())

#mkdir /tmp/rm; mount --bind / /tmp/rm
#mkdir /ramdisk/text; echo "hello" > /ramdisk/text/hello; echo "world" > /ramdisk/text/world

# ser.write("tar -c /ramdisk/tmp/rootmount 2>/dev/null | gzip -c\r\n".encode('ascii'))
# ser.write("tar -c /ramdisk/text 2>/dev/null | hexdump -ve '1/1 \"%.2x\"' \r\n".encode('ascii'))
# ser.write("tar -c /ramdisk/tmp/rm 2>/dev/null | gzip -c | hexdump -ve '1/1 \"%.2x\"' \r\n".encode('ascii'))
ser.write("cat /dev/mtdblock8 2>/dev/null | gzip -c | hexdump -ve '1/1 \"%.2x\"' \r\n".encode('ascii'))
# ser.write("ls\r\n".encode('ascii'))

# time.sleep(2)
data = bytes()
bytes_cnt = 0
last_rep = 0
cp_cnt = 1
last_cp = 0

while True: 
    if ser.read(1).decode('ascii') == '\n': break


while True:
    if ser.inWaiting() <= 0:
        empty_cnt = 200
        while empty_cnt > 0:
            time.sleep(0.05)
            if ser.inWaiting() > 0: break
            empty_cnt -= 1

        if empty_cnt <= 0: break

    chunk = ser.read(ser.inWaiting())
    data += chunk
    bytes_cnt += len(chunk)
    if bytes_cnt - last_rep > 1024: 
        print(f"got {bytes_cnt / 1024 : .2f}KB, actual size {bytes_cnt / 1024 / 2 : .2f}KB", end="\r")
        last_rep = bytes_cnt
        
    
    # if bytes_cnt - last_cp > 1024 * 1024:
    #     print("\ncheck point saved")
    #     f = open(f"cps/checkpoint{cp_cnt}.tar.gz",'wb')
    #     cp_cnt += 1
    #     f.write(hexstring2bin(data))
    #     f.flush()
    #     f.close()
    #     last_cp = bytes_cnt
    # print(d.__class__)
    # data.append()

while True:
    if chr(data[-1]) in ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']: break
    data = data[:-1]

open("raw.bin", 'wb').write(data)

open("mtdblocks/mtdblock8.gz", 'wb').write(hexstring2bin(data))
print()
print(len(data))