from Utils import *
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lets automatically find stuff!")
    parser.add_argument('Function', metavar='c', type=str,help='The activity you want to do')
    parser.add_argument('--Dir', metavar= 'c', type=str,help ='The directory for the files that the function will need')
    parser.add_argument('--arg2',metavar = '',type=str,nargs = '+',help = 'Any argument of the function. In case of writing coordinates, please put a space between x and y')
    args = parser.parse_args()
    if args.Function == 'click':
        click()
    elif args.Function == 'Keypress':
        if args.arg2 == None:
            args.arg2 = input('Please enter a key')
            while len(args.arg2)!=1:
                args.arg2 = input('Please enter a single key')
            keypress(args.arg2)
        else:
            while len(args.arg2)!=1:
                args.arg2 = input('Please enter a single key')
            keypress(args.arg2)
    elif args.Function == 'whatisonscreen':
        flag =False
        if args.arg2 ==None:
            args.arg2 = input('Please enter enter Feedback visual modules seperated by space')
            args.arg2 = args.arg2.split()
        address = args.Dir
        for module in args.arg2:
            path = find_file(address, f'{module}')
            coor_choice = whereis(path)
            if type(coor_choice) ==tuple:
                flag =True
                print(f'{module}')
        if flag ==False:
            print('crap')
    elif args.Function == 'movecursorto':
        print(args.arg2)
        if args.arg2 == None:
            args.arg2 = input('Please enter x and y coordinates seperated by space')
            while len(args.arg2.split())!=2:
                args.arg2 = input('Please enter x and y coordinates seperated by space')
        else:
            while len(args.arg2)!=2:
                args.arg2 = input('Please enter x and y coordinates seperated by space')
        coor = (int(args.arg2[0]),int(args.arg2[1]))
        win32api.SetCursorPos(coor)
    elif args.Function == 'getMouseLocation':
        print(pyautogui.position())
    elif args.Function == 'whereis':
        while args.arg2 == None:
            args.arg2 = input('Please enter the name of the file without extention')
        address = None
        i = 0
        while address == None:
            if i == 0:
                action = args.arg2
                address = whereis(f'{action[0]}.png')
                i +=1
            else:
                input('file does not exist. Please try again')
        else:
            print(address)
    elif args.Function == 'continuouspresskey':
        if args.arg2 == None:
            args.arg2 = input('Please enter a key')
            while len(args.arg2)!=1:
                args.arg2 = input('Please enter a single key')

        else:
            while len(args.arg2)!=1:
                args.arg2 = input('Please enter a single key')
        longkeypress(args.arg2)
    elif args.Function == "movecursortopattern":
        if args.Dir is None:
            args.Dir = addressfinder()
        while args.arg2 is None:
            args.arg2 = input('Please enter the name of the file without extention')
        address = args.Dir
        i = 0
        path = find_file(address,f'{args.arg2[0].lower()}')
        from PIL import Image
        im = Image.open(path)

        coor_choice =whereis(path)
        naturalmove((int(coor_choice[0]),int(coor_choice[1])))
