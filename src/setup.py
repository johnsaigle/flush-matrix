import sys
from cx_Freeze import setup, Executable

setup(
        name = 'Flush Tool',
        version = '0.1',
        description = 'T tool to facilitate product flush calculations',
        executables = [Executable("flush_matrix.py")])
