# VisiTor

VisiTor is a visual GUI automation tool that allows you to define functional visual elements on your screen and interact with them programmatically. It leverages Python for screen capturing, template matching (via PyTorch/OpenCV), and simulating user interactions (mouse clicks, mouse movement, and keyboard presses). Furthermore, it features a Common Lisp interface explicitly designed for integration within Emacs workflows.

## What VisiTor Does

1. **Environment Definition**: By executing `GettingStarted.py`, you can capture screenshots and crop "visual modules" (like buttons or text boxes) that you want to track or continuously interact with.
2. **Visual Automation**: It scans the screen to find these defined modules (`whatisonscreen`, `whereis`) and performs actions natively using `pyautogui` and `win32api` (e.g., `click`, `movecursorto`, `keypress`, `longkeypress`).
3. **Lisp/Emacs Integration**: VisiTor exposes its Python functionality to Common Lisp via two different implementations (`Function_TCP.lisp` and `Fucntion_shell.lisp`), making it accessible to Emacs via tools like SLIME or SLY.

---

## How to Run VisiTor in Emacs

In order to use VisiTor in Emacs, you will need Quicklisp setup with your Common Lisp implementation (to load required libraries like `usocket`, `cl-json`, and `inferior-shell`) alongside SLIME/SLY.

There are two primary ways to run VisiTor: using the **TCP Server** method or the **Shell** method.

### 1. The TCP Server Method (Recommended)

This method is faster and more efficient as it doesn't incur the overhead of spawning a new Python process for each command. It keeps a Python server running persistently in the background and communicates over a local socket.

**Step 1:** Start the Python TCP Server. Open a terminal outstide Emacs (or use `M-x shell`) and execute:
```bash
python TCP_VisiTor.py
```
*(The server defaults to listening on `127.0.0.1:65432`)*

**Step 2:** Open Emacs and start your Common Lisp REPL (e.g., `M-x slime` or `M-x sly`).

**Step 3:** Load the TCP Lisp bridge:
```lisp
(load "Function_TCP.lisp")
```
*Note: This automatically quickloads `:usocket` and `:cl-json`.*

**Step 4:** You can now natively call VisiTor automation functions from within Emacs. For example:
```lisp
(click)
(keypress "a")
(whereis "my_visual_module")
```

### 2. The Shell Method

This method runs the corresponding Python CLI script (`Shell_VisiTor.py`) directly from Lisp each time you invoke a function.

**Step 1:** Ensure your Python executable path is configured correctly in `Fucntion_shell.lisp`. 
Check the `run-shell-command` defun and update the `C:\Users\ambkh\anaconda3\python.exe` path if your Python interpreter is located elsewhere.

**Step 2:** In Emacs, start your REPL (`M-x slime` or `M-x sly`).

**Step 3:** Load the shell functions:
```lisp
(load "Fucntion_shell.lisp")
```
*Note: This automatically quickloads `:inferior-shell`.*

**Step 4:** You can invoke commands that internally build shell arguments and invoke the Python executable:
```lisp
(run-visitor "click")
(run-visitor "Keypress" nil '("b"))
```