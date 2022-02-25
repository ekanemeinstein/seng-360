#!/bin/bash


#Script to test run server.py and client.py to make sure they work

#Create a function to print exit code and then exit
#Input: exit code
function exit_w_code() {
    echo "Exiting script with code: $1"
    exit $1
}

#Run server.py in background if it exits with an error, then exit the script with that error
python3 server.py &
server_pid=$!

if [ $? -ne 0 ]; then
    kill $server_pid
    exit_w_code $?
fi

#sleep for two seconds to make sure the server is up
sleep 2

#Run ps to check if server.py is running
#If it is not running, print error message and exit
ps -p $server_pid > /dev/null
if [ $? -ne 0 ]; then
    echo "Server.py failed to start"
    kill $server_pid
    exit_w_code 2
fi


#Run client.py for 10 seconds
sleep 8
timeout 2 python3 client.py
client_exit_status=$?

if [ $client_exit_status -eq 124 ]; then
    echo "Client timed out"
    kill $server_pid
    exit_w_code 0
fi
exit_w_code $client_exit_status
