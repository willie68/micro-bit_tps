# Button A is PRG or S1 (p5)
# Button B is SEL or S2 (p11)
# output pins 
#   0 pin12
#   1 pin8
#   2 pin2
#   3 pin1
# input pins
#   0 pin16
#   1 pin15
#   2 pin14
#   3 pin13
#  a/d pins
#  d/a pins
#  servo pins
#  ppm in pins
#
# p0  a/d           DOut 0
# p1  a/d           DOut 1
# p2  a/d           DOut 2
# p3  LED Col 3 a/d A/D 0
# p4  LED Col 1 a/d A/D 1
# p5  Button A      PRG/S1
# p6  LED Col 4 
# p7  LED Col 2 
# p8                D/A 0
# p9                D/A 1
# p10 LED Col 5 a/d
# p11 Button B      SEL/S2
# p12 reserved      DOut 3
# p13               DIn 0
# p14               DIn 1
# p15               DIn 2
# p16               DIn 3
# p19 I2C           
# p20 I2C           

from microbit import *
import gc
gc.collect()

CRLF='\r\n'
TPS_FILENAME='microtps.bin'
min_acc = -1024
max_acc = 1024
range_acc = max_acc - min_acc
E2END=1024

p=bytearray(E2END)

stack=bytearray(16)
stackp=0

def writeln(msg):
    uart.write(msg)
    uart.write(CRLF)

def save(fn):
    with open(fn, 'wb') as mb:
        mb.write(p)

def load(fn):
    try:
        with open(fn, 'rb') as mb:
            mb.readinto(p)
        writeln("reading ok")
    except OSError:
        writeln("Can't read file %s" % fn)

def hi_nib(pb):
    return (p[pb]>>4)&0x0F

def lo_nib(pb):
    return p[pb]&0x0F

def get_nib(pb,nib):
    if nib:
        return p[pb]&0x0F
    else:
        return 

def set_nib(pb,nib,v):
    if nib:
        p[pb]=(p[pb]&0xF0)|v
    else:
        p[pb]=(v<<4)|(p[pb]&0x0F)

def hexToByte (c):
    if ((c >= '0') and (c <= '9')): 
        return ord(c) - ord('0')
    if ((c >= 'A') and (c <= 'F')):
        return (ord(c) - ord('A')) + 10

def nibbleToHex(value):
    c = value & 0x0F
    if ((c >= 0) and (c <= 9)):
        return c + ord('0')
    if ((c >= 10) and (c <= 15)):
        return (c + ord('A')) - 10

def printCheckSum(value):
    checksum = value & 0xFF
    checksum = (checksum ^ 0xFF) + 1
    printHex8(checksum)
    uart.write(CRLF)

def printHex8(num):
    tmp=bytearray(2)
    tmp[0] = nibbleToHex(num >> 4)
    tmp[1] = nibbleToHex(num)
    uart.write(tmp)

def printHex16(num):
    tmp=bytearray(4)
    tmp[0] = nibbleToHex(num >> 12)
    tmp[1] = nibbleToHex(num >> 8)
    tmp[2] = nibbleToHex(num >> 4)
    tmp[3] = nibbleToHex(num)
    uart.write(tmp)

def getNextChar():
    while not uart.any():
        sleep(10)
    c=uart.read(1)
    return chr(c[0])

def writeProgramSerial():
    display.show(Image.ARROW_N)
    writeln('program data:')
    checksum = 0
    for addr in range(E2END):
        value = p[addr]
        if ((addr % 8) == 0):
            if addr > 0:
                printCheckSum(checksum)
            checksum = 0
            uart.write(":08")
            checksum += 0x08
            printHex16(addr)
            checksum += (addr >> 8)
            checksum += (addr & 0x00FF)
            uart.write("00")
                    
        printHex8(value)
        checksum += value
                
    printCheckSum(checksum)
    # ending
    writeln(":00000001FF")


def serialprg():
    display.show(Image.DIAMOND)
    eOfp=False
    uart.init(baudrate=9600)
    uart.write(CRLF)
    writeln('micro_bit_v2')
    writeln('waiting for command:')
    writeln('w: write HEX file, r: read file, e: end')
    while not eOfp:
        while uart.any():
            c=uart.read(1)
            ch = chr(c[0])
            if ch == 'w':
                display.show(Image.ARROW_S)
                #hexfile is comming to programm
                writeln('ready')
                eOfF=False
                addr = 0
                data=bytearray(32)
                while True:
                    for i in range(8):
                        data[i] = 0xFF
    
                    while True:
                        c = getNextChar()
                        if c == ':':
                            break
    
                    #read counter
                    c = getNextChar()
                    count = hexToByte(c) << 4
                    c = getNextChar()
                    count += hexToByte(c)
    
                    crc = count

                    #address
                    c = getNextChar()
                    readAddress = hexToByte(c) << 12
                    c = getNextChar()
                    readAddress += hexToByte(c) << 8
                    c = getNextChar()
                    readAddress += hexToByte(c) << 4
                    c = getNextChar()
                    readAddress += hexToByte(c)
    
                    crc += readAddress >> 8
                    crc += readAddress & 0x00FF
    
                    #reading data type
                    c = getNextChar()
                    type = hexToByte(c) << 4
                    c = getNextChar()
                    type += hexToByte(c)
            
                    crc += type

                    if (type == 0x01):
                        eOfF = True

                    #read data bytes
                    for x in range(count):
                        c = getNextChar()
                        value = hexToByte(c) << 4
                        c = getNextChar()
                        value += hexToByte(c)

                        data[x] = value
                        crc += value

                    #read CRC
                    c = getNextChar()
                    readcrc = hexToByte(c) << 4
                    c = getNextChar()
                    readcrc += hexToByte(c)
    
                    crc += readcrc
                    #check CRC
                    value = crc & 0x00FF
    
                    if value == 0:
                        uart.write("ok")
                        for x in range(count):
                            p[readAddress + x] = data[x]
                    else:
                        writeln(', CRC Error')
                        eOfF=True

                    writeln("")
                    if eOfF: 
                        break
                    
                writeln('endOfFile')
                save(TPS_FILENAME)
            if ch == 'r':
                load(TPS_FILENAME)
                writeProgramSerial
            if ch == 'e':
                writeln('end')
                eOfp = True
    display.clear()

def prg():
    PC=0
    nib=0
    moved=1
    load(TPS_FILENAME)
    for i in range(2):
        for j in range(2):
            for k in range(4):
                if get_nib(i,j)&(1<<k):
                    display.set_pixel(4-k,i*2+j,7*bool(get_nib(i,j)&(1<<k)))

    for i in range(4):
        display.set_pixel(4-i,nib%4,9)

    while button_b.is_pressed():
        pass

    while True:
        if button_a.is_pressed() and button_b.is_pressed():
            save()
            display.clear()
            while button_a.is_pressed() and button_b.is_pressed():
                pass
            break

        if button_a.is_pressed():
            if moved:
                moved=0
                set_nib(PC,nib%2,0x0F)
            set_nib(PC,nib%2,(get_nib(PC,nib%2)+1)%16)
            sleep(100)

        if button_b.is_pressed():
            moved=1
            nib=(nib+1)%512
            PC=nib>>1
            if nib%4==0:
                for i in range(2):
                    for j in range(2):
                        for k in range(4):
                            display.set_pixel(4-k,i*2+j,7*bool(get_nib(PC+i,j)&(1<<k)))

            for i in range(4):
                display.set_pixel(0,i,5*bool(PC&(1<<i)))
            for i in range(4,8):
                display.set_pixel(4-(i-4),4,5*bool(PC&(1<<i)))

            for i in range(4):
                display.set_pixel(4-i,nib%4,9)
            sleep(100)

        for i in range(4):
            display.set_pixel(4-i,nib%4,7*bool(get_nib(PC,nib%2)&(1<<i)))
        sleep(100)

def run():
    uart.init(baudrate=115200)
    uart.write(CRLF)
    writeln('micro:bit v2 running micro TPS')

    A=0
    B=0
    C=0
    D=0
    E=0
    F=0
    PC=0
    PAGE=0
    RET=0
    SKIP=0
    INST=0
    DATA=0
    Row=0

# initialise the interpreter
    wait=[1,2,5]
    Din=[pin13, pin14, pin15, pin16]
    Dout=[pin0, pin1, pin2, pin12]
    Aout=[pin8, pin9]
    Ain=[pin3, pin4]
    button=[button_a, button_b]
    for i in range(E2END):
        p[i] = 0xff
    
    for i in range(4):
        Din[i].set_pull(Din[i].PULL_UP)

# loading the actual program file
    load(TPS_FILENAME)
    writeProgramSerial()
    display.clear()

# main lood
    while True:
        # getting instruction and data
        INST=hi_nib(PC)
        DATA=lo_nib(PC)

        if INST==0x00:
            PC=PC

        elif INST==0x01:
            for i in range(4):
                display.set_pixel(4-i,Row,9*bool(DATA&(1<<i)))
                Dout[i].write_digital(bool(DATA&(1<<i)))

        elif INST==0x02:
            if DATA==0x0E:
                slp=30000
            elif DATA==0x0F:
                slp=60000
            else:
                slp=(10**(DATA//3))*wait[DATA%3]
            sleep(slp)

        elif INST==0x03:
            PC=PC-DATA
            continue

        elif INST==0x04:
            A=DATA

        elif INST==0x05:
            if DATA==0x00:
                tmp = A
                A=B
                B=tmp
            elif DATA==0x01:
                B=A
            elif DATA==0x02:
                C=A
            elif DATA==0x03:
                D=A
            elif DATA==0x04:
                for i in range(4):
                    display.set_pixel(4-i,Row,9*bool(A&(1<<i)))
                    Dout[i].write_digital(bool(A&(1<<i)))

            elif DATA>=0x05 and DATA<=0x08:
                display.set_pixel(9-DATA,Row,9*(A&0x01))
                Dout[DATA-5].write_digital(bool(A&0x01))
            elif DATA==0x09:
                AOut[0].write_analog(A*68)
            elif DATA==0x0A:
                AOut[1].write_analog(A*68)
            elif DATA==0x0B:
                AOut[0].set_analog_period(20)
                AOut[0].write_analog(A*6)
            elif DATA==0x0C:
                AOut[1].set_analog_period(20)
                AOut[1].write_analog(A*6)
            elif DATA==0x0D:
                E=A
            elif DATA==0x0E:
                F=A
            elif DATA==0x0F:
                #Push to stack
                stack[stackp] = A
                stackp+=1
                if stackp > 15:
                    stackp=15

        elif INST==0x06:
            if DATA==0x00:
                A=Row
            elif DATA==0x01:
                A=B
            elif DATA==0x02:
                A=C
            elif DATA==0x03:
                A=D
            elif DATA==0x04:
                A=Din
            elif DATA>=0x05 and DATA<=0x08:
                A=(Din>>(DATA-5))&0x01
            elif DATA==0x09:
                A=int(pin1.read_analog()/64)
            elif DATA==0x0A:
                A=int(pin2.read_analog()/64)
            elif DATA==0x0E:
                save()
            elif DATA==0x0F:
                #Push to stack
                stackp-=1
                if stackp < 0:
                    stackp=0    
                A=stack[stackp]

        elif INST==0x07:
            if DATA==0x01:
                A=A+1
            elif DATA==0x02:
                A=A-1
            elif DATA==0x03:
                A=A+B
            elif DATA==0x04:
                A=A-B
            elif DATA==0x05:
                A=A*B
            elif DATA==0x06:
                if B:
                    A=A//B
            elif DATA==0x07:
                A=A&B
            elif DATA==0x08:
                A=A|B
            elif DATA==0x09:
                A=A^B
            elif DATA==0x0A:
                A=A^0x0F
            elif DATA==0x0B:
                A=A<<1
            elif DATA==0x0C:
                A=A>>1
            elif DATA==0x0D:
                A=(A<<1)|((A&0x08)>>3)
            elif DATA==0x0E:
                A=(A>>1)|((A&0x01)<<3)

        elif INST==0x08:
            PAGE=DATA*16

        elif INST==0x09:
            PC=PAGE+DATA
            continue

        elif INST==0x0A:
            if C>0:
                C=C-1
                PC=PAGE+DATA
                continue

        elif INST==0x0B:
           if D>0:
                D=D-1
                PC=PAGE+DATA
                continue

        elif INST==0x0C:
            SKIP=A==0
            if DATA==0x01:
                SKIP=A>B
            elif DATA==0x02:
                SKIP=A<B
            elif DATA==0x03:
                SKIP=A==B
            elif DATA>=0x04 and DATA<=0x0B:
                SKIP=(Din>>DATA%4)&0x01==1*(DATA<0x08)
            elif DATA>=0x0C and DATA<=0x0D:
                SKIP=button[DATA-0x0C].is_pressed()
            elif DATA>=0x0E:
                SKIP=not button[DATA-0x0E].is_pressed()
            if SKIP:
                PC=PC+1

        elif INST==0x0D:
            RET=PC+1
            PC=PAGE+DATA
            continue

        elif INST==0x0E:
            if DATA==0x00:
                PC=RET
                continue
            elif DATA>=0x01 and DATA<=0x03:
                if DATA==0x01:
                    acc_val = accelerometer.get_x()
                elif DATA==0x02:
                    acc_val = accelerometer.get_y()
                elif DATA==0x03:
                    acc_val = accelerometer.get_z()
                acc_val = min(max(min_acc, acc_val), max_acc)
                acc_val = ((acc_val - min_acc) / range_acc) * 16
                A = int(acc_val)
            elif DATA==0x04:
                if compass.is_calibrated == False:
                    compass.calibrate()
                A = int((compass.heading() / 360) * 16)
            elif DATA==0x05:
                mic_val = int((microphone.sound_level() / 255) * 16)
                A = mic_val
            elif DATA==0x06:
                A = int((display.read_light_level() / 255) * 16)
            elif DATA==0x07:
                music.play(music_note[A%len(music_note)])
            elif DATA==0x08:
                music.play(music_tune[A%len(music_tune)])
            elif DATA==0x09:
               audio.play(audio_sound[A%len(audio_sound)])
            elif DATA==0x0E:
                A = pin_logo.is_touched() == False
            elif DATA==0x0F:
                A = pin_logo.is_touched() == True
        elif INST==0x0F:
            PC = PC
            
        PC=(PC+1)%E2END

if button_b.is_pressed():
    prg()
if button_a.is_pressed():
    serialprg()
run()