import traceback
import sys
from window import Window

def main():
    print("init window")
    # CONFIGURATION
    WIN_WIDTH = 1680
    WIN_HEIGHT = 1100
    WINDOW_TITLE = "GimbleFlightSim"
    PLANE_OBJ_PATH = "assets/lowpolyplane.obj"
    print("init window")
    # init window
    window = Window(
        width=WIN_WIDTH,
        height=WIN_HEIGHT,
        title=WINDOW_TITLE,
        model_path=PLANE_OBJ_PATH
    )
    print("run window")
    window.run()

if __name__ == "__main__":
    main()