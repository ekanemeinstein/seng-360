'''
Wil Fredrickson Fall 2021
Created for SENG360 Assignment 3
It's garbage, but it's MY garbage
'''

import sqlite3
import sys
import os
import getpass

##change this to create a new database with a new name automatically
dbname='test.db'

def leave(GIVEN_NAME,CHAT_NUM):
	userin=input("Do you really want to leave this chatroom?\n(Y/N)\n")
	if userin=="Y":
		interface.execute('''BEGIN''')
		result=interface.execute('''
		SELECT COUNT(1) FROM chatroom WHERE num= ?;
		''',(CHAT_NUM,))
		for row in result:
			if row[0]==1:
				##as last member leaves, delete the room
				result=interface.execute('''
				DELETE FROM `message` WHERE num= ?;
				''',(CHAT_NUM,))
################delete paths as well
				result=interface.execute('''
				DELETE FROM `chatnames` WHERE num= ?;
				''',(CHAT_NUM,))
			result=interface.execute('''
			DELETE FROM `chatroom` WHERE username= ? AND num= ?;
			''',(GIVEN_NAME,CHAT_NUM,))
			interface.execute('''COMMIT''')
			print("Chatroom left, returning to Home")
	else:
		print("Returning to chatroom")
###CHANGE THIS###CHANGE THIS###CHANGE THIS###CHANGE THIS###CHANGE THIS

def purge(GIVEN_NAME,CHAT_NUM):
	result=interface.execute('''
	SELECT name FROM chatnames WHERE num= ?
	''',(CHAT_NUM,))
	for row in result:
		print("Do you really want to delete all your messages in",row[0],"?")
	userin=input("(Y/N)\n")
	if userin=='Y':
			interface.execute('''BEGIN''')
			interface.execute('''
			UPDATE `message` SET content='Message Deleted' 
			WHERE username= ? AND num= ?;
			''',(GIVEN_NAME,CHAT_NUM,))
			interface.execute('''COMMIT''')
			print("All your messages in this chatroom have been deleted")
###AND DELETE FILE PATH
	else:
		print("Returning to Chatroom")
###CHANGE THIS###CHANGE THIS###CHANGE THIS###CHANGE THIS###CHANGE THIS

def delete_message(GIVEN_NAME,CHAT_NUM):
	MESSAGE_NUM=input("Which message ID would you like to delete? input 'exit' to return\n")
	if MESSAGE_NUM=='exit':
		print("Returning to chatroom")
	else:
		result=interface.execute('''
		SELECT COUNT(1) FROM `message` 
		WHERE num= ? AND username= ? AND indexnum= ?;
		''',(CHAT_NUM,GIVEN_NAME,MESSAGE_NUM,))
		for row in result:
			if row[0]==0:
				print("You do not have permission to delete this message")
			else:
				interface.execute('''BEGIN''')
				interface.execute('''
				UPDATE `message` SET content= 'Message Deleted' 
				WHERE num= ? AND indexnum= ?;
				''',(CHAT_NUM,MESSAGE_NUM,))
				interface.execute('''COMMIT''')
############and delete the file at the end of the path
				print("Message Content Deleted")
###CHANGE THIS###CHANGE THIS###CHANGE THIS###CHANGE THIS###CHANGE THIS			

def update_chat(CHAT_NUM):
	NEW_NAME=input("What would you like to rename this chatroom to?\n")
	interface.execute('''BEGIN''')
	interface.execute('''
	UPDATE `chatnames` SET name= ? 
	WHERE num= ?;
	''',(NEW_NAME,CHAT_NUM,))
	interface.execute('''COMMIT''')
	print("Chatroom Name Updated")

def view_message(CHAT_NUM):
	result=interface.execute('''
	SELECT 
		CASE
		WHEN EXISTS(SELECT * FROM message WHERE num=?)
			THEN (SELECT MAX(indexnum) FROM message WHERE num=?)
			ELSE 0
		END
	''',(CHAT_NUM,CHAT_NUM,))
	for row in result:
		if row[0]==0:
			print("There are no messages in this chatroom")
		else:
			print("There are", row[0],"messages in this chat, which would you like to see?")
			userin=input()
			if 0<int(userin)<=row[0]:
				result2=interface.execute('''
				SELECT username, content FROM message 
				WHERE num= ? AND indexnum= ?;
				''',(CHAT_NUM,userin,))
				for row2 in result2:
					print(row2[1])
				#####this just prints the path, need to improve to handle files
				##leave it at this if message deleted
			else:
				print("Requested message does not exist")
	

def create(GIVEN_NAME,CHAT_NUM):
##when this gets working, it'll be "submit a file, and then it'll store it instead of this"
	userin=input("Submit some text\n")
	INDEXNUMBER=0
	result=interface.execute('''
	SELECT 
		CASE
		WHEN EXISTS(SELECT * FROM message WHERE num=?)
			THEN (SELECT MAX(indexnum) FROM message WHERE num=?)+1
			ELSE 1
		END;
	''',(CHAT_NUM,CHAT_NUM))
	for row in result:
		INDEXNUMBER=row[0]
	interface.execute('''BEGIN''')
	interface.execute('''
	INSERT INTO `message` (num, indexnum, content, username) VALUES
	(?,?,?,?);	
	''',(CHAT_NUM,INDEXNUMBER,userin,GIVEN_NAME,))
	interface.execute('''COMMIT''')
	print("Message Submitted")
###CHANGE THIS###CHANGE THIS###CHANGE THIS###CHANGE THIS###CHANGE THIS

def add_user(CHAT_NUM):
	NEW_USER=input("Who would you like to add?\n")
	result=interface.execute('''
	SELECT COUNT(1) FROM `accounts` 
	WHERE username= ?;
	''',(NEW_USER,))
	for row in result:
		if row[0]==1:
				result=interface.execute('''
				SELECT COUNT(1) FROM `chatroom` 
				WHERE num= ? AND username= ?;
				''',(CHAT_NUM,NEW_USER,))
				for row in result:
					if row[0]==1:
						interface.execute('''BEGIN''')
						interface.execute('''
						INSERT INTO `chatroom` (username, num) VALUES
						(?,?);
						''',(NEW_USER,CHAT_NUM))
						interface.execute('''COMMIT''')
						print("User", NEW_USER, "has been added")
					else:
						print("That user is already in this chatroom!")
		else:
			print("No user was found with that name")


def mode_chat(GIVEN_NAME,CHAT_NUM):
	userin=input("[A]dd user, [C]reate, [V]iew, [U]pdate, [D]elete, [P]urge, [L]eave, [R]eturn\n")
	if userin=='A':
		add_user(CHAT_NUM)
		mode_chat(GIVEN_NAME,CHAT_NUM)
	elif userin=='C':
		create(GIVEN_NAME,CHAT_NUM)
		mode_chat(GIVEN_NAME,CHAT_NUM)
	elif userin=='V':
		view_message(CHAT_NUM)
		mode_chat(GIVEN_NAME,CHAT_NUM)
	elif userin=='U':
		update_chat(CHAT_NUM)
		mode_chat(GIVEN_NAME,CHAT_NUM)
	elif userin=='D':
		delete_message(GIVEN_NAME,CHAT_NUM)
		mode_chat(GIVEN_NAME,CHAT_NUM)
	elif userin=='P':
		purge(GIVEN_NAME,CHAT_NUM)
		mode_chat(GIVEN_NAME,CHAT_NUM)
	elif userin=='L':
		leave(GIVEN_NAME,CHAT_NUM)
		mode_console(GIVEN_NAME)
	elif userin=='R':
		print("Returning to chatroom selection")
		mode_console(GIVEN_NAME)
	elif userin=='exit':
		print('Manual Exit')
		sys.exit(1)
	elif userin=='help':
		print("[A]dd User allows you to add a new user to this chatroom\n[C]reate allows you to send a new message\n[V]iew allows you to view a message in this chatroom\n[U]pdate let's you change the name of this chatroom\n[D]elete let's you remove the content of one of your messages\n[P]urge can delete the content of all your sent messages\n[L]eave will remove you from this chatroom permanently\n[R]eturn goes back to chatroom selection")
		mode_chat(GIVEN_NAME,CHAT_NUM)
	else:
		print("Command not understood, make sure it is capitalized, or try \"help\"")
		mode_chat(GIVEN_NAME,CHAT_NUM)

def delete_acc(GIVEN_NAME):
	userin=input("Are you sure you want to delete your account? (Y/N)\n")
	if userin=='Y':
		userin=input("Do you want to delete all your messages as well? (Y/N)\n")
		result=interface.execute('''
		SELECT num FROM `chatroom` where username= ?;
		''',(GIVEN_NAME,))
		if userin=='Y':
			for row in result:
				purge(GIVEN_NAME,row[0])
		for row in result:
			leave(GIVEN_NAME,row[0])
		interface.execute('''BEGIN''')
		interface.execute('''
		DELETE FROM `accounts` WHERE username=?;
		''',(GIVEN_NAME,))
		interface.execute('''COMMIT''')
		print("Returning to Sign in")
		mode_signin()
	else:
		print("Returning to Home")

def join_chat(GIVEN_NAME):
	CHAT_NUM=input("Enter the ID of the Chatroom you wish to join\n")
	result=interface.execute('''
	SELECT COUNT(1) FROM `chatroom` 
	WHERE num= ? AND username= ?;
	''',(CHAT_NUM,GIVEN_NAME,))
	for row in result:
		if row[0]==0:
			print("You do not have access to that chatroom, did you get the ID right?")
		else:
				result=interface.execute('''
				SELECT name FROM `chatnames` WHERE num= ?;
				''',(CHAT_NUM,))
				for row in result:
					print("Entering Chatroom:",row[0])
					mode_chat(GIVEN_NAME,CHAT_NUM)

def view_chat(GIVEN_NAME):
	result=interface.execute('''
	SELECT COUNT(1) FROM `chatroom` 
	WHERE username= ?;
	''',(GIVEN_NAME,))
	for row in result:
		if row[0]==0:
			print("You're not in any chatrooms, trying creating a new one!")
		else:
			result2=interface.execute('''
			SELECT chatroom.num, name 
			FROM chatnames inner join chatroom
			ON chatroom.num = chatnames.num
			WHERE username=?
			ORDER BY chatnames.num;
			''',(GIVEN_NAME,))
			for row2 in result2:
				print("The ID for Room",row2[1],"is",row2[0])

def new_chat(GIVEN_NAME):
	LIST_NAME=input("Who would you like to add to the chatroom?\n")
	result=interface.execute('''
	SELECT COUNT(1) FROM accounts
	WHERE username= ?;
	''',(LIST_NAME,))
	for row in result:
		if row[0] ==0:
			print("No match found for that username")
		else:
			FIRST_OPEN=0
			interface.execute('''BEGIN''')
			result=interface.execute('''
			SELECT 
				CASE
				WHEN EXISTS(SELECT num FROM chatroom)
					THEN (SELECT MAX(num) FROM chatroom)+1
					ELSE 1
				END;
			''')
			for row in result:
				FIRST_OPEN=row[0]
			interface.execute('''
			INSERT INTO `chatroom` (username, num) VALUES
			(?,?),(?,?);
			''', (GIVEN_NAME, FIRST_OPEN, LIST_NAME, FIRST_OPEN))
			print("Chatroom Created")
			while 1:
				userin=input("Would you like to add another user (Y/N)?\nYou can do this later as well\n")
				if userin=='N':
					break
				elif userin=='Y':
					LIST_NAME=input("Who would you like to add to the chatroom?\n")
					result=interface.execute('''
					SELECT COUNT(1) FROM accounts
					WHERE username= ?;
					''',(LIST_NAME,))
					for row in result:
						if row[0] ==0:
							print("No match found for that username")
						else:
							interface.execute('''
							INSERT INTO `chatroom` (username, num) VALUES
							(?,?);
							''', (LIST_NAME, FIRST_OPEN))
							print("Listed user added to chatroom")
				else:
					print("Please answer with [Y]es or [N]o")
			CHAT_NAME=input("What would you like to name the chatroom? This can be changed later\n")
			interface.execute('''
			INSERT INTO `chatnames` (name, num) VALUES
			(?,?);
			''', (CHAT_NAME, FIRST_OPEN))
			interface.execute('''COMMIT''')
			print("Chatroom created, you can join it with the Join command using chat ID",FIRST_OPEN)

def find():
	print("Displaying all usernames in the system")
	result=interface.execute('''
	SELECT username FROM accounts;
	''')
	for row in result:
		print(row[0])

def mode_console(GIVEN_NAME):
	userin=input("[F]ind, [N]ew, [V]iew, [J]oin, [D]elete account, [R]eturn\n")
	if userin== 'F':
		find()
		mode_console(GIVEN_NAME)
	elif userin== 'N':
		new_chat(GIVEN_NAME)
		mode_console(GIVEN_NAME)
	elif userin== 'V':
		view_chat(GIVEN_NAME)
		mode_console(GIVEN_NAME)
	elif userin== 'J':
		join_chat(GIVEN_NAME)
		mode_console(GIVEN_NAME)
	elif userin== 'D':
		delete_acc(GIVEN_NAME)
		mode_console(GIVEN_NAME)
	elif userin=='R':
		print("Signing out") ##aka going back
		mode_signin()
	elif userin=='exit':
		print('Manual Exit')
		sys.exit(1)
	elif userin== 'help':
		print("[F]ind displays all users\n[N]ew allows you to create a new chatroom\n[V]iew show all the chatrooms you are in\n[J]oin lets you join a chatroom you're a member of\n[D]elete allows you to delete your account\n[R]eturn signs you out")
		mode_console(GIVEN_NAME)
	else:
		print("Command not understood, make sure it is capitalized, or try \"help\"")
		mode_console(GIVEN_NAME)

def mode_signin():
	userin=input("[R]egister or [S]ign In\n")
	if userin== 'R':
		register()
	elif userin== 'S':
		signin()
	elif userin== 'help':
		print("[R]egister to create a new account, or [S]ign In if you have one already")
		mode_signin()
	elif userin== 'exit':
		print('Manual Exit')
		sys.exit(1)
	else:
		print("Command not understood, make sure it is capitalized, or try \"help\"")
		mode_signin()

def register_pass(GIVEN_NAME, GIVEN_PASS, interface):
	interface.execute('''BEGIN''')
	result=interface.execute('''
	INSERT INTO `accounts` (username, password) VALUES
	(?,?);
	''',(GIVEN_NAME,GIVEN_PASS,))
	interface.execute('''COMMIT''')
	print("Success")
	return

def register(GIVEN_NAME, GIVEN_PASS, interface):
	print("Trying to register " + GIVEN_NAME + " in database")
	result=interface.execute('''
	SELECT COUNT(1) FROM accounts
	WHERE username= ?;
	''',(GIVEN_NAME,))
	for row in result:
		if row[0] ==1:
			print("Failed")
			return False
		else:
			register_pass(GIVEN_NAME, GIVEN_PASS, interface)
			return True

def signin(GIVEN_NAME, GIVEN_PASS, interface):
	print("Trying to sign in" + GIVEN_NAME)
	result=interface.execute('''
	SELECT COUNT(1) FROM accounts
	WHERE username= ? AND password= ?;
	''',(GIVEN_NAME,GIVEN_PASS,))
	for row in result:
		if row[0] ==1:
			print(GIVEN_NAME + " now signing in")
			return True
		else:
			return False
