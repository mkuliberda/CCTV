import sys
import termios
import tty


break_now = False

def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return ch

def waitForKeyPress():

    global break_now

    while True:
        ch = getch()

        if ch == 'q':
                break_now = True
                break
            
def run():
    print("Running.. Hit Ctrl-D to exit")
    while True: 
        try:
            n = input()    
        except EOFError as e:
            break

