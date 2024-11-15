# VisiTor: A module to simulate the movement of eyes and hands

VisiTor is a tool that enables computer agents to interact with computer environments. It is capable of simulating keyboard and mouse movements, finding visual patterns on the screen and also visualizing where on the screen the agent is paying attention to. VIsiTor was initially developed to enable interaction for ACT-R agents to simulate human users. However, other agents developed using other cognitive architectures or other computer agents can still use this tool to enable interaction and validate the shifts of attention across the screen.   

# Attention Visualization Demos

VisiTor enables visualization methods for attention areas. In our current implementation, we have implemented *fovea simulation* and *gaze point simulation*. 


[Visualization Demo 1](https://pennstateoffice365-my.sharepoint.com/:v:/r/personal/abb6024_psu_edu/Documents/VisiTor_Demo/Media1.mp4?csf=1&web=1&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=24CKVH)



[Visualization Demo 2
](https://pennstateoffice365-my.sharepoint.com/:v:/r/personal/abb6024_psu_edu/Documents/VisiTor_Demo/Media2.mp4?csf=1&web=1&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=AD1Krn)

## Requirement:

You first are going to need to install the requirements. Installation of the requirements requires the following code on the command prompt:

```
pip install -r requirements.txt
```

## Getting Started

You may first open the file "GettingStarted.py". First, you will need to run the file through the command prompt [How to open command prompt](https://www.howtogeek.com/235101/10-ways-to-open-the-command-prompt-in-windows-10/#:~:text=Press%20Windows%2BR%20to%20open,open%20an%20administrator%20Command%20Prompt.). Then you will need to change the directory by the following code.
```
cd address/to/your/directory
```
**Note** if the address to your directory has space (for example "c:/users/important information"), you need to put the address in quotation so that windows understand that space is a part of the address.
Now you are ready to run GettingStarted.py
```
python GettingStarted.py
```
First, you will be asked to identify the environment you are going to use for your problem. You are required to click twice, as you click once, there will be a black box originating from that point to where you mouse is. You will need to make sure that the black box includes the whole environment. After that, you are asked to identify your visual modules within the environment. The process in the same as defining the environment the only difference is that instead of being able to choose any part of the screen, you are limited to the environment you defined earlier. You will need to name these items in a way that you'd be able to recall them later to use them. After that, you will need to define feedback modules but for this one, since sometimes, the environment changes based on the goal, you will be offered to use the whole screen again to identify your feedback modules. And then you can save the files or just close and start again.



The main file is "VisiTor.py". In order to run the file on the command prompt, you will need three arguments two of which are optional. The first argument is the function which you want to use. The options for this argument are one of the following:

- "**click**": Will simulate the action of right-clicking. It gets no argument.
- "**Keypress**": Will simulate the action of a Keypress. It will get an argument: 
  - --arg2 which is going to be the key you want the computer to press.
- "**movecursorto**": Will simulate the movement of the mouse to a specific part of the screen. It will get an argument :
  -  --arg2 which is going to be the "x" and "y" values separated by a space
- "**whatisonscreen**": Will check if any of the modules given can be found at that moment. It will get two arguments: 
  - --Dir: Directory of where the visual modules are defined.
  - --arg2: The visual modules that you want to look for. Each separated by a space
- "**getMouseLocation**": Gets the location of the mouse. It gets no argument.
- "**whereis**": Will find where a module is located. It will get two arguments: 
  - --Dir: Directory of where the visual modules are defined.
  - --arg2: The visual modules that you want to look for.
- "**movecursortopattern**": Will simulate the movement of the mouse to a specific pattern on the screen. It will get two arguments: 
  - --Dir: Directory of where the visual modules are defined.
  - --arg2: The visual modules that you want to look for.

To run the program, your request has to have the following format:

```
python Visitor (The function you want to use) --Dir (Directory) --arg2 (the second argument)
```

For example, for running "*movecursortopattern*" with all the arguments, we have a code similar below

```
python Visitor movecursortopattern --Dir Directory/to/where/you/want --arg2 SignInBotton
```

## Calling from Common lisp

Even though the code is written in Python, it is accessible from any programming language by accessing the command prompt and writing the correct code. In this part, we are going to talk about how to run this code on Common lisp (CLISP):

### Loading inferior-shell

You can load the inferior-shell in the slime by the following code 

```commonlisp
(ql:quickload 'inferior-shell)
```

Then with the inferior-shell loaded, we can write the following code:

```commonlisp
(inferior-shell:run/ss '("python" "C:/Route/To/The/Directory/Visitor.py" "Function" "--Dir" "Directory" "--arg2" "arg2 values each inside a quotation" ))
```
# Authorship
Amirreza Bagherzadeh [Email](mailto:abb6024@psu.edu),<a href="https://github.com/ar-zadeh">Github page</a>
