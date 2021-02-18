import socket
import threading
from termcolor import colored
from colorama import init
import atexit
init() #windows command line color support

print(colored("Welcome to the D.A.T Chat!! You are now blocking the server! Be courteous!", "green"))
action = input("what action would you like to execute?>")

class client_model:
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(('127.0.0.1',50222))
	not_kicked = True

	def gather_and_send_admin_password(self,message):
		self.client.send(message.encode('ascii'))
		password = input("What is the admin password?> ")
		self.client.send(str(password).encode('ascii'))

	def gather_and_send_new_user_credentials(self):
		username  = input("What is the new user's name?>")
		password = input("What is the new user's password?>")
		self.client.send(username.encode('ascii'))
		self.client.send(password.encode('ascii'))

	def gather_and_send_user_for_deletion(self):
		username = input("What is the username you would like to delete?")
		self.client.send(username.encode('ascii'))

	def user_creation(self):
			self.gather_and_send_admin_password("create user")
			auth_response = self.client.recv(1000).decode('ascii')
			if auth_response == "USER_CREATION_NAME":
				self.gather_and_send_new_user_credentials()
				server_resonse_to_credentials  =self.client.recv(1000).decode('ascii') 
				#update client
				if server_resonse_to_credentials == 'SUCESSFULL_USER_CREATION':
					print("user created sucessfully")
				else:
					print("Error occured!!")
			else:
				print("error 1111")
				input(" ")
				
	def user_deletion(self):
		self.gather_and_send_admin_password("delete user")
		auth_response = self.client.recv(1000).decode('ascii')
		if auth_response == "USER_DELETION_NAME":
			self.gather_and_send_user_for_deletion()
			server_resonse_to_username = self.client.recv(1000).decode('ascii')
			if server_resonse_to_username == "REMOVED":
				print("User sucessfully removed!!")
			else:
				print("error occured")
		else:
			print("error 1111")
			input(" ")

	def gather_and_send_username(self):
		self.client.send("login".encode('ascii'))
		self.username = input("username:")
		self.client.send(self.username.encode('ascii'))

	def check_login_status_and_update_client(self, status):
		if status == "AUTHED":
			print(" ")
			print(colored("Connected to the server!!" , "blue"))
			print("You can now send messages!!")
			current_users = self.client.recv(1000).decode('ascii')
			formatted_users = current_users.replace("'", " ")
			print(f"Users Already in chat:{formatted_users}")
			self.start_threads()
		elif status == "DISCONNECT":
			print(" ")
			print("Issue Authenticating user!! ")
			print(colored("Press enter to close the client!" , "red"))
			input(" ")
		else:
			print("1.Someone is blocking the server so you cannot connect right now!! Try again")
			print("2. or there is an internal error occuring!!")
			print(colored("Press enter to close the client!" , "red"))
			input(" ")

	def start_client(self):
		if action == "login":
				self.gather_and_send_username()
				password = input("password:")
				if len(password) < 1: #avoiding nonetype error
					print("make sure you enter a password")
					input(" ")
				else:
					self.client.send(str(password).encode('ascii'))
					status = self.client.recv(1000).decode('ascii')
					self.check_login_status_and_update_client(status)

		elif action == 'create user':
			self.user_creation()
		elif action == 'delete user':
			self.user_deletion()
		else:
			print("Nothing by that command")
			print("Press Enter to close window")
			input(" ")

	def start_threads(self):
		self.listen_thread = threading.Thread(target = self.listen)
		self.listen_thread.start()
		self.send_thread = threading.Thread(target=self.send_messages)
		self.send_thread.start()
					
	def close_connection(self):
		self.client.send("DISCONNECT_".encode('ascii'))
		self.client.close()

	def listen(self):
		while self.not_kicked == True:
			message = self.client.recv(1000).decode('ascii')
			if message == "**(kicked by admin)**":
				print(colored("You have been kicked from the server! by admin!"))
				self.not_kicked = False
			else:
				print(str(message))
			
	def send_messages(self):
		while self.not_kicked == True:
			message = str(self.username) + ":" +input("")
			if self.not_kicked == False:
				break
			self.client.send(message.encode('ascii'))

client_obj = client_model()
atexit.register(client_obj.close_connection)
client_obj.start_client()