#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys #Read arguements
# from pymouse import PyMouse
import pyautogui #Finds Patterns, click and keyboard stuff
from pathlib import Path # Contruction of paths
from time import sleep # To simulate pause
import argparse
import numpy as np  # Matrix stuff
import os # For moving between folders and stuff
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import shutil #Moving files
import pickle #Saving files
import tkinter # For GUI i saving files
import pygame #Gets mouse position and stuff
from tkinter import filedialog # GUI stuff
from tkinter.messagebox import showinfo
import glob #finds specific types of files
import tkinter as tk
from tkinter import filedialog as fd
import random




# Press a key and hold it

def keypress(key, time = 0.1):

    # presses the key
    print(key[0])
    key = key[0]
    pyautogui.keyDown(key)
    # waits a certain amount before releasing the key
    sleep(time)
    # releases the key
    pyautogui.keyUp(key)


# Click at a specific location of the screen
def click():

    pyautogui.mouseDown()
        # waits a 0.8s before releasing the key

    sleep(0.8)
    pyautogui.mouseUp()
# finds the location of a pattern????
def locate_pic(filename):
    pic=None
    while pic is None:
        pic = pyautogui.locateOnScreen(filename,confidence=.8)
        return pic
#Finds the location of a file in a directory and adds the extention to it
def find_file(address,filename):
    for ext in ['png','jpg','PNG']:
        arr = glob.glob(f'{address}/{filename}.{ext}',)
        if len(arr)>0:
            break
    return arr[0]
#Finds the location of a pattern
def whereis(path):
    pic = locate_pic(path)
    if pic ==None:
        return "Pattern doesn't exist"
    else:
        x = pic[0]+pic[2]/2
        y = pic[1]+pic[3]/2
        return x,y
#Finds the location of the top corner of a pattern
def whereis_top(path):
    pic = locate_pic(path)
    if pic ==None:
        return "Pattern doesn't exist"
    else:
        x = pic[0]
        y = pic[1]
        return x,y
#Just clicks
def PlainClick():
    pyautogui.click()
    
    
#=========
# Creates a set of points between an origin and a destination
def getEquidistantPoints(p1, p2, parts):
    return zip(np.geomspace(p1[0], p2[0], parts+1),
               np.geomspace(p1[1], p2[1], parts+1))
#=========
#A more natural movement
def getgeomPoints(p1,p2,parts):
    if (p1[0] ==p2[0]) or (p1[1] == p2[1]):
        return [p1]
    if p2[0]-p1[0]>=0:
        if p2[1]-p1[1]>=0:
            return zip([-1*_+p2[0] for _ in list(reversed(np.geomspace(1, p2[0]-p1[0], parts+1)-1))],[_+p2[1] for _ in list(reversed(np.geomspace(1, p2[1]-p1[1], parts+1)-1))])
        else:
            return zip([-1*_+p2[0] for _ in list(reversed(np.geomspace(1, p2[0]-p1[0], parts+1)-1))],[_+p2[1] for _ in list(reversed(np.geomspace(1, p1[1]-p2[1], parts+1)-1))])
    else:
        if p2[1]-p1[1]>=0:
            return zip([_+p2[0] for _ in list(reversed(np.geomspace(1, p1[0]-p2[0], parts+1)-1))],[-1*_+p2[1] for _ in list(reversed(np.geomspace(1, p2[1]-p1[1], parts+1)-1))])
        else:
            return zip([_+p2[0] for _ in list(reversed(np.geomspace(1, -p2[0]+p1[0], parts+1)-1))],[_+p2[1] for _ in list(reversed(np.geomspace(1, -p2[1]+p1[1], parts+1)-1))])


#=========

#=========
# Will move gradually so it will look like a person
def naturalmove(final_dest,parts = 100):
    current = pyautogui.position()
    for things in getgeomPoints(current,final_dest+(random.uniform(0,10),random.uniform(0,10)),parts):
        pyautogui.moveTo(int(things[0]),int(things[1]))
        sleep(0.0000001)

    
#=============
#Move files from one location to another
def movefiles(current, final):
    shutil.move(f"{current}", f"{final}/{current}")
    
#==============
#GUI for finding folder
def addressfinder():
    root = tkinter.Tk()
    root.withdraw() #use to hide tkinter window

    currdir = os.getcwd()
    tempdir = filedialog.askdirectory(parent=root, initialdir=currdir, title='Please select a directory')
    return tempdir
#=============

#crop stuff
def displayImage(screen, px, topleft, prior):
    # ensure that the rect always has positive width, height
    x, y = topleft
    width =  pygame.mouse.get_pos()[0] - topleft[0]
    height = pygame.mouse.get_pos()[1] - topleft[1]
    if width < 0:
        x += width
        width = abs(width)
    if height < 0:
        y += height
        height = abs(height)

    # eliminate redundant drawing cycles (when mouse isn't moving)
    current = x, y, width, height
    if not (width and height):
        return current
    if current == prior:
        return current

    # draw transparent box and blit it onto canvas
    screen.blit(px, px.get_rect())
    im = pygame.Surface((width, height))
    im.fill((128, 128, 128))
    pygame.draw.rect(im, (32, 32, 32), im.get_rect(), 1)
    im.set_alpha(128)
    screen.blit(im, (x, y))
    pygame.display.flip()

    # return current box extents
    return (x, y, width, height)
def setup(path):
    px = pygame.image.load(path)
    screen = pygame.display.set_mode( px.get_rect()[2:] )
    screen.blit(px, px.get_rect())
    pygame.display.flip()
    return screen, px

def mainLoop(screen, px):
    topleft = bottomright = prior = None
    n=0
    while n!=1:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                if not topleft:
                    topleft = event.pos
                else:
                    bottomright = event.pos
                    n=1
        if topleft:
            prior = displayImage(screen, px, topleft, prior)
    return ( topleft + bottomright )


#================
# User will determine which files to select
def filefinder(text):
    print(text)
    sleep(1)
    root = tkinter.Tk()
    root.withdraw() #use to hide tkinter window

    root = tk.Tk()
    root.title('Tkinter Open File Dialog')
    root.resizable(False, False)
    root.geometry('300x150')
    filetypes = (
        ('pickle files', '*.pkl'),
        ('All files', '*.*')
    )
    filenames = fd.askopenfilenames(
        title='Open files',
        initialdir='/',
        filetypes=filetypes)
    return filenames
#=================
# User selects where they have saved their files
def retreaveinfo():
    print('please show where you have saved the files')
    sleep(1)
    directory = addressfinder()
    os.chdir(directory)
    pickels = glob.glob(f"{directory}\*.pkl", recursive = True)
    if f'{directory}\\choices.pkl' in pickels:
        open_file = open(f'{directory}\\choices.pkl', "rb")
        choices = pickle.load(open_file)
        open_file.close()
        choices = [f'{directory}\\{_}'for _ in choices]
    else:
        choices_address = filefinder('please choose your choices and win lose setuations')
    if f'{directory}\\coordinates.pkl' in pickels:
        open_file = open(f'{directory}\\coordinates.pkl', "rb")
        open_file.close()
    else:
        coordinates_address = filefinder('please choose your coordinates files')
        open_file = open(coordinates_address, "rb")
        coordinates = pickle.load(open_file)
        open_file.close()
    types = ('*.png', '*.jpg') # the tuple of file types
    pictures = []
    for files in types:
        pictures.extend(glob.glob(f'{directory}/{files}.png', recursive = True))
    pictures = [_.split('.')[0] for _ in pictures]
    if f'{directory}\\environment' not in pictures:
        environment = filefinder('please choose your environment file')
    return choices
#===============
# Plays random for a specific number of iterations
def randomplay(iter = 10):
    results = list()
    i = 0
    while i<iter:
        random_index = random.randint(0,1)
        selected_choice = choices[0]
        print(selected_choice)
        coor_choice = whereis(f'{selected_choice}.png')
        naturalmove((int(coor_choice[0]),int(coor_choice[1])))
        click()
        win = whereis(f'win.png')
        lose = (whereis(f'lose.png'))
        if type(whereis(f'win.png')) ==tuple:
            print(f'in this try, we went for {selected_choice} and won!')
            results.append('win')
            i+=1
        elif type(whereis(f'lose.png')) == tuple:
            print(f'in this try, we went for {selected_choice} and lost :((')
            results.append('lose')
            i+=1
        else:
            print('something is wrong. Ignore this iteration')
            print(win,lose)
#===============
# Deep Reinforcement Learning
def play_game(action):
    coor_choice = whereis(f'{action}.png')
    naturalmove((int(coor_choice[0]),int(coor_choice[1])))
    click()
    win = whereis(f'win.png')
    lose = (whereis(f'lose.png'))
    if type(whereis(f'win.png')) ==tuple:
        print(f'Match')
        results =  1
    elif type(whereis(f'lose.png')) == tuple:
        print(f'Wrong')
        results = -1   
    else:
        results = play_game(action)
    return results
    
class DQN:
    def __init__(self,choices):
        self.memory  = deque(maxlen=200)
        self.choices = choices
        self.gamma = 0.85
        self.epsilon = 1
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.99
        self.learning_rate = 0.005
        self.tau = .125

        self.model        = self.create_model()
        self.target_model = self.create_model()

    def create_model(self):
        model   = Sequential()
        state_shape  = 1
        model.add(Dense(2, input_dim=1, activation="relu",use_bias = False,kernel_initializer="zeros"))
        model.add(Dense(2,use_bias=False))
        model.compile(loss="mean_squared_error",
            optimizer=Adam(lr=self.learning_rate))
        return model

    def act(self):
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon)
        if np.random.random() < self.epsilon:
            return np.random.random()<0.5 *0 + np.random.random()>0.5 *1  
        print((self.model.predict([1])))
        return np.argmax(self.model.predict([1])[0])

    def remember(self, action, reward):
        self.memory.append([action, reward])

    def replay(self):
        batch_size = 4
        if len(self.memory) < batch_size: 
            return

        samples = random.sample(self.memory, batch_size)
        for sample in samples:
            action, reward = sample
            target = self.target_model.predict([1])
            target[0][action] = reward
            self.model.fit(np.array([1]),target, epochs=1, verbose=0)

    def target_train(self):
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = weights[i] * self.tau + target_weights[i] * (1 - self.tau)
        self.target_model.set_weights(target_weights)

    def save_model(self, fn):
        self.model.save(fn)


