_C='rw error %s'
_B=False
_A=True
from microbit import *
import music,gc,os
gc.collect()
PN='micro:bit v2'
DBG=_B
ST=_B
CR='\r\n'
TFN='tps.bin'
E2E=1024
p=bytearray(E2E)
stack=bytearray(16)
stackp=0
music_note=['c','c#','d','d#','e','f','f#','g','g#','a','a#','b']
subs=[0,0,0,0,0,0]
wait=[1,2,5]
Din=[pin13,pin14,pin15,pin16]
Dout=[pin0,pin1,pin2,pin12]
Aout=[pin8,pin9]
Ain=[pin3,pin4]
button=[button_a,button_b]
images={1:Image.HEART,2:Image.HAPPY,3:Image.SMILE,4:Image.SAD,5:Image.CONFUSED,6:Image.ANGRY,7:Image.ASLEEP,8:Image.SURPRISED,9:Image.SILLY,10:Image.FABULOUS,11:Image.MEH,12:Image.YES,13:Image.NO,14:Image.CLOCK1,15:Image.CLOCK2,16:Image.CLOCK3,17:Image.CLOCK4,18:Image.CLOCK5,19:Image.CLOCK6,20:Image.CLOCK7,21:Image.CLOCK8,22:Image.CLOCK9,23:Image.CLOCK10,24:Image.CLOCK11,25:Image.CLOCK12,26:Image.ARROW_N,27:Image.ARROW_NE,28:Image.ARROW_E,29:Image.ARROW_SE,30:Image.ARROW_S,31:Image.ARROW_SW,32:Image.ARROW_W,33:Image.ARROW_NW,34:Image.TRIANGLE,35:Image.TRIANGLE_LEFT,36:Image.CHESSBOARD,37:Image.DIAMOND,38:Image.DIAMOND_SMALL,39:Image.SQUARE,40:Image.SQUARE_SMALL,41:Image.RABBIT,42:Image.COW,43:Image.MUSIC_CROTCHET,44:Image.MUSIC_QUAVER,45:Image.MUSIC_QUAVERS,46:Image.PITCHFORK,47:Image.XMAS,48:Image.PACMAN,49:Image.TARGET,50:Image.TSHIRT,51:Image.ROLLERSKATE,52:Image.DUCK,53:Image.HOUSE,54:Image.TORTOISE,55:Image.BUTTERFLY,56:Image.STICKFIGURE,57:Image.GHOST,58:Image.SWORD,59:Image.GIRAFFE,60:Image.SKULL,61:Image.UMBRELLA,62:Image.SNAKE,63:Image.HEART_SMALL}
def map(a,x1,y1,x2,y2):return int((a-x1)*(y2-x2)/(y1-x1)+x2)
def writeln(msg):uart.write(msg);uart.write(CR)
def save(fn):
	try:os.remove(fn)
	except OSError:writeln(_C%fn)
	with open(fn,'wb')as mb:mb.write(p)
def load(fn):
	try:
		with open(fn,'rb')as mb:mb.readinto(p)
	except OSError:writeln(_C%fn)
def hi_nib(pb):return p[pb]>>4&15
def lo_nib(pb):return p[pb]&15
def get_nib(pb,nib):
	if nib:return p[pb]&15
	else:return p[pb]>>4&15
def set_nib(pb,nib,v):
	if nib:p[pb]=p[pb]&240|v
	else:p[pb]=v<<4|p[pb]&15
def hexToByte(c):
	if c>='0'and c<='9':return ord(c)-ord('0')
	if c>='A'and c<='F':return ord(c)-ord('A')+10
def nibbleToHex(value):
	c=value&15
	if c>=0 and c<=9:return c+ord('0')
	if c>=10 and c<=15:return c+ord('A')-10
def printCheckSum(value):checksum=value&255;checksum=(checksum^255)+1;printHex8(checksum);uart.write(CR)
def printHex8(num):tmp=bytearray(2);tmp[0]=nibbleToHex(num>>4);tmp[1]=nibbleToHex(num);uart.write(tmp)
def printHex16(num):printHex8(num>>8);printHex8(num)
def getNextChar():
	while not uart.any():sleep(10)
	c=uart.read(1);return chr(c[0])
def getMidiNote(note):
	if note>=32 and note<=108:tune=music_note[note%12]+chr(ord('2')+int(note/12))+':4';return tune
	return'C0:1'
def tansAcc(value):return map(value,-2000,2000,0,256)
def writeProgramSerial():
	display.show(Image.ARROW_N);writeln('program data:');checksum=0
	for addr in range(E2E):
		value=p[addr]
		if addr%8==0:
			if addr>0:printCheckSum(checksum)
			checksum=0;uart.write(':08');checksum+=8;printHex16(addr);checksum+=addr>>8;checksum+=addr&255;uart.write('00')
		printHex8(value);checksum+=value
	printCheckSum(checksum);writeln(':00000001FF')
def serialprg():
	display.show(Image.DIAMOND);eOfp=_B;uart.init(baudrate=9600);uart.write(CR);writeln(PN);writeln('waiting for command:');writeln('w: write HEX file, r: read file, e: end')
	while not eOfp:
		while uart.any():
			c=uart.read(1);ch=chr(c[0])
			if ch=='w':
				display.show(Image.ARROW_S);writeln('ready');eOfF=_B;data=bytearray(32)
				while _A:
					for i in range(8):data[i]=255
					while _A:
						c=getNextChar()
						if c==':':break
					c=getNextChar();count=hexToByte(c)<<4;c=getNextChar();count+=hexToByte(c);crc=count;c=getNextChar();readAddress=hexToByte(c)<<12;c=getNextChar();readAddress+=hexToByte(c)<<8;c=getNextChar();readAddress+=hexToByte(c)<<4;c=getNextChar();readAddress+=hexToByte(c);crc+=readAddress>>8;crc+=readAddress&255;c=getNextChar();type=hexToByte(c)<<4;c=getNextChar();type+=hexToByte(c);crc+=type
					if type==1:eOfF=_A
					for x in range(count):c=getNextChar();value=hexToByte(c)<<4;c=getNextChar();value+=hexToByte(c);data[x]=value;crc+=value
					c=getNextChar();readcrc=hexToByte(c)<<4;c=getNextChar();readcrc+=hexToByte(c);crc+=readcrc;value=crc&255
					if value==0:
						uart.write('ok')
						for x in range(count):p[readAddress+x]=data[x]
					else:writeln(', CRC Error');eOfF=_A
					writeln('')
					if eOfF:break
				writeln('endOfFile');save(TFN)
			if ch=='r':load(TFN);writeProgramSerial()
			if ch=='e':writeln('end');eOfp=_A
	display.clear()
def prg():
	PC=0;nib=0;moved=1;load(TFN)
	for i in range(2):
		for j in range(2):
			for k in range(4):
				if get_nib(i,j)&1<<k:display.set_pixel(4-k,i*2+j,7*bool(get_nib(i,j)&1<<k))
	for i in range(4):display.set_pixel(4-i,nib%4,9)
	while button_b.is_pressed():0
	while _A:
		if button_a.is_pressed()and button_b.is_pressed():
			save();display.clear()
			while button_a.is_pressed()and button_b.is_pressed():0
			break
		if button_a.is_pressed():
			if moved:moved=0;set_nib(PC,nib%2,15)
			set_nib(PC,nib%2,(get_nib(PC,nib%2)+1)%16);sleep(100)
		if button_b.is_pressed():
			moved=1;nib=(nib+1)%E2E;PC=nib>>1
			if nib%4==0:
				for i in range(2):
					for j in range(2):
						for k in range(4):display.set_pixel(4-k,i*2+j,7*bool(get_nib(PC+i,j)&1<<k))
			for i in range(4):display.set_pixel(0,i,5*bool(PC&1<<i))
			for i in range(4,8):display.set_pixel(4-(i-4),4,5*bool(PC&1<<i))
			for i in range(4):display.set_pixel(4-i,nib%4,9)
			sleep(100)
		for i in range(4):display.set_pixel(4-i,nib%4,7*bool(get_nib(PC,nib%2)&1<<i))
		sleep(100)
def init():
	for i in range(E2E):p[i]=255
	for i in range(4):Din[i].set_pull(Din[i].PULL_UP)
	for i in range(6):subs[i]=0
def run():
	uart.init(baudrate=115200);uart.write(CR);writeln(PN+' running microbit TPS');A=0;B=0;C=0;D=0;E=0;F=0;PC=0;PAGE=0;RET=0;SKIP=0;INST=0;DATA=0;stackp=0;dbgtmp=bytearray(1);load(TFN);display.clear()
	for i in range(E2E):
		INST=hi_nib(i)
		if INST==14:
			DATA=lo_nib(i)
			if DATA>=8 and DATA<=13:subs[DATA-8]=i
	while _A:
		INST=hi_nib(PC);DATA=lo_nib(PC)
		if DBG:
			writeln('-');uart.write('PC: ');printHex16(PC);writeln('');uart.write('INST: ');dbgtmp[0]=nibbleToHex(INST);uart.write(dbgtmp);uart.write(', DATA: ');dbgtmp[0]=nibbleToHex(DATA);uart.write(dbgtmp);writeln('');writeln('Register:');uart.write('A: ');printHex8(A);uart.write(', B: ');printHex8(B);uart.write(', C: ');printHex8(C);writeln('');uart.write('D: ');printHex8(D);uart.write(', E: ');printHex8(E);uart.write(', F: ');printHex8(F);writeln('');uart.write('Page: ');printHex8(PAGE);uart.write(', Ret: ');printHex16(RET);writeln('')
			if ST:
				line=''
				while not line:line=uart.readline()
		if INST==0:
			if DATA==1:display.set_pixel(A,B,9)
			elif DATA==2:display.set_pixel(A,B,0)
			elif DATA==3:
				if A==0:display.clear()
				else:image=images.get(A,Image.SAD);display.show(image)
		elif INST==1:
			for i in range(4):display.set_pixel(4-i,0,9*bool(DATA&1<<i));Dout[i].write_digital(bool(DATA&1<<i))
		elif INST==2:
			if DATA==14:slp=30000
			elif DATA==15:slp=60000
			else:slp=10**(DATA//3)*wait[DATA%3]
			sleep(slp)
		elif INST==3:PC=PC-DATA;continue
		elif INST==4:A=DATA
		elif INST==5:
			if DATA==0:tmp=A;A=B;B=tmp
			elif DATA==1:B=A
			elif DATA==2:C=A
			elif DATA==3:D=A
			elif DATA==4:
				for i in range(4):display.set_pixel(4-i,0,9*bool(A&1<<i));Dout[i].write_digital(bool(A&1<<i))
			elif DATA>=5 and DATA<=8:display.set_pixel(9-DATA,0,9*(A&1));Dout[DATA-5].write_digital(bool(A&1))
			elif DATA==9:Aout[0].set_analog_period(2);Aout[0].write_analog(A%16*68)
			elif DATA==10:Aout[1].set_analog_period(2);Aout[1].write_analog(A%16*68)
			elif DATA==11:Aout[0].set_analog_period(20);Aout[0].write_analog(A%16*6)
			elif DATA==12:Aout[1].set_analog_period(20);Aout[1].write_analog(A%16*6)
			elif DATA==13:E=A
			elif DATA==14:F=A
			elif DATA==15:
				stack[stackp]=A;stackp+=1
				if stackp>15:stackp=15
		elif INST==6:
			if DATA==1:A=B
			elif DATA==2:A=C
			elif DATA==3:A=D
			elif DATA==4:A=Din[0].read_digital()|Din[1].read_digital()<<1|Din[2].read_digital()<<2|Din[3].read_digital()<<3
			elif DATA>=5 and DATA<=8:A=Din[DATA-5].read_digital()
			elif DATA==9:display.off();A=int(Ain[0].read_analog()/64);display.on()
			elif DATA==10:display.off();A=int(Ain[1].read_analog()/64);display.on()
			elif DATA==14:A=E
			elif DATA==14:A=F
			elif DATA==15:
				stackp-=1
				if stackp<0:stackp=0
				A=stack[stackp]
		elif INST==7:
			if DATA==1:A=A+1
			elif DATA==2:A=A-1
			elif DATA==3:A=A+B
			elif DATA==4:A=A-B
			elif DATA==5:A=A*B
			elif DATA==6:
				if B:A=A//B
			elif DATA==7:A=A&B
			elif DATA==8:A=A|B
			elif DATA==9:A=A^B
			elif DATA==10:A=A^15
			elif DATA==11:A=A%B
			elif DATA==12:A=A+16*B
			elif DATA==13:A=B-A
			elif DATA==14:A=A>>1
			elif DATA==15:A=A<<1
		elif INST==8:PAGE=DATA*16
		elif INST==9:PC=PAGE+DATA;continue
		elif INST==10:
			if C>0:C=C-1;PC=PAGE+DATA;continue
		elif INST==11:
			if D>0:D=D-1;PC=PAGE+DATA;continue
		elif INST==12:
			if DATA==0:SKIP=A==0
			elif DATA==1:SKIP=A>B
			elif DATA==2:SKIP=A<B
			elif DATA==3:SKIP=A==B
			elif DATA>=4 and DATA<=7:SKIP=Din[DATA%4].read_digital()&1==1
			elif DATA>=8 and DATA<=11:SKIP=Din[DATA%4].read_digital()&1==0
			elif DATA>=12 and DATA<=13:SKIP=button[DATA-12].is_pressed()
			elif DATA>=14:SKIP=not button[DATA-14].is_pressed()
			if SKIP:PC=PC+1
		elif INST==13:RET=PC+1;PC=PAGE+DATA;continue
		elif INST==14:
			if DATA==0:PC=RET;continue
			elif DATA>=1 and DATA<=6:RET=PC;PC=subs[DATA-1];continue
			elif DATA==15:reset()
		elif INST==15:
			if DATA==0:display.off();A=int(Ain[0].read_analog()>>2);display.on()
			elif DATA==1:display.off();A=int(Ain[1].read_analog()>>2);display.on()
			elif DATA==4:Aout[0].set_analog_period(2);Aout[0].write_analog(A<<4)
			elif DATA==5:Aout[1].set_analog_period(2);Aout[1].write_analog(A<<4)
			elif DATA==6:Aout[0].set_analog_period(20);Aout[0].write_analog(int(A/2))
			elif DATA==7:Aout[1].set_analog_period(20);Aout[1].write_analog(int(A/2))
			elif DATA==8:music.play(getMidiNote(A))
			elif DATA==9:A=tansAcc(accelerometer.get_x());E=tansAcc(accelerometer.get_y());F=tansAcc(accelerometer.get_z())
			elif DATA==10:
				if not compass.is_calibrated:compass.calibrate()
				A=int(compass.heading()/5)
			elif DATA==11:mic_val=int(microphone.sound_level()/255*16);A=mic_val
			elif DATA==12:A=display.read_light_level()
			elif DATA==13:A=pin_logo.is_touched()
		A=A&255;B=B&255;C=C&255;D=D&255;E=E&255;F=F&255;PC=(PC+1)%E2E
init()
if button_b.is_pressed():prg()
if button_a.is_pressed():serialprg()
run()