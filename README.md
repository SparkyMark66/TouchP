touchp - Touch and Paste Utility
touchp is a cross-platform command-line tool that extends the functionality of the traditional touch command. It first creates a new file or updates the timestamp of an existing one, and then immediately opens a graphical user interface (GUI) allowing you to paste and save content from your clipboard directly into the file(s).
This is incredibly useful for quickly creating new script files, notes, or documents with boilerplate content you have copied.
Features
⦁	File Creation & Timestamp Updating: Works just like the standard touch command.
⦁	GUI for Pasting: After touching the file(s), a simple editor pops up, pre-filled with your clipboard's content.
⦁	Multi-file Support: Create multiple files at once, and the GUI will save the content to all of them.
⦁	Cross-Platform: Runs on Windows, macOS, and Linux.
⦁	Standard Flag Support: Implements common touch flags:
⦁	-a: Change only the access time.
⦁	-m: Change only the modification time.
⦁	-c, --no-create: Do not create the file if it doesn't exist.
⦁	-r, --reference: Use a reference file's timestamps.
⦁	-d, --date: Use a specific date string for the timestamp.
⦁	-t: Use a specific timestamp format.
Dependencies
Before running the script, you need to have Python 3 and the following libraries installed:
⦁	PyQt5: For the graphical user interface.
⦁	python-dateutil: For robust date parsing.
You can install them using pip:
pip install PyQt5 python-dateutil
How to Download and Run
You can either run the script directly using Python or compile it into a standalone executable.
Method 1: Run Directly with Python
This is the simplest method if you already have Python set up.
1.	Download the Script
⦁	Click here (or navigate to the file in the repository) and save the touchp.py file to your computer.
2.	Install Dependencies
⦁	Open your terminal or command prompt and run:  
pip install PyQt5 python-dateutil
3.	Run from the Command Line
⦁	Navigate to the directory where you saved touchp.py and run it using python3 (or python on Windows).
⦁	On macOS/Linux:  
python3 touchp.py my_file.txt
⦁	On Windows:  
python touchp.py my_file.txt
Method 2: Create a Standalone Executable
This method packages the script and its dependencies into a single executable file. This allows you to run it on other computers that don't have Python or the required libraries installed. We will use PyInstaller for this.
1.	Install PyInstaller
⦁	If you don't have it, install it via pip:  
pip install pyinstaller
2.	Create the Executable
⦁	Open your terminal or command prompt and navigate to the directory containing touchp.py.
⦁	Run the appropriate command for your operating system.
⦁	For Windows (.exe):  
pyinstaller --onefile --noconsole touchp.py
⦁	--onefile: Bundles everything into a single .exe file.
⦁	--noconsole: Prevents the command prompt from appearing when you run the GUI.
⦁	For macOS (.app):  
pyinstaller --onefile --windowed touchp.py
⦁	--windowed: Creates a macOS application bundle (.app).
⦁	For Linux:  
pyinstaller --onefile touchp.py
3.	Find and Run the Executable
⦁	PyInstaller will create a dist folder in your current directory.
⦁	Inside the dist folder, you will find your standalone executable (touchp.exe, touchp.app, or touchp).
⦁	You can move this file to a convenient location (like /usr/local/bin on Linux/macOS or a folder in your Windows PATH) to run it from anywhere.
Usage Examples
Here are a few examples of how to use touchp from the command line.
1. Create a single new file and paste content:
touchp new_script.py
(A GUI will appear with your clipboard content, ready to save to new_script.py)
2. Create multiple files with the same content:
touchp notes.txt ideas.md
(The GUI will save the content to both notes.txt and ideas.md)
3. Update a file's timestamp using a reference file:
# Set new_file.txt's timestamp to match old_file.log  
touchp -r old_file.log new_file.txt
4. Update only the modification time of an existing file:
touchp -m important_document.docx
5. Create a file with a specific timestamp:
touchp -d "2023-10-27 10:00:00" project_start.log
