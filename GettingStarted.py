from Utils import *
if __name__== "__main__":
# gets the environment of the game:
    pygame.init()
    screenshot = ImageGrab.grab()
    screenshot.save('screen.png', 'PNG')  # Equivalent to `screenshot.save(filepath, format='PNG')`
    input_loc = 'screen.png'
    output_loc = 'environment.png'
    print("please determine your environment")
    sleep(1.5)
    screen, px = setup(input_loc)
    left, upper, right, lower = mainLoop(screen, px)
    # ensure output rect always has positive width, height
    if right < left:
        left, right = right, left
    if lower < upper:
        lower, upper = upper, lower
    im = PIL.Image.open(input_loc)
    im = im.crop((left, upper, right, lower))
    pygame.display.quit()
    im.save(output_loc)
    env_top_point = (upper, left)
    # to get choices:
    choices = list()
    env_top_point = list()
    query = 'empty'
    input_loc = 'environment.png'
    while query != 'done':
        if len(choices)==0:
            print("insert your visual modules")
        else:
            print("Your current modules are",choices, """\nplease crop your other modules if you have more. If not write "done" """ )
        query = input()
        if query =="done":
            query_goal = 'empty'
            while query_goal != "done":
                query_goal = input(f'Insert your Feedback modules!, if you are done, type done')
                if query_goal != 'done':
                    input('let me know when you are ready by pressing enter')
                    screenshot = ImageGrab.grab()
                    screenshot.save('screen.png', 'PNG')  # Equivalent to `screenshot.save(filepath, format='PNG')`
                    input_loc = 'screen.png'
                    choices.append(f'{query_goal}')
                    output_loc = f'{query_goal}.png'
                    screen, px = setup(input_loc)
                    left, upper, right, lower = mainLoop(screen, px)

                    # ensure output rect always has positive width, height
                    if right < left:
                        left, right = right, left
                    if lower < upper:
                        lower, upper = upper, lower
                    im = PIL.Image.open(input_loc)
                    im = im.crop(( left, upper, right, lower))
                    pygame.display.quit()
                    im.save(output_loc)
                    env_top_point.append((int((upper+lower)/2),int((left+right)/2)))
                else:
                    ans =input("do you want to save the data?[Y/N]")
                    if ans.lower()=='y':
                        print('please choose where you want to save your stuff')
                        sleep(2)
                        directory = addressfinder()
                        movefiles('environment.png', directory)
                        for files in choices:
                            movefiles(f"{files}.png", directory)
                        os.chdir(f'{directory}')
                        with open("choices.pkl", "wb") as fp:   #Pickling
                            pickle.dump(choices, fp)
                        with open("coordinates.pkl","wb") as fp:
                            pickle.dump(env_top_point,fp)
                        print("done!")
                    else:
                        for files in choices:
                            os.remove(f"{files}.png")
                    break
        else:
            print("please determine the parts you want to consider for this choice")
            sleep(2)
            choices.append(query)
            output_loc = f'{query}.png'
            screen, px = setup(input_loc)
            left, upper, right, lower = mainLoop(screen, px)

            # ensure output rect always has positive width, height
            if right < left:
                left, right = right, left
            if lower < upper:
                lower, upper = upper, lower
            im = PIL.Image.open(input_loc)
            im = im.crop(( left, upper, right, lower))
            pygame.display.quit()
            im.save(output_loc)
            env_top_point.append((int((upper+lower)/2),int((left+right)/2)))