import sys,socket,logging,os
import argparse,threading
import datetime,asyncio
from _thread import *
#####################################################
parser = argparse.ArgumentParser(description='Run a HoneyPort server')
parser.add_argument("--port", "-p", help="The port to bind the server to (default 22)", default=22, type=int, action="store")
parser.add_argument("--bind", "-b", help="The address to bind the ssh server to", default="", type=str, action="store")
args = parser.parse_args()
#####################################################
port=args.port
bind=args.bind
#####################################################
banner=None
prompt=None
welcome=None
#####################################################
UP_KEY = '\x1b[A'.encode() ; DOWN_KEY = '\x1b[B'.encode()
RIGHT_KEY = '\x1b[C'.encode() ; LEFT_KEY = '\x1b[D'.encode()
BACK_KEY = '\x7f'.encode()
#####################################################
if port==22:
	banner="SSH-2.0-OpenSSH_8.4p1 Debian-5+deb11u1"
	welcome="\r\nWelcome to Ubuntu 18.04.4 LTS (GNU/Linux 4.15.0-128-generic x86_64)\r\n\r\n"
	prompt="pi@raspberry:~ $"
#####################################################
logging.basicConfig(
    format='> **%(levelname)s** - %(message)s```',
    level=logging.INFO,
    filename="./logs/HoneyPort.log")
#####################################################
class MyPot:
	def __init__(self):
		self.HOST = bind
		self.PORT = port
		self.client_ips={}
		self.mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#####################################################
	async def start_pot(self):
		await self.open_socket()
		await self.listen()
#####################################################
	def get_datetime(self):
		dt=datetime.datetime.utcnow()+datetime.timedelta(hours=-8)
		dt=dt.strftime("`%m/%d/%Y %I:%M:%S %p):` ```") ; return dt
#####################################################
	def add_ip(self,ip):
		dt=self.get_datetime()
		tries=5
		if ip not in self.client_ips:
			self.client_ips[ip]={}  ; self.client_ips[ip]["amount"]=1
		elif ip in self.client_ips:
			self.client_ips[ip]["amount"]+=1
			if self.client_ips[ip]["amount"] ==tries:
				logging.warning("%s Blocked ip: (%s) on port (%s)",dt,ip,self.PORT); return False 
			elif self.client_ips[ip]["amount"] > tries:
				logging.info("%s Attempt (%s) from blocked ip: (%s) to port (%s)",
				dt,self.client_ips[ip]["amount"]-tries,ip,self.PORT); return False
		return True
#####################################################
	async def open_socket(self):
		try:
			dt=self.get_datetime()
			self.mysocket.bind((self.HOST, self.PORT))
			self.mysocket.listen(10)
			logging.info("%s Listening for connection on port %s",dt,self.PORT)
			print(f"{dt} Running on port {self.PORT}")
		except socket.error as msg:
			logging.info('%s Bind to port (%s) failed. Error Code: Message: -%s',dt,self.PORT,msg)
			sys.exit()
#####################################################
	async def listen(self):
		threads=[]
		try:
			listen=True
			while listen==True:
				conn, addr = self.mysocket.accept()
				conn.settimeout(10)
				added=self.add_ip(addr[0])
				if added==False: 
					try: conn.sendall(b"Connection refused")
					finally: conn.close()
				else:
					ip=addr[0]+':'+str(addr[1])
					dt=self.get_datetime()
					logging.critical(
					"%s Connected to %s on port %s",dt,ip,self.PORT)
					new_thread = threading.Thread(
						target=self.threaded_client, args=(conn, ip))
					new_thread.start() ; threads.append(new_thread)
					for thread in threads: thread.join()
		except error as err:
			logging.error("%s",err)
			print(err) ; self.mysocket.close()
#####################################################
	def threaded_client(self,conn,conn_ip):
		dt=self.get_datetime()
		send_banner=banner ; send_welcome=welcome
		run = True
		try:
			while run:
				if send_banner !=None: conn.sendall(send_banner.encode()) ; send_banner=None
				run,send_welcome=self.emulate_terminal(conn,conn_ip,send_welcome)
			dt=self.get_datetime()
			logging.critical("%s Closing connection with %s on port %s",dt,conn_ip,self.PORT)
			conn.close()
		except BrokenPipeError: 
			dt=self.get_datetime()
			logging.warning("%s (%s) Broken pipe - possible port (%s) scan",dt,conn_ip,self.PORT); conn.close(); logging.critical("%s Connection closed with %s port %s",dt, conn_ip,self.PORT)
		except error as err:
			logging.error(err)
			print(err); conn.close()
#####################################################
	def emulate_terminal(self,conn,conn_ip,send_welcome):
		run=True
		dt=self.get_datetime()
		command = ""
		while not command.endswith("\r"):
			run,command=self.get_input(conn,conn_ip,command)
			if run==False: break
		conn.send(b"\r\n")
		if send_welcome !=None: conn.send(send_welcome.encode()) ; send_welcome=None
		if command!= "": command = command.rstrip().lstrip()
		if len(command)!=0: logging.warning("%s (%s port %s) Command: %s",dt,conn_ip,self.PORT,command)
		if command.lower()  in ["exit","logout"]:
			logging.info("%s (%s port %s) Exited",dt,conn_ip,self.PORT) ; run=False ; return run,send_welcome
		else: self.handle_command(conn,conn_ip,command)
		if prompt is not None: conn.send(prompt.encode())
		return run,send_welcome
#####################################################
	def get_input(self,conn,conn_ip,command):
		dt=self.get_datetime()
		try: transport = conn.recv(16)
		except socket.timeout:
			logging.info("%s (%s) socket timeout on port %s",dt,conn_ip,self.PORT); return False,command
		except ConnectionResetError:
			logging.warning("%s (%s) connection reset error - possible port (%s) scan",dt,conn_ip,self.PORT)
			return False,command
		if not transport: 
			logging.warning("%s (%s) nothing sent - possible port (%s) scan",dt,conn_ip,self.PORT)
			return False,command
		elif "SSH" in transport.decode():
			conn.send(banner.encode())
			logging.warning("%s (%s) ssh attempt on port %s (%s)",dt,conn_ip,self.PORT,transport.decode()) ; self.add_ip(conn_ip)
			asyncio.run(asyncio.sleep(10))
			return False ,command
		if transport.decode() not in [ "\r","",""]:
			logging.debug("%s (%s) Sent: %s to port %s",dt,conn_ip,transport,self.PORT)
		if transport not in [
		UP_KEY, DOWN_KEY, LEFT_KEY, RIGHT_KEY ,BACK_KEY]:
			conn.send(transport)
			command += transport.decode()
		if len(command)>=24: return False,command
		if transport.decode() == "\r": return True,command
		return True,command
#####################################################
	def handle_command(self,conn,conn_ip,command):
		dt=datetime.datetime.utcnow()
		dt=dt.strftime("%Y-%m-%d %H:%M")
		if " " in command: command=command.split(" ")[0]
		if command=="": return
		elif command.lower()== "who": 
			conn.send(f"\rpi    pts/0        {dt} ({conn_ip.split(':')[0]}) \r\n".encode())
		else: 
			conn.send(f"\r\n-bash: {command}: command not found\r\n".encode())
#####################################################
mypot=MyPot()
asyncio.run(mypot.start_pot())
#####################################################
