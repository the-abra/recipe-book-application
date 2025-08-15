# utils/console_utils.py
import sys
import os
from typing import List, Callable, Any
from enum import Enum

# Import optional modules with fallbacks
try:
    import termios
    import tty
    import select
    HAS_TERMIOS = True
except ImportError:
    HAS_TERMIOS = False

try:
    if os.name == 'nt':
        import msvcrt
        HAS_MSVCRT = True
    else:
        HAS_MSVCRT = False
except ImportError:
    HAS_MSVCRT = False

class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

class ConsoleManager:
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def get_terminal_size():
        return os.get_terminal_size()
    
    @staticmethod
    def print_header(title: str, width: int = 80):
        print(f"{Color.CYAN}{Color.BOLD}")
        print("=" * width)
        print(f"{title:^{width}}")
        print("=" * width)
        print(f"{Color.RESET}")
    
    @staticmethod
    def print_success(message: str):
        print(f"{Color.GREEN}✅ {message}{Color.RESET}")
    
    @staticmethod
    def print_error(message: str):
        print(f"{Color.RED}❌ {message}{Color.RESET}")
    
    @staticmethod
    def print_warning(message: str):
        print(f"{Color.YELLOW}⚠️ {message}{Color.RESET}")
    
    @staticmethod
    def print_info(message: str):
        print(f"{Color.BLUE}ℹ️ {message}{Color.RESET}")

class KeyboardInput:
    @staticmethod
    def get_key():
        """Get a single keypress from stdin with cross-platform compatibility"""
        if os.name == 'nt':  # Windows
            try:
                import msvcrt
                key = msvcrt.getch()
                if key in (b'\xe0', b'\x00'):  # Arrow key prefix
                    key = msvcrt.getch()
                    arrow_keys = {b'H': 'UP', b'P': 'DOWN', b'K': 'LEFT', b'M': 'RIGHT'}
                    return arrow_keys.get(key, None)
                elif key == b'\r':
                    return 'ENTER'
                elif key == b'\x1b':
                    return 'ESC'
                return key.decode('utf-8', errors='ignore')
            except ImportError:
                # Fallback
                return input().strip()[:1] if input().strip() else 'ENTER'

        else:  # Unix/Linux/Mac (TTY)
            try:
                import termios
                import tty
                fd = sys.stdin.fileno()

                if not os.isatty(fd):
                    return 'FALLBACK'

                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    ch1 = sys.stdin.read(1)

                    if ch1 == '\x1b':  # Escape sequence
                        ch2 = sys.stdin.read(1)
                        ch3 = sys.stdin.read(1)
                        arrow_keys = {'A': 'UP', 'B': 'DOWN', 'C': 'RIGHT', 'D': 'LEFT'}
                        return arrow_keys.get(ch3, 'ESC')
                    elif ch1 in ('\n', '\r'):
                        return 'ENTER'
                    elif ch1 == '\x03':  # Ctrl+C
                        raise KeyboardInterrupt
                    elif ch1 == '\x04':  # Ctrl+D
                        return 'ESC'
                    elif ch1 == ' ':
                        return 'SPACE'
                    elif ch1 == '\t':
                        return 'TAB'
                    elif 32 <= ord(ch1) <= 126:
                        return ch1
                    else:
                        return None
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            except (ImportError, OSError, termios.error, IOError, ValueError):
                return 'FALLBACK'

class InteractiveMenu:
    def __init__(self, title: str, options: List[str], show_back: bool = True):
        self.title = title
        self.options = options.copy()
        if show_back:
            self.options.append("← Back")
        self.selected_index = 0
        self.use_arrows = self._test_arrow_support()
    
    def _test_arrow_support(self) -> bool:
        """Test if arrow key navigation is supported"""
        # More comprehensive testing for arrow key support
        try:
            if os.name == 'nt':
                import msvcrt
                return True
            else:
                # Check for all required modules and proper terminal
                import termios
                import tty
                import select
                
                # Must be running in a proper TTY
                if not (sys.stdin.isatty() and sys.stdout.isatty()):
                    return False
                
                # Test if we can actually get terminal attributes
                try:
                    fd = sys.stdin.fileno()
                    termios.tcgetattr(fd)
                    return True
                except (OSError, termios.error):
                    return False
                    
        except (ImportError, OSError, AttributeError):
            return False
    
    def display(self):
        ConsoleManager.clear_screen()
        ConsoleManager.print_header(self.title)
        print()
        
        if self.use_arrows:
            # Arrow key mode
            for i, option in enumerate(self.options):
                if i == self.selected_index:
                    print(f"{Color.CYAN}{Color.BOLD}► {option}{Color.RESET}")
                else:
                    print(f"  {option}")
            print(f"\n{Color.YELLOW}Use ↑↓ arrows to navigate, Enter to select, ESC to exit{Color.RESET}")
        else:
            # Number selection mode
            for i, option in enumerate(self.options):
                print(f"{Color.CYAN}{i + 1}.{Color.RESET} {option}")
            print(f"\n{Color.YELLOW}Enter number (1-{len(self.options)}) or 'q' to go back:{Color.RESET}")
    
    def run(self) -> int:
        if self.use_arrows:
            return self._run_arrow_mode()
        else:
            return self._run_number_mode()
    
    def _run_arrow_mode(self) -> int:
        """Arrow key navigation mode"""
        while True:
            try:
                self.display()
                key = KeyboardInput.get_key()
                
                # Handle the case where get_key returns None (timeout) or FALLBACK
                if key is None:
                    continue  # No key pressed, keep waiting
                elif key == 'FALLBACK':
                    # Arrow key detection failed, switch to number mode
                    ConsoleManager.print_warning("Arrow key detection failed, switching to number mode...")
                    input("Press Enter to continue...")
                    return self._run_number_mode()
                elif key == 'UP':
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif key == 'DOWN':
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif key == 'ENTER':
                    return self.selected_index
                elif key == 'ESC':
                    return -1
                elif key and key.isdigit():
                    # Allow number selection even in arrow mode
                    try:
                        num = int(key)
                        if 1 <= num <= len(self.options):
                            return num - 1
                    except ValueError:
                        pass
                # Ignore other keys and continue the loop
            except KeyboardInterrupt:
                return -1
            except Exception as e:
                # If arrow mode fails, fall back to number mode
                ConsoleManager.print_warning("Arrow key mode encountered an error, switching to number mode...")
                input("Press Enter to continue...")
                return self._run_number_mode()
    
    def _run_number_mode(self) -> int:
        """Number selection mode (fallback)"""
        while True:
            try:
                self.display()
                choice = input(f"{Color.BLUE}Your choice: {Color.RESET}").strip().lower()
                
                if choice in ['q', 'quit', 'back', 'exit']:
                    return -1
                
                try:
                    num = int(choice)
                    if 1 <= num <= len(self.options):
                        return num - 1
                    else:
                        ConsoleManager.print_error(f"Please enter a number between 1 and {len(self.options)}")
                        input("Press Enter to continue...")
                except ValueError:
                    ConsoleManager.print_error("Please enter a valid number or 'q' to go back")
                    input("Press Enter to continue...")
            except (EOFError, KeyboardInterrupt):
                return -1

class FormField:
    def __init__(self, name: str, label: str, field_type: str = "text", 
                 required: bool = True, options: List[str] = None, 
                 validator: Callable = None):
        self.name = name
        self.label = label
        self.field_type = field_type  # text, number, select, multiline, boolean
        self.required = required
        self.options = options or []
        self.validator = validator
        self.value = None

class InteractiveForm:
    def __init__(self, title: str, fields: List[FormField]):
        self.title = title
        self.fields = fields
        self.current_field = 0
    
    def display_field(self, field: FormField):
        ConsoleManager.clear_screen()
        ConsoleManager.print_header(f"{self.title} - {field.label}")
        print()
        
        if field.field_type == "select":
            menu = InteractiveMenu(f"Select {field.label}", field.options, show_back=False)
            selected = menu.run()
            if selected >= 0:
                field.value = field.options[selected]
        elif field.field_type == "boolean":
            menu = InteractiveMenu(field.label, ["Yes", "No"], show_back=False)
            selected = menu.run()
            field.value = selected == 0
        elif field.field_type == "multiline":
            print(f"Enter {field.label} (press Ctrl+D when done):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                field.value = lines
        else:
            while True:
                current_value = field.value if field.value else ""
                print(f"Current value: {current_value}")
                print(f"Enter {field.label} (leave blank to keep current):")
                
                value = input().strip()
                if not value and field.value:
                    break
                elif not value and field.required:
                    ConsoleManager.print_error(f"{field.label} is required!")
                    input("Press Enter to continue...")
                    continue
                elif field.validator and not field.validator(value):
                    ConsoleManager.print_error("Invalid input format!")
                    input("Press Enter to continue...")
                    continue
                else:
                    if field.field_type == "number":
                        try:
                            field.value = float(value) if '.' in value else int(value)
                        except ValueError:
                            ConsoleManager.print_error("Please enter a valid number!")
                            input("Press Enter to continue...")
                            continue
                    else:
                        field.value = value
                    break
    
    def run(self) -> dict:
        for field in self.fields:
            self.display_field(field)
        
        return {field.name: field.value for field in self.fields}