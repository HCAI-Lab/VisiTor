from Utils import *
import os
import random
import subprocess

actions = ("Heads","Tails")
feedbacks = ("Match","MisMatch")
action = random.choice(actions)
directory = r"C:\Users\ambkh\Downloads\VisiTor-main"
VisiTor_directory = r"C:\Users\ambkh\Downloads\VisiTor-main\VisiTor.py"
def ActionTaking(action):
    os.system(f"python {VisiTor_directory} whereis --Dir {directory} --arg2 {action}")
    os.system(f"python {VisiTor_directory} movecursortopattern --Dir {directory} --arg2 {action}")
    os.system(f"python {VisiTor_directory} click")
def FeedbackCheck(feedbacks):
    command = f"python {VisiTor_directory} whatisonscreen --Dir {directory} --arg2 {feedbacks[0]} {feedbacks[1]}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    # Capture the output
    command_output = result.stdout
    print(command_output)
    return command_output
ActionTaking(action)
FeedbackCheck(feedbacks)