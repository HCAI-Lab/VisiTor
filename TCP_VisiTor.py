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
    raw_function = command.get('function', '')
    function = raw_function.lower() if isinstance(raw_function, str) else ''
    args = command.get('args', [])
    kwargs = command.get('kwargs', {})

    if args is None:
        args = []

    if function == 'click':
        click()
        return {"result": "Click executed"}
    elif function == 'keypress':
        keypress(*args, **kwargs)
        return {"result": "Keypress executed"}
    elif function == 'longkeypress':
        longkeypress(*args)
        return {"result": "Long keypress started"}
    elif function == 'continuouspresskey':
        key = kwargs.get('key') if kwargs else None
        if key is None:
            key = args[0] if args else None
        if not key:
            return {"error": "continuouspresskey requires a key"}
        longkeypress(key)
        return {"result": f"Continuous key press started for '{key}'"}
    elif function == 'whereis':
        # Supports both whereis(path) and Shell style whereis(dir, filename)
        directory = kwargs.get('Dir') if kwargs else None
        if directory is None and kwargs:
            directory = kwargs.get('dir')

        pattern_name = kwargs.get('pattern') if kwargs else None
        if pattern_name is None and kwargs:
            pattern_name = kwargs.get('arg2')

        if directory and pattern_name:
            if isinstance(pattern_name, list):
                pattern_name = pattern_name[0] if pattern_name else None
            path = find_file(directory, str(pattern_name))
            result = whereis(path)
        elif len(args) >= 2:
            path = find_file(args[0], args[1])
            result = whereis(path)
        else:
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
    elif function == 'movecursorto':
        x = kwargs.get('x') if kwargs else None
        y = kwargs.get('y') if kwargs else None
        if x is None or y is None:
            if len(args) >= 2:
                x, y = args[0], args[1]
            elif len(args) == 1 and isinstance(args[0], (list, tuple)) and len(args[0]) == 2:
                x, y = args[0][0], args[0][1]
            else:
                return {"error": "movecursorto requires x and y coordinates"}
        coor = (int(x), int(y))
        win32api.SetCursorPos(coor)
        return {"result": f"Cursor moved to {coor[0]}, {coor[1]}"}
    elif function == 'movecursortopattern':
        directory = kwargs.get('Dir') if kwargs else None
        if directory is None and kwargs:
            directory = kwargs.get('dir')
        if directory is None:
            directory = args[1] if len(args) >= 2 else None
        if directory is None:
            directory = addressfinder()

        pattern_name = kwargs.get('pattern') if kwargs else None
        if pattern_name is None and kwargs:
            pattern_name = kwargs.get('arg2')
        if pattern_name is None:
            pattern_name = args[0] if args else None
        if not pattern_name:
            return {"error": "movecursortopattern requires a pattern name"}

        path = find_file(directory, str(pattern_name).lower())
        coor_choice = whereis(path)
        if isinstance(coor_choice, tuple):
            naturalmove((int(coor_choice[0]), int(coor_choice[1])))
            return {"result": f"Cursor moved to pattern '{pattern_name}' at {coor_choice}"}
        return {"error": str(coor_choice)}
    elif function == 'whatisonscreen':
        directory = kwargs.get('Dir') if kwargs else None
        if directory is None and kwargs:
            directory = kwargs.get('dir')
        if directory is None:
            directory = args[0] if args else None
        if not directory:
            return {"error": "whatisonscreen requires a directory"}

        modules = kwargs.get('modules') if kwargs else None
        if modules is None and kwargs:
            modules = kwargs.get('arg2')
        if modules is None:
            modules = args[1:] if len(args) > 1 else []
        if isinstance(modules, str):
            modules = [modules]
        if not modules:
            return {"error": "whatisonscreen requires one or more module names"}

        found_modules = []
        for module in modules:
            path = find_file(directory, module)
            coor_choice = whereis(path)
            if isinstance(coor_choice, tuple):
                found_modules.append(module)

        if not found_modules:
            return {"result": [], "message": "crap"}
        return {"result": found_modules}
    elif function == 'getmouselocation':
        pos = pyautogui.position()
        return {"result": f"Mouse position: {pos.x}, {pos.y}"}
    else:
        return {"error": f"Unknown function: {raw_function}"}

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