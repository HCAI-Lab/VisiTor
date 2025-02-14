from Functions import *
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lets automatically find stuff!")
    parser.add_argument('Function', metavar='c', type=str, help='The activity you want to do')
    parser.add_argument('--Dir', metavar='c', type=str, help='The directory for the files that the function will need')
    parser.add_argument('--arg2', metavar='', type=str, nargs='+',
                        help='Any argument of the function. In case of writing coordinates, please put a space between x and y')
    args = parser.parse_args()

    if args.Function == 'click':
        click()

    elif args.Function == 'Keypress':
        if args.arg2 is None:
            args.arg2 = input('Please enter a key')
        while len(args.arg2) != 1:
            args.arg2 = input('Please enter a single key')
        keypress(args.arg2)

    elif args.Function == 'whatisonscreen':
        flag = False
        if args.arg2 is None:
            args.arg2 = input('Please enter Feedback visual modules separated by space').split()
        address = args.Dir
        for module in args.arg2:
            path = find_file(address, module)
            coor_choice = whereis(path)
            if isinstance(coor_choice, tuple):
                flag = True
                print(f'{module}')
        if not flag:
            print('crap')

    elif args.Function == 'movecursorto':
        if args.arg2 is None or len(args.arg2) != 2:
            args.arg2 = input('Please enter x and y coordinates separated by space').split()
            while len(args.arg2) != 2:
                args.arg2 = input('Please enter x and y coordinates separated by space').split()
        coor = (int(args.arg2[0]), int(args.arg2[1]))
        win32api.SetCursorPos(coor)

    elif args.Function == 'getMouseLocation':
        print(pyautogui.position())

    elif args.Function == 'whereis':
        address = args.Dir
        while args.arg2 is None:
            args.arg2 = input('Please enter the name of the file without extension').split()
        action = args.arg2[0]
        path = find_file(address, action)
        try:
            address = whereis(path)
            print(f"Pattern found at: {address}")
        except Exception as e:
            print(f"Error: {e}")

    elif args.Function == 'continuouspresskey':
        if args.arg2 is None:
            args.arg2 = input('Please enter a key')
        while len(args.arg2) != 1:
            args.arg2 = input('Please enter a single key')
        longkeypress(args.arg2)

    elif args.Function == "movecursortopattern":
        if args.Dir is None:
            args.Dir = addressfinder()
        while args.arg2 is None:
            args.arg2 = input('Please enter the name of the file without extension').split()
        address = args.Dir
        path = find_file(address, args.arg2[0].lower())

        coor_choice = whereis(path)
        if isinstance(coor_choice, tuple):
            naturalmove((int(coor_choice[0]), int(coor_choice[1])))
        else:
            print(f"Error: {coor_choice}")