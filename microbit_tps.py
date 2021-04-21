from microbit import *
import music
import gc
gc.collect()

CRLF='\r\n'
#default filename for tps file
TPS_FILENAME='microtps.bin'

#program memory
E2END=1024
p=bytearray(E2END)

# our sdtack for push and pull with the pointer
stack=bytearray(16)
stackp=0

#array of sub routines
subs=[0,0,0,0,0,0]

wait=[1,2,5]
Din=[pin13, pin14, pin15, pin16]
Dout=[pin0, pin1, pin2, pin12]
Aout=[pin8, pin9]
Ain=[pin3, pin4]
button=[button_a, button_b]
images={
    1: Image.HEART,
    2: Image.HAPPY,
    3: Image.SMILE,
    4: Image.SAD,
    5: Image.CONFUSED,
    6: Image.ANGRY,
    7: Image.ASLEEP,
    8: Image.SURPRISED,
    9: Image.SILLY,
    10: Image.FABULOUS,
    11: Image.MEH,
    12: Image.YES,
    13: Image.NO,
    14: Image.CLOCK1, 
    15: Image.CLOCK2, 
    16: Image.CLOCK3, 
    17: Image.CLOCK4, 
    18: Image.CLOCK5, 
    19: Image.CLOCK6, 
    20: Image.CLOCK7, 
    21: Image.CLOCK8, 
    22: Image.CLOCK9, 
    23: Image.CLOCK10, 
    24: Image.CLOCK11, 
    25: Image.CLOCK12,
    26: Image.ARROW_N, 
    27: Image.ARROW_NE, 
    28: Image.ARROW_E, 
    29: Image.ARROW_SE, 
    30: Image.ARROW_S, 
    31: Image.ARROW_SW, 
    32: Image.ARROW_W, 
    33: Image.ARROW_NW,
    34: Image.TRIANGLE,
    35: Image.TRIANGLE_LEFT,
    36: Image.CHESSBOARD,
    37: Image.DIAMOND,
    38: Image.DIAMOND_SMALL,
    39: Image.SQUARE,
    40: Image.SQUARE_SMALL,
    41: Image.RABBIT,
    42: Image.COW,
    43: Image.MUSIC_CROTCHET,
    44: Image.MUSIC_QUAVER,
    45: Image.MUSIC_QUAVERS,
    46: Image.PITCHFORK,
    47: Image.XMAS,
    48: Image.PACMAN,
    49: Image.TARGET,
    50: Image.TSHIRT,
    51: Image.ROLLERSKATE,
    52: Image.DUCK,
    53: Image.HOUSE,
    54: Image.TORTOISE,
    55: Image.BUTTERFLY,
    56: Image.STICKFIGURE,
    57: Image.GHOST,
    58: Image.SWORD,
    59: Image.GIRAFFE,
    60: Image.SKULL,
    61: Image.UMBRELLA,
    62: Image.SNAKE,
    63: Image.HEART_SMALL
}

# starting with the code
def map(a,x1,y1,x2,y2):
    return int((a - x1) * (y2 - x2) / (y1 - x1) + x2)
    
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
        return (p[pb]>>4)&0x0F

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


music_note = ['c','c#','d','d#','e','f','f#','g','g#','a','a#','b']
def getMidiNote(note):
    if note >=32 and note <= 108:
        tune = music_note[ note % 12] + chr(ord('2') + (int(note / 12))) + ":4"
        writeln("tune:" + tune)
        return tune
    return "C0:1"

def tansformAcc(value):
    return map(value, -2000, 2000, 0, 256)

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
            nib=(nib+1)%E2END
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

def init():
    for i in range(E2END):
        p[i] = 0xff
    
    for i in range(4):
        Din[i].set_pull(Din[i].PULL_UP)

    for i in range(6):
        subs[i]=0

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

# loading the actual program file
    load(TPS_FILENAME)
    # writeProgramSerial()
    display.clear()

# scanning thru the program to get the sub routines
    for i in range(E2END):
        INST=hi_nib(i)
        if INST== 0x0e:
            DATA=lo_nib(i)
            if DATA >=0x08 and DATA <= 0x0d:
              subs[DATA-0x08] = i
              
# main lood
    while True:
        # getting instruction and data
        INST=hi_nib(PC)
        DATA=lo_nib(PC)

        if INST==0x00:
            if DATA==0x01:
                display.set_pixel(A,B,9)                
            elif DATA==0x02:
                display.set_pixel(A,B,0)                
            elif DATA==0x03:
                if A==0:
                    display.clear()
                else:
                    image = images.get(A, Image.SAD)
                    display.show(image)

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
                AOut[0].set_analog_period(2)
                AOut[0].write_analog(A*68)
            elif DATA==0x0A:
                AOut[1].set_analog_period(2)
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
                PC=PC
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
                A=int(Ain[0].read_analog()/64)
            elif DATA==0x0A:
                A=int(Ain[1].read_analog()/64)
            elif DATA==0x0E:
                A=E
            elif DATA==0x0E:
                A=F
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
                A=A%B
            elif DATA==0x0C:
                A=A+16*B
            elif DATA==0x0D:
                A=B-A
            elif DATA==0x0E:
                A=A>>1
            elif DATA==0x0F:
                A=A<<1

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
            if DATA==0x00:
                SKIP=A==0
            elif DATA==0x01:
                SKIP=A>B
            elif DATA==0x02:
                SKIP=A<B
            elif DATA==0x03:
                SKIP=A==B
            elif DATA>=0x04 and DATA<=0x07:
                SKIP=(Din[DATA%4])&0x01==1
            elif DATA>=0x08 and DATA<=0x0B:
                SKIP=(Din[DATA%4])&0x01==0
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
            elif DATA>=0x01 and DATA <= 0x06:
                RET=PC
                PC=subs[DATA-0x01]
                continue
            elif DATA==0x0F:
                microbit.reset()
        elif INST==0x0F:
            if DATA==0x00:
                A=int(Ain[0].read_analog()>>2)
            elif DATA==0x01:
                A=int(Ain[1].read_analog()>>2)
            elif DATA==0x04:
                AOut[0].set_analog_period(2)
                AOut[0].write_analog(A<<4)
            elif DATA==0x05:
                AOut[1].set_analog_period(2)
                AOut[1].write_analog(A<<4)
            elif DATA==0x06:
                AOut[0].set_analog_period(20)
                AOut[0].write_analog(int(A/2))
            elif DATA==0x07:
                AOut[1].set_analog_period(20)
                AOut[1].write_analog(int(A/2))
            elif DATA==0x08:
                music.play(getMidiNote(A))
            elif DATA==0x09:
                #get accel
                A=transformAcc(accelerometer.get_x())
                E=transformAcc(accelerometer.get_y())
                F=transformAcc(accelerometer.get_z())
            elif DATA==0x0A:
                if compass.is_calibrated == False:
                    compass.calibrate()
                A = int(compass.heading() / 5)
            elif DATA==0x0B:
                mic_val = int((microphone.sound_level() / 255) * 16)
                A = mic_val
            elif DATA==0x0C:
                A = display.read_light_level()
            elif DATA==0x0D:
                A = pin_logo.is_touched() == True
           
                
        PC=(PC+1)%E2END

init()
if button_b.is_pressed():
    prg()
if button_a.is_pressed():
    serialprg()
run()