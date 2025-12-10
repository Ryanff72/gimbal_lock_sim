import traceback
import sys
from window import Window

def main():
    print("init window")
    # CONFIGURATION
    WIN_WIDTH = 1280
    WIN_HEIGHT = 780
    WINDOW_TITLE = "GimbleFlightSim"
    PLANE_OBJ_PATH = "assets/rats.obj"
    PLANE_MTL_PATH = "assets/airplane.mtl"
    PLANE_MTL_PATH = "assets/airplane.mtl"
    # init window
    window = Window(
        width=WIN_WIDTH,
        height=WIN_HEIGHT,
        title=WINDOW_TITLE,
    )
    print("run window")
    window.run()

if __name__ == "__main__":
    main()