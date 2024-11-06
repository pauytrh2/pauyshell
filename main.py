import os
import ctypes
import sys
import curses
import subprocess

platform = os.name

def fix_technical_stuff():
    def is_admin():
        if platform == "nt":
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False
        else:
            return os.geteuid() == 0

    if not is_admin():
        print("This script requires admin privileges. Please run it as an administrator.")
        if platform == "nt":
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        else:
            print("Please run this script with 'sudo'.")
        sys.exit()

def text_editor(stdscr, filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            content = f.readlines()
    else:
        content = ['']

    cursor_x = 0
    cursor_y = 0
    modified = False

    while True:
        stdscr.clear()

        for i, line in enumerate(content):
            stdscr.addstr(i, 0, "{:4d} {}".format(i + 1, line), curses.A_NORMAL)

        stdscr.addstr(curses.LINES - 2, 0, "-" * (curses.COLS - 1))
        stdscr.addstr(curses.LINES - 1, 0, f"Ctrl+X to exit, Ctrl+O to save. Line: {cursor_y + 1}, Col: {cursor_x + 1}")

        stdscr.move(cursor_y, cursor_x + 5)

        key = stdscr.getch()

        if key == curses.KEY_BACKSPACE or key == 127:
            if cursor_x > 0:
                content[cursor_y] = content[cursor_y][:cursor_x - 1] + content[cursor_y][cursor_x:]
                cursor_x -= 1
                modified = True
        elif key == curses.KEY_LEFT:
            if cursor_x > 0:
                cursor_x -= 1
            elif cursor_y > 0:
                cursor_y -= 1
                cursor_x = len(content[cursor_y])
        elif key == curses.KEY_RIGHT:
            if cursor_x < len(content[cursor_y]):
                cursor_x += 1
            elif cursor_y < len(content) - 1:
                cursor_y += 1
                cursor_x = 0
        elif key == curses.KEY_UP:
            if cursor_y > 0:
                cursor_y -= 1
                cursor_x = min(cursor_x, len(content[cursor_y]))
        elif key == curses.KEY_DOWN:
            if cursor_y < len(content) - 1:
                cursor_y += 1
                cursor_x = min(cursor_x, len(content[cursor_y]))
        elif key == 10:
            content.insert(cursor_y + 1, content[cursor_y][cursor_x:] + '\n')
            content[cursor_y] = content[cursor_y][:cursor_x] + '\n'
            cursor_y += 1
            cursor_x = 0
            modified = True
        elif key == 24:
            if modified:
                stdscr.addstr(curses.LINES - 1, 0, "Save modified buffer? (y/n) ")
                stdscr.refresh()
                save_key = stdscr.getch()
                if save_key == ord('y'):
                    with open(filename, 'w') as f:
                        f.writelines(content)
            break
        elif key == 15:
            with open(filename, 'w') as f:
                f.writelines(content)
            modified = False
            stdscr.addstr(curses.LINES - 1, 0, "File saved. Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()
        else:
            if len(content) == 0 or cursor_y == len(content):
                content.append('')
            content[cursor_y] = content[cursor_y][:cursor_x] + chr(key) + content[cursor_y][cursor_x:]
            cursor_x += 1
            modified = True

if platform == "nt":
    os.system("cls")
else:
    os.system("clear")

while True:
    command = input(f"Pauyshell at {os.getcwd()} >>  ").strip()
    
    if command:
        match command.split()[0]:
            case "h":
                print("Available commands:")
                print("- c: (clear) Clear the terminal")
                print("- s [message]: (say) Print the specified message")
                print("- x: (exit) Exit the shell")
                print("- f: (files) List files and directories")
                print("- mv [directory]: (move) Change the current directory")
                print("- md [directory]: (makedir) Create a new directory")
                print("- rd [directory]: (removedir) Remove an empty directory")
                print("- rm [file]: (remove) Delete a specified file")
                print("- d [file]: (display) Display the contents of a specified file")
                print("- m [file]: (make) Create a new empty file or update timestamp")
                print("- ren [old_name] [new_name]: (rename) Rename a specified file or directory")
                print("- e [file]: (edit) Edit a specified file")
                print("- var [var_name] [var_val]: (set variable) set an enviorment variable")
                print("- env [var_name]: (show variable) show the specified enviorment variable")
                print("- py [file]: (python) Run a specified Python file or enter Python interactive shell")
            case "c":
                os.system("cls" if platform == "nt" else "clear")
            case "s":
                print(" ".join(command.split()[1:]))
            case "x":
                sys.exit()
            case "whereami":
                print(os.getcwd())
            case "f":
                print("\n".join(os.listdir()))
            case "mv":
                directory = " ".join(command.split()[1:])
                if directory == "" or ".":
                    os.chdir("..")
                else:
                    try:
                        os.chdir(directory)
                    except Exception as e:
                        print(f"Error changing directory: {e}")
            case "md":
                try:
                    new_dir = " ".join(command.split()[1:])
                    os.makedirs(new_dir, exist_ok=True)
                    print(f"Created directory: {new_dir}")
                except Exception as e:
                    print(f"Error creating directory: {e}")
            case "rd":
                try:
                    dir_to_remove = " ".join(command.split()[1:])
                    os.rmdir(dir_to_remove)
                    print(f"Removed directory: {dir_to_remove}")
                except Exception as e:
                    print(f"Error removing directory: {e}")
            case "rm":
                try:
                    file_to_delete = " ".join(command.split()[1:])
                    os.remove(file_to_delete)
                    print(f"Deleted file: {file_to_delete}")
                except Exception as e:
                    print(f"Error deleting file: {e}")
            case "d":
                try:
                    file_to_read = " ".join(command.split()[1:])
                    with open(file_to_read, 'r') as f:
                        print(f.read())
                except Exception as e:
                    print(f"Error reading file: {e}")
            case "t":
                try:
                    file_to_touch = " ".join(command.split()[1:])
                    with open(file_to_touch, 'a'):
                        os.utime(file_to_touch, None)
                    print(f"Updated timestamp for file: {file_to_touch}")
                except Exception as e:
                    print(f"Error creating/updating file: {e}")
            case "ren":
                try:
                    old_name, new_name = command.split()[1:3]
                    os.rename(old_name, new_name)
                    print(f"Renamed {old_name} to {new_name}")
                except Exception as e:
                    print(f"Error renaming file: {e}")
            case "e":
                filename = " ".join(command.split()[1:])
                if os.path.exists(filename) or not filename:
                    curses.wrapper(text_editor, filename)
                else:
                    print(f"File {filename} does not exist.")
            case "py":
                if len(command.split()) == 1:
                    subprocess.run([sys.executable])
                else:
                    filename = " ".join(command.split()[1:])
                    if os.path.exists(filename) and filename.endswith(".py"):
                        subprocess.run([sys.executable, filename])
                    else:
                        print("Error: Please specify a valid Python file.")
            case "var":
                parts = command.split()
                if len(parts) == 2:
                    var_name = parts[1]
                    print(os.environ.get(var_name, "Variable not set."))
                elif len(parts) == 3:
                    var_name, var_val = parts[1], parts[2]
                    os.environ[var_name] = var_val
                    print(f"Set environment variable: {var_name} = {var_val}")
                else:
                    print("Usage: var [var_name] [var_val] to set, or var [var_name] to show")
            case "stfu":
                print("no u")
            case _:
                print(f"Unknown command: {command}, type 'h' for help")