Flush Tool
==========
The flush tool is used to determine an optimal flush volume given certain critera (ie. the previous product, next product, destination equipment and blend/receipt size if applicable). 
Product and equipment information is loaded from Excel files using the xlrd package.

Usage
-----
The use of the program is very intuitive. Simply enter a material code representing the previous product in the tank, the next product entering the tank, and the destination (the tank itself). Depending on which department the equipment is located in, a volume field representing the blend size will be enabled as an additional input. Click 'Generate', and the results will be displayed.

Dependencies
------------
This project was built using Python 3 with libraries from [Portable Python](http://portablepython.com), especially [PyQt](https://wiki.python.org/moin/PyQt). [xlrd](https://pypi.python.org/pypi/xlrd) was used for reading data from Excel.   

License
-------
This code can be distributed under the MIT license. 
