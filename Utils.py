
import sys #Read arguements
import pyautogui #Finds Patterns, click and keyboard stuff
from time import sleep # To simulate pause
import numpy as np  # Matrix stuff
import os # For moving between folders and stuff
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import shutil #Moving files
import pickle #Saving files
from PIL import Image
from tkinter import *# For GUI i saving files
from PIL import ImageGrab,ImageTk
import PIL
import pygame #Gets mouse position and stuff
from tkinter import filedialog # GUI stuff
import glob #finds specific types of files
import tkinter as tk
from tkinter import filedialog as fd
import random
import win32gui
import win32con
from TemplateMatching import *

width = 1920 #self.winfo_screenwidth()
height = 1080 #self.winfo_screenheight()

#To click through the tkinter

def setClickthrough(hwnd):
    try:
        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        styles = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
        win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)
    except Exception as e:
        print(e)
root = Tk()
root.geometry('%dx%d' % (width, height))



# Create an object of tkinter ImageTk
img = PIL.Image.open("JSegManEye.jpg")
resize_image = img.resize((50, 50))

img = ImageTk.PhotoImage(resize_image)

root.title("Applepie")
root.attributes('-transparentcolor', 'white', '-topmost', 1)
root.config(bg='white')
root.attributes("-alpha", 0.5)
root.wm_attributes("-topmost", 1)
global bg

bg = Canvas(root, width=width, height=height, bg='white')

setClickthrough(bg.winfo_id())
bg = Label(root, image = img)

bg.pack()
root.overrideredirect(True)



def create_circle(x, y, r, canvasName):  # center coordinates, radius
   x0 = x - r
   y0 = y - r
   x1 = x + r
   y1 = y + r
   return canvasName.create_oval(x0, y0, x1, y1,fill="blue")


def naturaleyemove(final_dest,parts = 100):

    final_dest = (int(final_dest[0]),int(final_dest[1]))
    current = (int(bg.winfo_rootx()),int(bg.winfo_rooty()))
    for things in getgeomPoints(current,final_dest+(random.uniform(0,10),random.uniform(0,10)),parts):
        if things == current:
            continue
        else:
            if np.abs(current[0]-int(things[0]))+np.abs(current[1]-int(things[1]))>10:
                bg.place(x=int(things[0]),y=int(things[1]))
                root.update()
                current = things
                sleep(0.01)
    bg.place(x=int(things[0]), y=int(things[1]))

def keypress(key, time = 0.1):
    # presses the key
    key = key[0]
    pyautogui.keyDown(key)
    # waits five seconds before releasing the key
    sleep(time)
    # releases the key
    pyautogui.keyUp(key)


# Click at a specific location of the screen
def click():
#If you want mouse down and up to take more time
    # pyautogui.mouseDown()
    # sleep(0.1)
    # pyautogui.mouseUp()
# If you want just a click:
    pyautogui.click()
    root.update()
# finds the location of a pattern works better than opencv
def locate_pic(filename):
    pic=None
    while pic is None:
        root.update_idletasks()
        conf = .8
        while conf>0.5:
            try:
                pic = pyautogui.locateOnScreen(filename,confidence=conf)
                break
            except:
                conf*=0.9
        return pic
# finding the location of a pattern using opencv and rescaling
def locate_pic_CV(filename):
    pic = matching(filename)
    return pic
#Finds the location of a file in a directory and adds the extention to it
def find_file(address,filename):
    for ext in ['png','jpg']:
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
        naturaleyemove((x,y))
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
#For a more natural movement we need to break the path geometrically
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
# Will move gradually so it will look like a person

def naturalmove(final_dest,parts = 100):
    current = pyautogui.position()
    for things in getgeomPoints(current,final_dest+(random.uniform(0,10),random.uniform(0,10)),parts):
        if current == things:
            continue
        elif np.abs(current[0]-things[0])+np.abs(current[1]-things[1])>15:
            pyautogui.moveTo(int(things[0]),int(things[1]))
            sleep(0.0000001)
            current = things
    pyautogui.moveTo(int(things[0]) - 5, int(things[1]) - 5)



    
#=============
#Move files from one location to another
def movefiles(current, final):
    shutil.move(f"{current}", f"{final}/{current}")
    
#==============
#GUI for finding folder
def addressfinder():
    root = Tk()
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
    #print(text)
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
