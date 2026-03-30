# VisiTor: A module to simulate the movement of eyes and hands

VisiTor is a Python-based tool that enables computer agents to interact with computer environments. It is capable of simulating keyboard and mouse movements, finding visual patterns on the screen and also visualizing where on the screen the agent is paying attention to. VisiTor was initially developed to enable interaction for ACT-R agents to simulate human users. However, other agents developed using other cognitive architectures or other computer agents can still use this tool to enable interaction and validate the shifts of attention across the screen.

# (NEW) Attention Visualization Demos

VisiTor enables visualization methods for attention areas. In our current implementation, we have implemented *fovea simulation* and *gaze point simulation*. 

[Visualization Demo 1](https://pennstateoffice365-my.sharepoint.com/:v:/r/personal/abb6024_psu_edu/Documents/VisiTor_Demo/Media1.mp4?csf=1&web=1&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=24CKVH)

[Visualization Demo 2](https://pennstateoffice365-my.sharepoint.com/:v:/r/personal/abb6024_psu_edu/Documents/VisiTor_Demo/Media2.mp4?csf=1&web=1&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=AD1Krn)

## Features

- **Mouse and Keyboard Simulation**: Natural movement patterns and key press simulation
- **Visual Pattern Recognition**: Screen element detection and location
- **Attention Visualization**: Simulates human attention patterns including foveal vision
- **TCP Server Integration**: Remote control capabilities through network communication
- **Cross-Platform Support**: Works on Windows systems with Python 3.x

## Requirements

You first are going to need to install the requirements. Installation of the requirements requires the following code on the command prompt:

```bash
pip install -r requirements.txt
```

## Getting Started

### Initial Setup

You may first open the file "GettingStarted.py". First, you will need to run the file through the command prompt [How to open command prompt](https://www.howtogeek.com/235101/10-ways-to-open-the-command-prompt-in-windows-10/#:~:text=Press%20Windows%2BR%20to%20open,open%20an%20administrator%20Command%20Prompt.). Then you will need to change the directory by the following code:

```bash
cd address/to/your/directory
```

**Note**: If the address to your directory has space (for example "c:/users/important information"), you need to put the address in quotation marks so that Windows understands that space is a part of the address.

Now you are ready to run GettingStarted.py:
```bash
python GettingStarted.py
```

The setup process will guide you through:
1. Identifying your environment (click twice to create a bounding box)
2. Defining visual modules within the environment
3. Defining feedback modules (can use the entire screen)
4. Saving your configuration

### Core Functions

The main file is "Shell_VisiTor.py". To run the file on the command prompt, you will need three arguments, two of which are optional. The basic syntax is:

```bash
python Shell_VisiTor.py <function> [--Dir <directory>] [--arg2 <arguments>]
```

Available functions:

| Function | Description | Required Arguments |
|----------|-------------|-------------------|
| `click` | Simulates mouse click | None |
| `Keypress` | Simulates key press | `--arg2 <key>` |
| `movecursorto` | Moves cursor to coordinates | `--arg2 <x> <y>` |
| `whatisonscreen` | Detects visible modules | `--Dir <path> --arg2 <module1> <module2> ...` |
| `getMouseLocation` | Returns cursor position | None |
| `whereis` | Locates specific module | `--Dir <path> --arg2 <module>` |
| `movecursortopattern` | Moves to visual pattern | `--Dir <path> --arg2 <pattern>` |
| `continuouspresskey` | Holds key down | `--arg2 <key>` |

Example usage:
```bash
python Shell_VisiTor.py movecursortopattern --Dir Directory/to/where/you/want --arg2 SignInButton
```

### TCP Server Usage

VisiTor includes a TCP server for remote control:

1. Start the server:
```bash
python TCP_Visitor.py
```

2. Send commands using the Functions_TCP.py client.

## Calling from Common Lisp

Even though the code is written in Python, it is accessible from any programming language by accessing the command prompt. Here's how to run this code from Common Lisp (CLISP):

### Loading inferior-shell

Load the inferior-shell in SLIME with:

```lisp
(ql:quickload 'inferior-shell)
```

Then with inferior-shell loaded, you can execute VisiTor commands:

```lisp
(inferior-shell:run/ss '("python" "C:/Route/To/The/Directory/Visitor.py" "Function" "--Dir" "Directory" "--arg2" "arg2 values each inside a quotation"))
```

## Architecture

VisiTor consists of several key components:

- **Shell_VisiTor.py**: Command-line interface for direct interaction
- **TCP_Visitor.py**: Network server for remote control
- **Functions.py**: Core functionality classes:
  - `EyeTracker`: Attention visualization
  - `VisionFunctions`: Pattern recognition
  - `MotorFunctions`: Input simulation
  - `UtilityFunctions`: Helper methods

## Development

### Extended Pattern Recognition

VisiTor uses multiple methods for pattern recognition:

- PyAutoGUI's image recognition
- OpenCV template matching
- Deep learning-based feature extraction (ResNet50)
- SIFT feature matching

### Natural Movement Simulation

Mouse movements use geometric interpolation to create natural-looking cursor paths, simulating human-like behavior.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.



## Author

Amirreza Bagherzadeh
- Email: abb6024@psu.edu
- GitHub: [ar-zadeh](https://github.com/ar-zadeh)
- HCAI Laboratory
