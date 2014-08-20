Flush Tool
==========
The flush tool is used to determine an optimal flush volume given certain critera (ie. the previous product, next product, destination equipment and blend/receipt size if applicable). 
Product and equipment information is loaded from Excel files using the xlrd package.

Usage
-----
The use of the program is very intuitive. Simply enter a material code representing the previous product in the tank, the next product entering the tank, and the destination (the tank itself). Depending on which department the equipment is located in, a volume field representing the blend size will be enabled as an additional input. Click 'Generate', and the results will be displayed.

*Note: For security reasons, the data files that the application depends on are not included in the source or in any releases. These must be added to the (unzipped) root folder before execution. If you should be using this application, you should have these files.*

Configuration
-------------
There are various variables that are read by the program from a file called 'settings.ini'. A description of the function of each variable follows:

**File Locations**

*(These represent filenames and administrative information.)*
  * Product File Name -- the name of the file - in the root directory - that contains the product information
  * Equipment File name -- the name of the file - in the root directory - that contains the equipment information
  * Title of Product Worksheet -- the name of the Excel worksheet within the Product File from which to read
  * Title of Equipment Worksheet -- the name of the Excel worksheet within the Equipment File from which to read

**Algebraic Values**

*(These represent variables and equations used in the flush calculations.)*
  * Concentration Epsilon -- the flush cycles will continue incrementing until the simulated elemental concentrations are withn X% of the target, where X is the Concentration Epsilon
  * Viscosity Epsilon -- the flush cycles will continue incrementing until the simulated viscosity values are withn X% of the target, where X is the Viscosity Epsilon
  * Viscosity Constant -- used in the calculation of ln partials. This value shouldn't be changed, but given my limited chemistry background I left this configurable just in case.
  * Demulse Constant -- the number of cycles needed when a demulse factor is present in the flush.
  * Dye Constant -- the number of cycles needed when a dye factor is present in the flush.
  * Viscosity Threshold -- when the target viscosity average is above this value, the flush product will be set to Base Oil 2

Dependencies
------------
This project was built using Python 3 with libraries from [Portable Python](http://portablepython.com), especially [PyQt](https://wiki.python.org/moin/PyQt). [xlrd](https://pypi.python.org/pypi/xlrd) was used for reading data from Excel. 

Downloads
---------
https://github.com/johnsaigle/flush-tool/releases

License
-------
This code can be distributed under the MIT license. 
