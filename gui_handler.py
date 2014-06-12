# GUI component of the flush tool
import sys
from PyQt4 import QtCore, QtGui, uic
import flush_matrix

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
        prev_value = self.linetext_prev.text().strip()
        next_value = self.linetext_next.text().strip()

        # NEVER FORGET ABOUT BUFFER OVERFLOW
        if len(prev_value) > 15 or len (next_value) > 15:
            QtGui.QMessageBox.critical(self,
                    "Invalid Input",
                    "Material code is too large.")
            return

        # check prev value isn't empty
        if prev_value is None or prev_value == "":
            QtGui.QMessageBox.critical(self,
                    "Invalid Input",
                    "Please fill in the 'Previous Material Code' field.")
            return
        
        # check next value isn't empty
        if next_value is None or next_value == "":
            QtGui.QMessageBox.critical(self,
                    "Invalid Input",
                    "Please fill in the 'Next Material Code' field.")
            return

        # convert codes to ints
        try:
            prev_value = int(prev_value)
            next_value = int(next_value)
        except ValueError:
            QtGui.QMessageBox.critical(self,
                    "Invalid Input",
                    "Material codes must be integers.")
            return

        # check to make sure provided codes correspond to a product in the database
        if flush_matrix.find_match(prev_value) is None:
            QtGui.QMessageBox.critical(self,
                    "Invalid Input",
                    "No match found for Previous Material Code")
            return

        if flush_matrix.find_match(next_value) is None:
            QtGui.QMessageBox.critical(self,
                    "Invalid Input",
                    "No match found for Next Material Code")
            return
        # if everything is kosher so far, launch the calculating script
        try:
            flush_factor = flush_matrix.generate_flush_factor(prev_value, next_value)
        except Exception as e:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)
        
        # display value
        self.flush_volume.setText(str(flush_factor))


# initialize and show window
app = QtGui.QApplication(sys.argv)
window = AppWindow(None)
window.show()
app.exec_()

