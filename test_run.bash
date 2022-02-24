#!/bin/bash


#Script to test run server.py and client.py to make sure they work

#Run server.py in background if it exits with an error, then exit the script with that error
python3 server.py &
server_pid=$!

if [ $? -ne 0 ]; then
    kill $server_pid
    exit $?
fi

#Run client.py for 10 seconds
timeout 10 python3 client.py
client_exit_status=$?

if [ $client_exit_status -eq 124 ]; then
    echo "Client timed out"
    exit 0
fi
exit $client_exit_status