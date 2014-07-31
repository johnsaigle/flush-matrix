# GUI component of the flush tool
import sys
import flush_matrix
import configparser
from PyQt4 import QtCore, QtGui, uic

# set ui file
form_class = uic.loadUiType("flushtool_interface.ui")[0] # load ui file

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
    def __init__(self, parent = None): # parent specification may not be necessary
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.show()
        # bind buttons to event handlers
        self.button_generate.clicked.connect(self.button_generate_clicked)
        self.combo_destination.activated.connect(self.grab_destination_selection)
    
        # populate combo boxes with equipment names
        self.populate_combo_box(self.combo_destination)

    def populate_combo_box(self, combobox):
        for e in flush_matrix.equipment:
            QtGui.QComboBox.addItem(combobox, e.name)

    def grab_destination_selection(self):
        selection = self.combo_destination.currentText()
        print("Destination selection: " + str(selection))
        for e in flush_matrix.equipment:
            if e.name == selection:
                department = e.area
                break
        if department == 'Blending':
            self.combo_source.setEnabled(True)
            self.linetext_volume.setEnabled(True)
            self.label_volume.setText('Blend Size (L)')
        elif department == 'Bulk Receiving':
            self.combo_source.setEnabled(True)
            self.linetext_volume.setEnabled(True)
            self.label_volume.setText('Receipt Size (L)')
        else:
            self.combo_source.setEnabled(False)
            self.linetext_volume.setEnabled(False)
            self.label_volume.setText('Volume (L)')


    def button_generate_clicked(self):
        """Controls the behaviour of the 'Generate' button."""
        # ensure integrity of user values
        prev_product_code = self.linetext_prev.text().strip()
        next_product_code = self.linetext_next.text().strip()
        equipment_destination_name = self.combo_destination.currentText()
        destination = None
        source = None
        for e in flush_matrix.equipment:
            if e.name == equipment_destination_name:
                destination = e
                break
        flush_factor = None

        # validate equipment selection
        if destination is None:
            QtGui.QMessageBox.critical(self,
                 "Invalid Input",
                 "Could not find in loaded equipment for destination selection.")
            return

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
        if source is None:
            num_flush_cycles = flush_matrix.generate_flush_factor(prev_product, next_product, destination)
        else:
            num_flush_cycles = flush_matrix.generate_flush_factor(prev_product, next_product, destination, source)

        if num_flush_cycles is None:
            print("Fatal error: unable to calculate flush factor. (are the values correct?)")
        elif num_flush_cycles <= 0:
            print("Error: flush factor is 0.")
        else:
            self.label_num_cycles.setValue(int(num_flush_cycles))
            self.label_cycle_volume.setText(str(destination.cycle_size))

def main():
    # initialize and show window
    app = QtGui.QApplication(sys.argv)
    
    # load backend before creating front end
    flush_matrix.init_data()

    window = AppWindow(None)
    # start
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
