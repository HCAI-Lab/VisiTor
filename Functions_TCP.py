import socket
import json

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432  # The port used by the server


def send_command(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(json.dumps(command).encode('utf-8'))
        data = s.recv(1024)
    return json.loads(data.decode('utf-8'))


if __name__ == "__main__":
    print("Welcome to the Utils TCP client!")

    function = input("Enter the function you want to execute: ")

    args = []
    while True:
        arg = input("Enter an argument (or press Enter to finish): ")
        if arg == "":
            break
        args.append(arg)

    command = {
        "function": function,
        "args": args
    }

    result = send_command(command)
    print("Result:", result)