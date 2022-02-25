#!/bin/bash

#Process ensure on ly one or 2 command line arguments are present
if [ $# -ne 1 ] && [ $# -ne 2 ]; then
    echo "Use: $0 --help for usage instructions"
    exit 1
fi

if [ $1 = "--help" ]; then
    echo "Usage: $0 [--help] [--run]"
    echo "--help: Prints this message"
    echo "--run [file]: Runs the server or client"
    exit 0
elif [ $1 = "--run" ]; then
    if [ $# -ne 2 ]; then
        echo "Use: $0 --help for usage instructions"
        exit 1
    fi

    if [ $2 = "server" ]; then
        echo "Running server, please check server.log for output"
        python3 server.py 2> server.log &
    elif [ $2 = "client" ]; then
        echo "Running client"
        python3 client.py
    elif [ $2 = "test" ]; then
        echo "Running tests script"
        bash test_run.bash
    else
        echo "Invalid file"
        exit 1
    fi
elif [ $1 = "--test" ]; then
    echo "Running tests script"
    bash test_run.bash
else
    echo "Invalid method"
    exit 1
fi
        
