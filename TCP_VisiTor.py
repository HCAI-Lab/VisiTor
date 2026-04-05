import socket
import json
from Functions import *
import threading
import os
import subprocess
import sys
import importlib

def auto_install(module_name, package_name=None):
    if package_name is None:
        package_name = module_name
    try:
        return __import__(module_name)
    except ImportError:
        print(f"Module '{module_name}' not found. Installing '{package_name}'...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            # The user specifically asked for "uv pip install", so let's try that if uv is available, 
            # but standard pip is more universal. Wait, the user said: automatically run "uv pip install ..."
            # I will use "uv pip install" as requested.
            subprocess.check_call(["uv", "pip", "install", package_name])
        except Exception as e:
            # Fallback to pip if uv fails or isn't installed
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            except Exception as e2:
                print(f"Failed to install {package_name}: {e2}")
                raise e2
        return __import__(module_name)

# Apply auto_install to dependencies that might be missing
# (socket, json, threading, os, subprocess, sys are stdlib)

from Functions import *

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


def _safe_mouse_position():
    try:
        pos = pyautogui.position()
        return int(pos.x), int(pos.y)
    except Exception:
        try:
            pos = win32api.GetCursorPos()
            return int(pos[0]), int(pos[1])
        except Exception:
            return None


def _set_cursor_pos_verified(x, y):
    target = (int(x), int(y))
    before = _safe_mouse_position()
    errors = []

    try:
        win32api.SetCursorPos(target)
    except Exception as e:
        errors.append(f"win32api.SetCursorPos failed: {e}")

    after = _safe_mouse_position()
    if after != target:
        try:
            pyautogui.moveTo(target[0], target[1], duration=0)
        except Exception as e:
            errors.append(f"pyautogui.moveTo failed: {e}")
        try:
            win32api.SetCursorPos(target)
        except Exception as e:
            errors.append(f"retry SetCursorPos failed: {e}")
        after = _safe_mouse_position()

    return {
        "target": [target[0], target[1]],
        "before": [before[0], before[1]] if before else None,
        "after": [after[0], after[1]] if after else None,
        "moved": after == target,
        "errors": errors,
    }


def _click_verified():
    before = _safe_mouse_position()
    errors = []

    try:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    except Exception as e:
        errors.append(f"win32api.mouse_event failed: {e}")
        try:
            pyautogui.click()
        except Exception as e2:
            errors.append(f"pyautogui.click failed: {e2}")

    after = _safe_mouse_position()
    return {
        "position": [after[0], after[1]] if after else ([before[0], before[1]] if before else None),
        "errors": errors,
    }


def _default_spreadsheet_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Spreadsheet"))


def _default_visual_script_path():
    return os.path.join(_default_spreadsheet_dir(), "visual_v3.py")


def _import_visual_module(module_name="visual_v3"):
    spreadsheet_dir = _default_spreadsheet_dir()
    if spreadsheet_dir not in sys.path:
        sys.path.insert(0, spreadsheet_dir)

    return importlib.import_module(module_name)


def _as_name_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value]
    return [str(value)]


def _first_name(value):
    items = _as_name_list(value)
    return items[0] if items else None


def _use_uia(kwargs):
    value = kwargs.get('use_uia') if kwargs else None
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "t", "yes", "y"}
    return bool(value)


def _default_visicon_json_path():
    return os.path.join(_default_spreadsheet_dir(), "visicons.json")


def _visicon_json_path(kwargs):
    path = kwargs.get('visicon_json') if kwargs else None
    if not path:
        path = _default_visicon_json_path()
    return os.path.abspath(path)


def _load_visicons(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _find_visicon_by_name(visicons, target_name):
    target = str(target_name).strip().casefold()
    for item in visicons:
        name = str(item.get('name', '')).strip().casefold()
        if name == target:
            return item
    return None

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    with conn:
        buffer = ""
        while True:
            data = conn.recv(4096)
            if not data:
                break
            buffer += data.decode('utf-8')

            while '\n' in buffer:
                raw_message, buffer = buffer.split('\n', 1)
                raw_message = raw_message.strip()

                if not raw_message:
                    continue

                try:
                    command = json.loads(raw_message)
                    result = execute_command(command)
                    conn.sendall((json.dumps(result) + "\n").encode('utf-8'))
                    if result.get("quit"):
                        print("Quitting server...")
                        os._exit(0)
                except json.JSONDecodeError:
                    conn.sendall((json.dumps({"error": "Invalid JSON"}) + "\n").encode('utf-8'))
                except Exception as e:
                    conn.sendall((json.dumps({"error": str(e)}) + "\n").encode('utf-8'))

def execute_command(command):
    raw_function = command.get('function', '')
    function = raw_function.lower() if isinstance(raw_function, str) else ''
    args = command.get('args', [])
    kwargs = command.get('kwargs', {})

    if args is None:
        args = []

    if function == 'click':
        click_info = _click_verified()
        return {"result": "Click executed", "details": click_info}
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
        move_info = _set_cursor_pos_verified(x, y)
        target = move_info["target"]
        if move_info["moved"]:
            return {"result": f"Cursor moved to {target[0]}, {target[1]}", "details": move_info}
        return {
            "error": f"Cursor did not reach target {target[0]}, {target[1]}",
            "details": move_info,
        }
    elif function == 'movecursortopattern':
        use_uia = _use_uia(kwargs)

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

        pattern_name = _first_name(pattern_name)
        if not pattern_name:
            return {"error": "movecursortopattern requires a pattern name"}

        if use_uia:
            visicon_path = _visicon_json_path(kwargs)
            if not os.path.isfile(visicon_path):
                return {"error": f"UIA visicon JSON not found: {visicon_path}"}

            try:
                visicons = _load_visicons(visicon_path)
            except Exception as e:
                return {"error": f"Failed reading UIA visicon JSON: {e}"}

            target = _find_visicon_by_name(visicons, pattern_name)
            if not target:
                return {"error": f"UIA item '{pattern_name}' not found in {visicon_path}"}

            position = target.get('position')
            if not isinstance(position, (list, tuple)) or len(position) != 2:
                return {"error": f"UIA item '{pattern_name}' has invalid position: {position}"}

            x, y = int(position[0]), int(position[1])
            naturalmove((x, y))
            return {"result": f"Cursor moved to UIA item '{pattern_name}' at ({x}, {y})"}

        path = find_file(directory, str(pattern_name).lower())
        coor_choice = whereis(path)
        if isinstance(coor_choice, tuple):
            naturalmove((int(coor_choice[0]), int(coor_choice[1])))
            return {"result": f"Cursor moved to pattern '{pattern_name}' at {coor_choice}"}
        return {"error": str(coor_choice)}
    elif function == 'whatisonscreen':
        use_uia = _use_uia(kwargs)

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
        modules = _as_name_list(modules)
        if not modules:
            return {"error": "whatisonscreen requires one or more module names"}

        if use_uia:
            visicon_path = _visicon_json_path(kwargs)
            if not os.path.isfile(visicon_path):
                return {"error": f"UIA visicon JSON not found: {visicon_path}"}

            try:
                visicons = _load_visicons(visicon_path)
            except Exception as e:
                return {"error": f"Failed reading UIA visicon JSON: {e}"}

            found_modules = []
            for module in modules:
                if _find_visicon_by_name(visicons, module):
                    found_modules.append(module)

            if not found_modules:
                return {"result": [], "message": "crap"}
            return {"result": found_modules}

        found_modules = []
        for module in modules:
            path = find_file(directory, module)
            coor_choice = whereis(path)
            if isinstance(coor_choice, tuple):
                found_modules.append(module)

        if not found_modules:
            return {"result": [], "message": "crap"}
        return {"result": found_modules}
    elif function == 'refreshvisicons':
        try:
            visual_v3 = _import_visual_module("visual_v3")
        except Exception as e:
            return {"error": f"Failed to import visual_v3 module: {e}"}

        app_titles = kwargs.get('app_titles') if kwargs else None
        if isinstance(app_titles, str):
            app_titles = [app_titles]

        output_path = kwargs.get('output_path') if kwargs else None

        try:
            if hasattr(visual_v3, "refresh_visicons"):
                refresh_result = visual_v3.refresh_visicons(app_titles=app_titles, output_path=output_path)
                return {"result": "visicons refreshed", "details": refresh_result}

            if app_titles is None and hasattr(visual_v3, "DEFAULT_APP_TITLES"):
                app_titles = visual_v3.DEFAULT_APP_TITLES

            if app_titles is None:
                return {"error": "visual_v3 has no refresh_visicons and no default app titles available"}

            visicons = visual_v3.extract_ui_elements(app_titles)
            return {
                "result": "visicons refreshed",
                "details": {"visicons_count": len(visicons)},
            }
        except Exception as e:
            return {"error": f"visual_v3 refresh failed: {e}"}
    elif function == 'getmouselocation':
        pos = pyautogui.position()
        return {"result": f"Mouse position: {pos.x}, {pos.y}"}
    elif function == 'quit':
        return {"result": "Quitting server", "quit": True}
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