import sys
from cx_Freeze import setup, Executable

setup(
        name = 'Flush Tool',
        version = '0.2',
        description = 'T tool to facilitate product flush calculations',
        executables = [Executable("gui_handler.py", 
		targetName="FlushTool.exe",
		base="Win32GUI")])
