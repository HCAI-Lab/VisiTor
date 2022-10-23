#!/usr/bin/env python
# coding: utf-8

# In[1]:


from Utils import *


# In[ ]:


def folderretreave(address):
    pickels = glob.glob(f"{address}\*.pkl", recursive = True)
    print(pickels)
    if f'{address}\choices.pkl' in pickels:
        open_file = open(f'{address}\choices.pkl', "rb")
        choices = pickle.load(open_file)
        print('choices retreaved')
        open_file.close()
    else:
        choices_address = filefinder('please choose your choices and win lose setuations')
    if f'{address}\coordinates.pkl' in pickels:
        open_file = open(f'{address}\coordinates.pkl', "rb")
        coordinates = pickle.load(open_file)
        print('coordinates retreaved')
        open_file.close()
    else:
        coordinates_address = filefinder('please choose your coordinates files')
        open_file = open(coordinates_address, "rb")
        coordinates = pickle.load(open_file)
        open_file.close()   
    types = ('*.png', '*.jpg') # the tuple of file types
    pictures = []
    for files in types:
        pictures.extend(glob.glob(files))
    print(pictures)
    pictures = [_.split('.')[0] for _ in pictures]
    if 'environment' not in pictures:
        environment = filefinder('please choose your environment file')
    return choices,coordinates


# In[5]:


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lets Play HeadsNTails!")
    parser.add_argument('folder', metavar='c', type=str,help='address of the data needed')
    parser.add_argument('action',metavar = 'c',type=str,help = 'What do you play?')
    args = parser.parse_args()
    os.chdir(args.folder)
    if args.folder is None:
        choices,coordinates,environment = retreaveinfo()
    else:
        choices,coordinates = folderretreave(args.folder)
    result = play_game(args.action)


# In[ ]:




