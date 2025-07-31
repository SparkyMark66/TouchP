#!/usr/bin/env python3
#
# touchp - v1.0
#
# A cross-platform command-line tool to 'touch' a file (update timestamps or create it)
# and then pop up a GUI to paste the clipboard contents into it.
#
# Dependencies:
#   - PyQt5: For clipboard access and GUI dialog.
#     Install with: pip install PyQt5
#   - python-dateutil: For robust date parsing for -d and -t flags.
#     Install with: pip install python-dateutil

import sys
import os
import argparse
import datetime
from dateutil.parser import parse as parse_date

try:
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QMessageBox
    from PyQt5.QtCore import Qt
except ImportError:
    print("Error: PyQt5 is not installed. Please install it using 'pip install PyQt5'", file=sys.stderr)
    sys.exit(1)

# --- Core 'touch' Logic ---

def update_timestamps(filepath, mtime=None, atime=None, no_create=False):
    """
    Updates the modification and/or access times of a file.
    Creates the file if it doesn't exist, unless no_create is True.

    Args:
        filepath (str): The path to the file.
        mtime (float, optional): The modification time timestamp. Defaults to now.
        atime (float, optional): The access time timestamp. Defaults to mtime.
        no_create (bool): If True, do not create the file if it doesn't exist.

    Returns:
        bool: True if a file was updated or created, False otherwise.
    """
    if not os.path.exists(filepath):
        if no_create:
            print(f"touchp: cannot touch '{filepath}': No such file or directory (and -c flag is set)")
            return False
        try:
            # Create the file by opening it in append mode
            with open(filepath, 'a'):
                pass
            print(f"touchp: created '{filepath}'")
        except IOError as e:
            print(f"touchp: cannot create '{filepath}': {e}", file=sys.stderr)
            return False

    # If no specific times are given, use the current time
    if mtime is None and atime is None:
        # os.utime with None uses current time, so this is explicit but clear
        times = None
    else:
        # Get current stats to fill in missing time
        stat = os.stat(filepath)
        current_atime = stat.st_atime
        current_mtime = stat.st_mtime

        # If only one time is specified, the other defaults to it.
        final_atime = atime if atime is not None else (mtime if mtime is not None else current_atime)
        final_mtime = mtime if mtime is not None else (atime if atime is not None else current_mtime)
        times = (final_atime, final_mtime)

    try:
        os.utime(filepath, times)
    except OSError as e:
        print(f"touchp: setting times for '{filepath}': {e}", file=sys.stderr)
        return False

    return True


# --- PyQt5 GUI Logic ---

class PasteDialog(QWidget):
    """
    A simple dialog window with a text editor and Save/Cancel buttons.
    """
    def __init__(self, filepaths, clipboard_text):
        super().__init__()
        self.filepaths = filepaths
        self.clipboard_text = clipboard_text
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f'Paste to {len(self.filepaths)} file(s) - touchp')
        self.setGeometry(300, 300, 500, 400) # x, y, width, height

        layout = QVBoxLayout()

        # Text Editor
        self.text_editor = QTextEdit(self)
        self.text_editor.setText(self.clipboard_text)
        self.text_editor.setPlaceholderText("Clipboard was empty. Paste your content here.")
        layout.addWidget(self.text_editor)

        # Buttons
        save_button = QPushButton('Save to File(s)', self)
        save_button.clicked.connect(self.save_content)
        save_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")


        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.close)
        cancel_button.setStyleSheet("background-color: #f44336; color: white; padding: 10px; border-radius: 5px;")


        layout.addWidget(save_button)
        layout.addWidget(cancel_button)

        self.setLayout(layout)
        self.show()
        # Bring window to front
        self.activateWindow()
        self.raise_()

    def save_content(self):
        """
        Writes the content of the text editor to the specified file(s).
        """
        content_to_save = self.text_editor.toPlainText()
        saved_files = []
        errors = []

        for fpath in self.filepaths:
            try:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content_to_save)
                saved_files.append(os.path.basename(fpath))
            except IOError as e:
                errors.append(f"Could not save to {fpath}: {e}")

        # Show confirmation message
        msg_box = QMessageBox()
        if saved_files:
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText(f"Content successfully saved to:\n" + "\n".join(saved_files))
        else:
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText("No files were saved.")

        if errors:
            msg_box.setDetailedText("\n".join(errors))

        msg_box.setWindowTitle("Save Status")
        msg_box.exec_()

        self.close()

# --- Main Execution ---

def main():
    """
    Parses arguments, performs the 'touch' operation, and launches the GUI.
    """
    parser = argparse.ArgumentParser(
        description="A 'touch' command replacement that allows pasting clipboard contents into the file via a GUI.",
        epilog="Example: touchp -m -r reference_file.txt new_file.txt"
    )
    parser.add_argument('file', nargs='+', help='One or more file paths to touch.')
    parser.add_argument('-a', action='store_true', help='change only the access time')
    parser.add_argument('-m', action='store_true', help='change only the modification time')
    parser.add_argument('-c', '--no-create', action='store_true', help="do not create any files")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--date', type=str, help='parse a string and use it instead of current time')
    group.add_argument('-r', '--reference', type=str, help='use this file\'s times instead of current time')
    group.add_argument('-t', type=str, help='use [[CC]YY]MMDDhhmm[.ss] instead of current time')

    args = parser.parse_args()

    atime_change = None
    mtime_change = None
    
    # Determine the timestamp to use
    if args.reference:
        if not os.path.exists(args.reference):
            print(f"touchp: failed to get attributes of '{args.reference}': No such file or directory", file=sys.stderr)
            sys.exit(1)
        ref_stat = os.stat(args.reference)
        atime_change = ref_stat.st_atime
        mtime_change = ref_stat.st_mtime
    elif args.date:
        try:
            dt_obj = parse_date(args.date)
            atime_change = mtime_change = dt_obj.timestamp()
        except (ValueError, OverflowError) as e:
            print(f"touchp: invalid date format '{args.date}'", file=sys.stderr)
            sys.exit(1)
    elif args.t:
        try:
            # Basic parsing for [[CC]YY]MMDDhhmm[.ss]
            # This is a simplification; a full implementation is very complex
            t_str = args.t
            now = datetime.datetime.now()
            if '.' in t_str:
                t_str, ss = t_str.split('.')
            else:
                ss = now.second
            
            if len(t_str) == 8: # MMDDhhmm
                yy = now.year
                mm, dd, hh, min = int(t_str[0:2]), int(t_str[2:4]), int(t_str[4:6]), int(t_str[6:8])
            elif len(t_str) == 10: # YYMMDDhhmm
                yy = int(str(now.year)[:2] + t_str[0:2])
                mm, dd, hh, min = int(t_str[2:4]), int(t_str[4:6]), int(t_str[6:8]), int(t_str[8:10])
            elif len(t_str) == 12: # CCYYMMDDhhmm
                yy = int(t_str[0:4])
                mm, dd, hh, min = int(t_str[4:6]), int(t_str[6:8]), int(t_str[8:10]), int(t_str[10:12])
            else:
                raise ValueError("Invalid format length")

            dt_obj = datetime.datetime(yy, mm, dd, hh, min, int(ss))
            atime_change = mtime_change = dt_obj.timestamp()

        except (ValueError, IndexError) as e:
            print(f"touchp: invalid date format '{args.t}' ({e})", file=sys.stderr)
            sys.exit(1)

    # Determine which times to update based on -a and -m flags
    atime_final, mtime_final = None, None
    if args.a and not args.m: # Only -a
        atime_final = atime_change or datetime.datetime.now().timestamp()
    elif args.m and not args.a: # Only -m
        mtime_final = mtime_change or datetime.datetime.now().timestamp()
    else: # Both or neither
        atime_final = atime_change or datetime.datetime.now().timestamp()
        mtime_final = mtime_change or datetime.datetime.now().timestamp()

    # Perform the touch operation on all files
    successful_files = []
    for f in args.file:
        if update_timestamps(f, mtime=mtime_final, atime=atime_final, no_create=args.no_create):
            successful_files.append(f)

    # If no files were successfully touched/created, exit now.
    if not successful_files:
        print("touchp: No files were created or updated. Exiting.")
        sys.exit(1)

    # --- Launch GUI ---
    app = QApplication.instance()  # checks if QApplication already exists
    if not app:
        app = QApplication(sys.argv)
    
    clipboard = app.clipboard()
    clipboard_text = clipboard.text()

    # Pass only the successfully handled files to the dialog
    dialog = PasteDialog(successful_files, clipboard_text)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
