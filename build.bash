!#/bin/bash

#Process command line arguments
if [ $# -ne 1 ]; then
    echo "Use: $0 --help for usage instructions"
    exit 1
fi

method = $1

if [ $method = "--help" ]; then
    echo "Usage: $0 [--help] [--run]"
    echo "--help: Prints this message"
    echo "--run [file]: Runs the server or client"
    exit 0
elif [ $method = "--run" ]; then
    if [ $# -ne 2 ]; then
        echo "Use: $0 --help for usage instructions"
        exit 1
    fi
    file = $2
    if [ $file = "server" ]; then
        echo "Running server"
        python3 server.py &
    elif [ $file = "client" ]; then
        echo "Running client"
        python3 client.py &
    elif [ $file = "test" ]; then
        echo "Running tests script"
        bash test_run.bash
    else
        echo "Invalid file"
        exit 1
    fi
elif [ $method = "--test" ]; then
    echo "Running tests script"
    bash test_run.bash
else
    echo "Invalid method"
    exit 1
fi
        
