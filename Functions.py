import os
import shutil
import pickle
import random
from time import sleep
from typing import Tuple, List, Optional, Union

import numpy as np
import pyautogui
import win32gui
import win32con
import win32api
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
import cv2
import glob
import torch
import torchvision.models as models
from torchvision.models import ResNet50_Weights
import torchvision.transforms as transforms
import pygame
from PIL import ImageGrab, ImageTk
import PIL
# Constants
WIDTH = 1920
HEIGHT = 1080
IMAGE_PATH_CONFIG = 'image_path_config.pkl'


#Environment Setup functions
def movefiles(current, final):
    shutil.move(f"{current}", f"{final}/{current}")


def displayImage(screen, px, topleft, prior):
    # ensure that the rect always has positive width, height
    x, y = topleft
    width = pygame.mouse.get_pos()[0] - topleft[0]
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
    screen = pygame.display.set_mode(px.get_rect()[2:])
    screen.blit(px, px.get_rect())
    pygame.display.flip()
    return screen, px

def mainLoop(screen, px):
    topleft = bottomright = prior = None
    n = 0
    while n != 1:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                if not topleft:
                    topleft = event.pos
                else:
                    bottomright = event.pos
                    n = 1
        if topleft:
            prior = displayImage(screen, px, topleft, prior)
    return (topleft + bottomright)


# Now we define the classes and functions that will be used in the VisiTor2.0 script

class EyeTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_gui()

    def setup_gui(self):
        self.root.geometry(f'{WIDTH}x{HEIGHT}')
        self.root.title("Applepie")
        self.root.attributes('-transparentcolor', 'white', '-topmost', 1)
        self.root.config(bg='white')
        self.root.attributes("-alpha", 0.5)
        self.root.wm_attributes("-topmost", 1)
        self.root.overrideredirect(True)

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg='white')
        self.setClickthrough(self.canvas.winfo_id())

        image_path = self.load_image_path()
        if image_path is None:
            image_path = self.prompt_for_image()

        img = Image.open(image_path)
        resize_image = img.resize((50, 50))
        self.img = ImageTk.PhotoImage(resize_image)

        self.bg_label = tk.Label(self.root, image=self.img)
        self.bg_label.pack()

    @staticmethod
    def setClickthrough(hwnd):
        try:
            styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            styles = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
            win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)
        except Exception as e:
            print(f"Error in setClickthrough: {e}")

    @staticmethod
    def save_image_path(image_path: str):
        with open(IMAGE_PATH_CONFIG, 'wb') as f:
            pickle.dump(image_path, f)

    @staticmethod
    def load_image_path() -> Optional[str]:
        try:
            with open(IMAGE_PATH_CONFIG, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None

    def prompt_for_image(self) -> str:
        print('Select the JsegManEye image')
        self.root.withdraw()
        image_path = filedialog.askopenfilename(title='Select the JsegManEye image')
        if image_path:
            self.save_image_path(image_path)
            return image_path
        else:
            raise ValueError("No image selected. Exiting the application.")

    def naturaleyemove(self, final_dest: Tuple[int, int], parts: int = 100):
        final_dest = (int(final_dest[0]), int(final_dest[1]))
        current = (int(self.bg_label.winfo_rootx()), int(self.bg_label.winfo_rooty()))

        for point in self.getgeomPoints(current, final_dest, parts):
            if point == current:
                continue
            if np.abs(current[0] - int(point[0])) + np.abs(current[1] - int(point[1])) > 10:
                self.bg_label.place(x=int(point[0]), y=int(point[1]))
                self.root.update()
                current = point
                sleep(0.01)

        self.bg_label.place(x=int(point[0]), y=int(point[1]))

    @staticmethod
    def getgeomPoints(p1: Tuple[float, float], p2: Tuple[float, float], parts: int) -> List[Tuple[float, float]]:
        if p1[0] == p2[0] or p1[1] == p2[1]:
            return [p1]

        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        x_space = np.geomspace(1, abs(dx), parts + 1) - 1
        y_space = np.geomspace(1, abs(dy), parts + 1) - 1

        if dx >= 0:
            x_coords = [-x + p2[0] for x in reversed(x_space)]
        else:
            x_coords = [x + p2[0] for x in reversed(x_space)]

        if dy >= 0:
            y_coords = [-y + p2[1] for y in reversed(y_space)]
        else:
            y_coords = [y + p2[1] for y in reversed(y_space)]

        return list(zip(x_coords, y_coords))


class VisionFunctions:
    @staticmethod
    def locate_pic(filename: str, confidence: float = 0.8) -> Optional[Tuple[int, int, int, int]]:
        while confidence > 0.5:
            try:
                return pyautogui.locateOnScreen(filename, confidence=confidence)
            except pyautogui.ImageNotFoundException:
                confidence *= 0.9
        return None

    @staticmethod
    def locate_pic_CV(filename: str) -> Optional[Tuple[int, int, int, int]]:
        screen = np.array(pyautogui.screenshot())
        template = cv2.imread(filename, 0)
        screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > 0.8:
            return (*max_loc, template.shape[1], template.shape[0])
        return None

    @classmethod
    def whereis(cls, path: str) -> Union[Tuple[float, float], str]:
        pic = cls.locate_pic(path)
        if pic is None:
            return "Pattern doesn't exist"
        x = pic[0] + pic[2] / 2
        y = pic[1] + pic[3] / 2
        return x, y

    @classmethod
    def whereis_top(cls, path: str) -> Union[Tuple[int, int], str]:
        pic = cls.locate_pic(path)
        if pic is None:
            return "Pattern doesn't exist"
        return pic[0], pic[1]

    @staticmethod
    def extract_features(image_path: str, model: torch.nn.Module, layer_name: str) -> np.ndarray:
        image = Image.open(image_path).convert('RGB')
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        input_tensor = preprocess(image)
        input_batch = input_tensor.unsqueeze(0)

        if torch.cuda.is_available():
            input_batch = input_batch.to('cuda')
            model = model.to('cuda')

        with torch.no_grad():
            features = None

            def hook(module, input, output):
                nonlocal features
                features = output.cpu().numpy()

            handle = model._modules[layer_name].register_forward_hook(hook)
            model(input_batch)
            handle.remove()

        return features

    @staticmethod
    def find_pattern_with_single_bbox(image1_path: str, image2_path: str, match_threshold: float = 0.7, ratio_threshold: float = 0.7) -> Tuple[int, Tuple[int, int, int, int]]:
        img1 = cv2.imread(image1_path)
        img2 = cv2.imread(image2_path)
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        sift = cv2.SIFT_create()
        kp1, des1 = sift.detectAndCompute(gray1, None)
        kp2, des2 = sift.detectAndCompute(gray2, None)

        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(des1, des2, k=2)

        good_matches = []
        for m, n in matches:
            if m.distance < ratio_threshold * n.distance and m.distance < match_threshold:
                good_matches.append(m)

        matched_kps = [kp1[m.queryIdx].pt for m in good_matches]

        if matched_kps:
            x_coords, y_coords = zip(*matched_kps)
            x1, y1 = int(min(x_coords)), int(min(y_coords))
            x2, y2 = int(max(x_coords)), int(max(y_coords))

            padding = 20
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(img1.shape[1], x2 + padding)
            y2 = min(img1.shape[0], y2 + padding)
        else:
            x1, y1, x2, y2 = 0, 0, 0, 0

        return len(good_matches), (x1, y1, x2, y2)

    @classmethod
    def Deep_Pattern_Matching(cls, path: str, template_path: str, match_threshold: float = 0.7, ratio_threshold: float = 0.7) -> Union[Tuple[float, float], str]:
        weights = ResNet50_Weights.IMAGENET1K_V1
        model = models.resnet50(weights=weights)
        model.eval()

        features1 = cls.extract_features(path, model, 'layer4')
        features2 = cls.extract_features(template_path, model, 'layer4')

        num_matches, bbox = cls.find_pattern_with_single_bbox(path, template_path, match_threshold, ratio_threshold)

        feature_similarity = np.sum(np.abs(features1 - features2))

        if num_matches > 0:
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2
            return center_x, center_y
        else:
            return "Pattern doesn't exist"


class MotorFunctions:
    @staticmethod
    def keypress(key: str, duration: float = 0.1):
        pyautogui.keyDown(key)
        sleep(duration)
        pyautogui.keyUp(key)

    @staticmethod
    def click():
        pyautogui.click()

    @staticmethod
    def longkeypress(key: str):
        pyautogui.keyDown(key)
        # Note: This will keep the key pressed until manually released

    @staticmethod
    def naturalmove(final_dest: Tuple[float, float], parts: int = 100):
        current = pyautogui.position()
        for point in EyeTracker.getgeomPoints(current, final_dest, parts):
            if current == point:
                continue
            if np.abs(current[0] - point[0]) + np.abs(current[1] - point[1]) > 15:
                pyautogui.moveTo(int(point[0]), int(point[1]))
                sleep(0.0000001)
                current = point
        pyautogui.moveTo(int(point[0]) - 5, int(point[1]) - 5)


class UtilityFunctions:
    @staticmethod
    def find_file(address: str, filename: str) -> str:
        for ext in ['png', 'jpg']:
            file_path = os.path.join(address, f"{filename}.{ext}")
            if os.path.exists(file_path):
                return file_path
        raise FileNotFoundError(f"File {filename} not found in {address}")

    @staticmethod
    def movefiles(current: str, final: str):
        shutil.move(current, os.path.join(final, os.path.basename(current)))

    @staticmethod
    def addressfinder() -> str:
        root = tk.Tk()
        root.withdraw()
        return filedialog.askdirectory(title='Please select a directory')

    @staticmethod
    def filefinder(text: str,
                   filetypes: Tuple[Tuple[str, str], ...] = (('pickle files', '*.pkl'), ('All files', '*.*'))) -> Tuple[
        str, ...]:
        root = tk.Tk()
        root.withdraw()
        return filedialog.askopenfilenames(title=f'Open files: {text}', initialdir='/', filetypes=filetypes)

    @classmethod
    def retreaveinfo(cls) -> List[str]:
        print('Please show where you have saved the files')
        sleep(1)
        directory = cls.addressfinder()
        os.chdir(directory)

        pickles = glob.glob(os.path.join(directory, "*.pkl"))
        choices_file = os.path.join(directory, 'choices.pkl')

        if choices_file in pickles:
            with open(choices_file, "rb") as f:
                choices = pickle.load(f)
            choices = [os.path.join(directory, choice) for choice in choices]
        else:
            choices = cls.filefinder('Please choose your choices and win-lose situations')

        coordinates_file = os.path.join(directory, 'coordinates.pkl')
        if coordinates_file in pickles:
            with open(coordinates_file, "rb") as f:
                coordinates = pickle.load(f)
        else:
            coordinates_address = cls.filefinder('Please choose your coordinates files')[0]
            with open(coordinates_address, "rb") as f:
                coordinates = pickle.load(f)

        pictures = []
        for ext in ['png', 'jpg']:
            pictures.extend(glob.glob(os.path.join(directory, f'*.{ext}')))
        pictures = [os.path.splitext(pic)[0] for pic in pictures]

        if os.path.join(directory, 'environment') not in pictures:
            environment = cls.filefinder('Please choose your environment file')

        return choices


# Create instances of each class for easy access to methods
eye_tracker = EyeTracker()
vision = VisionFunctions()
motor = MotorFunctions()
utility = UtilityFunctions()

# Make commonly used functions available at the module level
click = motor.click
keypress = motor.keypress
longkeypress = motor.longkeypress
whereis = vision.whereis
find_file = utility.find_file
addressfinder = utility.addressfinder
naturalmove = motor.naturalmove