import socket
import json
from Functions import *
import threading

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            try:
                command = json.loads(data.decode('utf-8'))
                result = execute_command(command)
                conn.sendall(json.dumps(result).encode('utf-8'))
            except json.JSONDecodeError:
                conn.sendall(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
            except Exception as e:
                conn.sendall(json.dumps({"error": str(e)}).encode('utf-8'))

def execute_command(command):
    function = command.get('function')
    args = command.get('args', [])
    kwargs = command.get('kwargs', {})

    if function == 'click':
        click()
        return {"result": "Click executed"}
    elif function == 'keypress':
        keypress(*args, **kwargs)
        return {"result": "Keypress executed"}
    elif function == 'longkeypress':
        longkeypress(*args)
        return {"result": "Long keypress started"}
    elif function == 'whereis':
        result = whereis(*args)
        return {"result": result}
    elif function == 'find_file':
        result = find_file(*args)
        return {"result": result}
    elif function == 'addressfinder':
        result = addressfinder()
        return {"result": result}
    elif function == 'naturalmove':
        naturalmove(*args, **kwargs)
        return {"result": "Cursor moved"}
    elif function == 'getMouseLocation':
        pos = pyautogui.position()
        return {"result": f"Mouse position: {pos.x}, {pos.y}"}
    else:
        return {"error": f"Unknown function: {function}"}

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    start_server()