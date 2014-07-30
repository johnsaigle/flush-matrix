# GUI component of the flush tool
import sys
import flush_matrix
from PyQt4 import QtCore, QtGui, uic

# load backend before creating front end
flush_matrix.init_data()

# set ui file
form_class = uic.loadUiType("mockup.ui")[0] # temporary file name

class ErrorDialog(QtGui.QDialog):
    def __init__(self, parent = None):
        super(ErrorDialog, self).__init__(parent)

        layout = QVBoxLayout(self)

        self.buttons = QDialogButtonBox(
                QDialogButtonBox.Ok, self)
        self.layout.addWidget(self.buttons)

    def showDialog(self):
        self.show()

class AppWindow(QtGui.QMainWindow, form_class):
    def __init__(self, parent = None): # parent specification my not be necessary
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        # bind buttons to event handlers
        self.button_generate_flush.clicked.connect(self.button_generate_clicked)

    def button_generate_clicked(self):
        # ensure integrity of user values
        prev_product_code = self.linetext_prev.text().strip()
        next_product_code = self.linetext_next.text().strip()
        flush_factor = None

        # NEVER FORGET ABOUT BUFFER OVERFLOW
        if len(prev_product_code) > 15 or len (next_product_code) > 15:
            QtGui.QMessageBox.critical(self,
                    "Invalid Input",
                    "Material code is too large.")
            return

        # check prev value isn't empty
        if prev_product_code is None or prev_product_code == "":
            QtGui.QMessageBox.critical(self,
                    "Invalid Input",
                    "Please fill in the 'Previous Material Code' field.")
            return
        
        # check next value isn't empty
        if next_product_code is None or next_product_code == "":
            QtGui.QMessageBox.critical(self,
                    "Invalid Input",
                    "Please fill in the 'Next Material Code' field.")
            return

        # convert codes grabbed from text fields into ints
        try:
            prev_product_code = int(prev_product_code)
            next_product_code = int(next_product_code)
        except ValueError:
            QtGui.QMessageBox.critical(self,
                    "Invalid Input",
                    "Material codes must be integers.")
            return

        # check to make sure provided codes correspond to a product in the database
        prev_product = flush_matrix.find_match(prev_product_code)
        if prev_product is None:
            QtGui.QMessageBox.critical(self,
                    "Invalid Input",
                    "No match found for Previous Material Code")
            return
        
        next_product = flush_matrix.find_match(next_product_code)
        if next_product is None:
            QtGui.QMessageBox.critical(self,
                    "Invalid Input",
                    "No match found for Next Material Code")
            return
        # if everything is kosher so far, launch the calculating script
       
        flush_factor = flush_matrix.generate_flush_factor(prev_product, next_product)

        if flush_factor is None:
            print("Fatal error: unable to calculate flush factor. (are the values correct?)")
        elif flush_factor <= 0:
            print("Error: flush factor is 0.")
        else:
            self.flush_volume.setText(str(flush_factor))

# initialize and show window
app = QtGui.QApplication(sys.argv)
window = AppWindow(None)
window.show()
app.exec_()
