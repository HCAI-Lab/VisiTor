import os
import shutil
import pickle
import random
import sys
import subprocess
import ctypes
from ctypes import wintypes
from time import sleep
from typing import Tuple, List, Optional, Union

def auto_install(module_name, package_name=None):
    if package_name is None:
        package_name = module_name
    try:
        return __import__(module_name)
    except ImportError:
        print(f"Module '{module_name}' not found. Attempting to install: {package_name}")
        try:
            # User specifically asked for "uv pip install"
            subprocess.check_call(["uv", "pip", "install", package_name])
        except Exception:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            except Exception as e:
                print(f"Failed to install package: {package_name}. Error: {e}")
                raise e
        return __import__(module_name)

np = auto_install("numpy")
pyautogui = auto_install("pyautogui")
win32gui = auto_install("win32gui", "pywin32")
win32con = auto_install("win32con", "pywin32")
win32api = auto_install("win32api", "pywin32")
PIL = auto_install("PIL", "Pillow")
from PIL import Image, ImageTk, ImageGrab
tk = auto_install("tkinter") # Standard but sometimes needs install on linux/mac; simplified here
from tkinter import filedialog
cv2 = auto_install("cv2", "opencv-python")
glob = auto_install("glob")
torch = auto_install("torch")
torchvision = auto_install("torchvision")
from torchvision import models, transforms
from torchvision.models import ResNet50_Weights
pygame = auto_install("pygame")

# Constants
WIDTH = 1920
HEIGHT = 1080
IMAGE_PATH_CONFIG = 'image_path_config.pkl'

# Win32 constants for click-through window proc override.
GWL_WNDPROC = -4
WM_NCHITTEST = 0x0084
HTTRANSPARENT = -1

# Pointer-sized Win32 aliases for safe 32/64-bit callback marshalling.
LONG_PTR = ctypes.c_ssize_t
UINT_PTR = ctypes.c_size_t
LRESULT = LONG_PTR


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
        self.icon_w = 50
        self.icon_h = 50
        self._old_wndproc = None
        self._wndproc_ref = None
        self._hwnd = None
        self._screen = None
        self._sprite = None
        self._setup_overlay()

    def _default_eye_image_path(self) -> str:
        return os.path.join(os.path.dirname(__file__), "eye.png")

    def _resolve_eye_image_path(self) -> str:
        image_path = self.load_image_path()
        if image_path and os.path.isfile(image_path):
            return image_path

        default_path = self._default_eye_image_path()
        if os.path.isfile(default_path):
            self.save_image_path(default_path)
            return default_path

        # Last resort fallback to file dialog if no default image exists.
        return self.prompt_for_image()

    def _setup_overlay(self):
        image_path = self._resolve_eye_image_path()

        pygame.init()
        self._screen = pygame.display.set_mode((self.icon_w, self.icon_h), pygame.NOFRAME)
        pygame.display.set_caption("VisiTorEye")

        raw_img = pygame.image.load(image_path).convert_alpha()
        self._sprite = pygame.transform.smoothscale(raw_img, (self.icon_w, self.icon_h))
        self._screen.fill((0, 0, 0))
        self._screen.blit(self._sprite, (0, 0))
        pygame.display.update()

        wm_info = pygame.display.get_wm_info()
        self._hwnd = wm_info.get("window")
        if not self._hwnd:
            raise RuntimeError("Failed to obtain window handle for eye overlay")

        self.setClickthrough(self._hwnd)
        self.install_hit_test_transparent(self._hwnd)
        win32gui.SetWindowPos(
            self._hwnd,
            win32con.HWND_TOPMOST,
            0,
            0,
            0,
            0,
            win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW,
        )

    @staticmethod
    def setClickthrough(hwnd):
        try:
            styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            styles = (styles |
                      win32con.WS_EX_LAYERED |
                      win32con.WS_EX_TRANSPARENT |
                      win32con.WS_EX_NOACTIVATE |
                      win32con.WS_EX_TOOLWINDOW)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
            win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)
        except Exception as e:
            print(f"Error in setClickthrough: {e}")

    def install_hit_test_transparent(self, hwnd):
        """Subclass the overlay window and return HTTRANSPARENT on hit-test.
        This guarantees clicks pass through to underlying windows.
        """
        try:
            user32 = ctypes.windll.user32
            user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
            user32.GetWindowLongPtrW.restype = LONG_PTR
            user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, LONG_PTR]
            user32.SetWindowLongPtrW.restype = LONG_PTR
            user32.CallWindowProcW.argtypes = [LONG_PTR, wintypes.HWND, wintypes.UINT, UINT_PTR, LONG_PTR]
            user32.CallWindowProcW.restype = LRESULT

            old_wndproc = user32.GetWindowLongPtrW(hwnd, GWL_WNDPROC)

            WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, UINT_PTR, LONG_PTR)

            def _proc(hWnd, msg, wParam, lParam):
                if msg == WM_NCHITTEST:
                    return HTTRANSPARENT
                return user32.CallWindowProcW(old_wndproc, hWnd, msg, wParam, lParam)

            self._wndproc_ref = WNDPROC(_proc)
            new_wndproc_addr = ctypes.cast(self._wndproc_ref, ctypes.c_void_p).value
            user32.SetWindowLongPtrW(hwnd, GWL_WNDPROC, LONG_PTR(new_wndproc_addr))
            self._old_wndproc = old_wndproc
        except Exception as e:
            print(f"Error installing transparent hit-test WndProc: {e}")

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
        root = tk.Tk()
        root.withdraw()
        image_path = filedialog.askopenfilename(title='Select the JsegManEye image')
        root.destroy()
        if image_path:
            self.save_image_path(image_path)
            return image_path
        else:
            raise ValueError("No image selected. Exiting the application.")

    def naturaleyemove(self, final_dest: Tuple[int, int], parts: int = 100):
        final_dest = (int(final_dest[0]), int(final_dest[1]))
        rect = win32gui.GetWindowRect(self._hwnd)
        current = (int(rect[0]), int(rect[1]))

        for point in self.getgeomPoints(current, final_dest, parts):
            if point == current:
                continue
            if np.abs(current[0] - int(point[0])) + np.abs(current[1] - int(point[1])) > 10:
                win32gui.SetWindowPos(
                    self._hwnd,
                    win32con.HWND_TOPMOST,
                    int(point[0]),
                    int(point[1]),
                    0,
                    0,
                    win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW,
                )
                pygame.event.pump()
                current = point
                sleep(0.01)

        win32gui.SetWindowPos(
            self._hwnd,
            win32con.HWND_TOPMOST,
            int(final_dest[0]),
            int(final_dest[1]),
            0,
            0,
            win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW,
        )
        pygame.event.pump()

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