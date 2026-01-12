#!/usr/bin/env python3
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import VERSION, APP_NAME

def main():
    print(f"{APP_NAME} v{VERSION}")
    print("Starting...")
    
    try:
        from ui.terminal import run
        run()
    except KeyboardInterrupt:
        print("\nBye!")
    except Exception as ex:
        # TODO: add proper logging later
        print(f"Something went wrong: {ex}")
        import traceback
        traceback.print_exc()
        input("Press Enter...")

if __name__ == "__main__":
    main()
