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
interface = None
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

def purge(GIVEN_NAME, CHAT_NUM, interface):
	result=interface.execute('''
	SELECT name FROM chatnames WHERE num= ?
	''',(CHAT_NUM,))
	for row in result:
		interface.execute('''BEGIN''')
		interface.execute('''
		UPDATE `message` SET content='Message Deleted' 
		WHERE username= ? AND num= ?;
		''',(GIVEN_NAME,CHAT_NUM,))
		interface.execute('''COMMIT''')
		return
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
	

def create(GIVEN_NAME, CHAT_NUM, userin, interface):
##when this gets working, it'll be "submit a file, and then it'll store it instead of this"
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
	return
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

def delete_acc(GIVEN_NAME, interface):
	result=interface.execute('''
	SELECT num FROM `chatroom` where username= ?;
	''',(GIVEN_NAME,))
	for row in result:
		purge(GIVEN_NAME,row[0],interface)
	#for row in result:
	#	leave(GIVEN_NAME,row[0],interface)
	interface.execute('''BEGIN''')
	interface.execute('''
	DELETE FROM `accounts` WHERE username=?;
	''',(GIVEN_NAME,))
	interface.execute('''COMMIT''')
	return

def join_chat(GIVEN_NAME, CHAT_NUM, interface):
	result=interface.execute('''
	SELECT COUNT(1) FROM `chatroom` 
	WHERE num= ? AND username= ?;
	''',(CHAT_NUM,GIVEN_NAME,))
	for row in result:
		if row[0]==0:
			return False
		else:
			result=interface.execute('''
			SELECT name FROM `chatnames` WHERE num= ?;
			''',(CHAT_NUM,))
			for row in result:
				print("Entering Chatroom:",row[0])
				return row[0]

def view_chat(GIVEN_NAME, interface):
	list = []
	result=interface.execute('''
	SELECT COUNT(1) FROM `chatroom` 
	WHERE username= ?;
	''',(GIVEN_NAME,))
	for row in result:
		if row[0]==0:
			break
		else:
			result2=interface.execute('''
			SELECT chatroom.num, name 
			FROM chatnames inner join chatroom
			ON chatroom.num = chatnames.num
			WHERE username=?
			ORDER BY chatnames.num;
			''',(GIVEN_NAME,))
			for row2 in result2:
				string = "Room name: " + str(row2[1]) + ", ID: " + str(row2[0]) + "\n"
				list.append(string)
	return list

def new_chat(GIVEN_NAME, LIST_NAME, interface):
	result=interface.execute('''
	SELECT COUNT(1) FROM accounts
	WHERE username= ?;
	''',(LIST_NAME,))
	for row in result:
		if row[0] ==0:
			return -1
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
			return FIRST_OPEN

def name_new_chat(CHAT_NAME, FIRST_OPEN, interface):
	interface.execute('''
	INSERT INTO `chatnames` (name, num) VALUES
	(?,?);
	''', (CHAT_NAME, FIRST_OPEN))
	interface.execute('''COMMIT''')
	return


def find(my_name, interface):
	print("Displaying all usernames in the system")
	result=interface.execute('''
	SELECT username FROM accounts;
	''')
	list = []
	for row in result:
		if row[0] != my_name:
			list.append(row[0])
	return list

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
	print("Trying to sign in " + GIVEN_NAME)
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
