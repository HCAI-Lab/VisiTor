
# import pyiblRPS
import pyibl
import sys
sys.path.append('../')
import os
# os.chdir('../')
# print(os.getcwd())

from Utils import *
from HeadsNtail import *
a = pyibl.Agent("My Agent")
a.default_utility = 10.0
i = 0
def choose_and_respond():
    global i
    f = open('pyibl.txt','a')
    selected_choice = a.choose("Head", "tail")
    f.write(f'{selected_choice}\n')
    f.close()
    #Todo: Change it to your directory
    path = find_file('C:\\Users\\Amirreza\\EyesNHandsFiles', f'{selected_choice}')
    coor_choice = whereis(path)
    naturalmove((int(coor_choice[0]), int(coor_choice[1])))
    click()
    if i ==0:
        sleep(2)
        i+=1
    # sleep(5)
    #Todo: Change it to your directory
    path = find_file('C:\\Users\\Amirreza\\EyesNHandsFiles', 'win')
    sleep(0.5)
    win = whereis(path)
    #Todo: Change it to your directory
    path = find_file('C:\\Users\\Amirreza\\EyesNHandsFiles', 'lose')
    lose = (whereis(path))
    if type(win) == tuple:
        print(f'in this try, we went for {selected_choice} and won!')
        a.respond(6.0)

    elif type(lose) == tuple:
        print(f'in this try, we went for {selected_choice} and lost :((')
        a.respond(0)
    else:
        print('something is wrong. Ignore this iteration')
        print(win, lose)
    return selected_choice

if __name__ == "__main__":
    results = {"Head": 0, "tail": 0}
    for i in range(100):
        results[choose_and_respond()] += 1
    print(a.instances())
