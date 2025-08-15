import sys
import os

# Detect OS
is_windows = os.name == 'nt'

if is_windows:
    import msvcrt

    def get_key():
        key = msvcrt.getch()
        if key == b'\xe0' or key == b'\x00':  # Arrow key prefix
            key = msvcrt.getch()
            if key == b'H':
                return "UP"
            elif key == b'P':
                return "DOWN"
            elif key == b'M':
                return "RIGHT"
            elif key == b'K':
                return "LEFT"
        return key.decode('utf-8', errors='ignore')

else:
    import termios
    import tty

    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch1 = sys.stdin.read(1)
            if ch1 == '\x1b':  # Escape sequence
                ch2 = sys.stdin.read(1)
                ch3 = sys.stdin.read(1)
                if ch2 == '[':
                    if ch3 == 'A':
                        return "UP"
                    elif ch3 == 'B':
                        return "DOWN"
                    elif ch3 == 'C':
                        return "RIGHT"
                    elif ch3 == 'D':
                        return "LEFT"
            return ch1
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# Main loop
print("Press arrow keys (Ctrl+C to exit):")
while True:
    key = get_key()
    if key in ("UP", "DOWN", "LEFT", "RIGHT"):
        print(f"{key} arrow pressed")
    else:
        break
