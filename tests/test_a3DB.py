import sqlite3
import sys
sys.path.append('.')
import a3DB

dbname='test.db'
interface = sqlite3.connect(dbname)

def test_register():
    a3DB.register("user", "password", interface)
    run = interface.cursor()
    run.execute("SELECT * FROM accounts;")
    result = run.fetchall()
    assert result[0][0] == 'user'
    assert result[0][1] == 'password'

def test_signin():
    assert a3DB.signin("user", "password", interface) == True

def test_find():
    a3DB.register("user1", "password", interface)
    result = a3DB.find("user3", interface)
    assert result[0] == 'user'
    assert result[1] == 'user1'

def test_new_chat():
    result = a3DB.new_chat("user", "user1", interface)
    assert result != -1

def test_teardown():
    interface.close()
    interface2 = sqlite3.connect(dbname)
    a3DB.delete_acc("user", interface2)
    a3DB.delete_acc("user1", interface2)
    assert a3DB.find("user", interface2) == []

