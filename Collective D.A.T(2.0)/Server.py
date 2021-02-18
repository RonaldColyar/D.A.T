import socket
import threading
import mysql.connector

'''database.cursor().execute("CREATE TABLE Usertest (username VARCHAR(255) , password VARCHAR(255))")'''
class server:

	def __init__(self):
		self.database = mysql.connector.connect(host = "" , user= "" , password = "", database = "")
		self.cursor=self.database.cursor()
		self.host = '127.0.0.1' #localhost
		self.port = 50222
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.user_names = []
		self.clients = []

	def update_all_clients(self,message):
		for client in self.clients:
			try:
				client.send(message.encode('ascii'))
			except:
				try:
					index = self.clients.index(client)
					username = self.user_names[index]
					self.clients.remove(client)
					self.user_names.remove(username)
					print(f"""client with username: {username} connection has been severed 
						since there was a issue brodcasting to the client....""")
				except:
					print("Error 2005")


	def create_user(self ,username_init,password,client,addr):
		self.cursor.execute("INSERT INTO Usertest (username , password) VALUES (%s,%s)" , (username_init , password,))
		self.database.commit()
		print('       ')
		print(f"user:({username_init}) created with password:({password}) by :({addr})")
		client.send('SUCESSFULL_USER_CREATION'.encode('ascii'))

	def delete_user(self,username,client,addr):
		self.cursor.execute("DELETE FROM Usertest WHERE username = %s", (username,))
		self.database.commit()
		print("       ")
		print(f"user:({username}) was deleted by :({addr})")
		client.send("REMOVED".encode('ascii'))

	def create_user_auth(self , client,addr):
		admin_password = client.recv(1000).decode('ascii') # block and wait on password for admin
		self.cursor.execute("SELECT password FROM Usertest WHERE username =%s" , ('admin',))
		if self.cursor.fetchone()[0] == admin_password:
			print(f'Auth Success by :{addr}')
			client.send("USER_CREATION_NAME".encode('ascii'))
			username_init = client.recv(1000).decode('ascii') #block and wait on username( for creation)
			password = client.recv(1000).decode('ascii') 	  #block and wait on password( for creation)
			print(username_init)
			print(password)
			self.create_user(username_init,password,client,addr)
		else:
			client.send("FAILED AUTH".encode('ascii'))

	def delete_user_auth(self, client,addr):
		password = client.recv(1000).decode('ascii')
		self.cursor.execute("SELECT password FROM Usertest WHERE username =%s" , ('admin',))

		if self.cursor.fetchone()[0] == password:
			print(f"Auth Success by :{addr}")
			client.send("USER_DELETION_NAME".encode('ascii'))
			username_for_deletion = client.recv(1000).decode('ascii')
			self.delete_user(username_for_deletion,client,addr)
		else:
			client.send("FAILED AUTH".encode('ascii'))

	def remove_connection_and_username(self,client,username):
		self.clients.remove(client)
		client.close()
		self.user_names.remove(username)
		self.update_all_clients(f"{username} has left the chat!!")
		self.update_all_clients(f"Remaining users in the chat:{str(self.user_names)}")

	def check_for_kick(self, client,message):
		try:
			if str(message).find('kick') == 6 :
				username_to_kick = message[11:]   # since 'admin:kick' is 10 indexs
				index = self.user_names.index(username_to_kick)
				self.user_names.remove(self.user_names[index])
				client_of_kicked = self.clients[index]
				client_of_kicked.send("**(kicked by admin)**".encode('ascii'))
				self.clients.remove(client_of_kicked)
				client_of_kicked.close()
				print(f"{username_to_kick} was kicked by admin!!")
		except:
			client.send("Issue kicking this user!!".encode('ascii'))

	def client_thread(self , client,username):
		thread_running = True
		while thread_running == True:
			message = client.recv(1000).decode('ascii')
			if username == 'admin':
				self.check_for_kick(client,message)
			if message == "DISCONNECT_":
				try:
					self.remove_connection_and_username(client,username)
				except:
					print(f"{client} tried to disconnect but was already kicked by admin!!")
				thread_running = False
			else:
				self.update_all_clients(message)

		print("ended thread")
	def login(self, username,client,addr ):
		print(f"Client Screen Name @ address:{addr} is {username}")
		client.send("AUTHED".encode('ascii'))
		client.send(str(self.user_names).encode('ascii'))
		self.update_all_clients(f"{username} has joined the chat!!")
		self.start_client_thread(username,client)

	def start_client_thread(self,username,client):
		self.clients.append(client)
		self.user_names.append(username)
		thread = threading.Thread(target =self.client_thread, args = (client,username,))
		thread.start()

	def login_auth (self,client,addr):
		username = client.recv(1000).decode('ascii')
		password = client.recv(1000).decode('ascii')
		self.cursor.execute("SELECT password FROM Usertest WHERE username=%s" , (username,))
		accountpassword = self.cursor.fetchall()	

		if len(accountpassword) == 0: 
			client.send("DISCONNECT".encode('ascii'))
		elif accountpassword[0][0] == password:
			self.login(username,client,addr)

		else:   #wrong password or other error
			client.send("DISCONNECT".encode('ascii'))
			client.close()
			print(f"Error with client at :{addr} trying to connect with user: ({username}) and password :({password})")

	def start(self):
		while True :
			client , addr = self.server.accept() #block and wait for a connection
			print(client)
			print(f"client connected!! : @ {addr}")
			action = client.recv(1000).decode('ascii')
			if action == "login":
				print("          ")
				print(f"client at : {addr} is trying to login to a user")
				print("          ")
				self.login_auth(client,addr)
				
			elif action == 'create user':
				print("          ")
				print(f"Client at :{addr} is attempting to create a user. ")
				print('waiting on Auth password')
				self.create_user_auth(client,addr)
			elif action == 'delete user':
				self.delete_user_auth(client,addr)
			else:
				client.send("UNKNOWN_ACTION".encode('ascii'))

	def init_server(self):
		self.server.bind((self.host,self.port))
		self.server.listen()
		self.start()

if __name__ == '__main__':
	server().init_server()
