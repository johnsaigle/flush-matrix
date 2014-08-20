# GUI component of the flush tool
import sys
import flush_tool
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
        for e in flush_tool.equipment:
            QtGui.QComboBox.addItem(combobox, e.name)

    def grab_destination_selection(self):
        self.label_num_cycles.setValue(0)
        self.label_cycle_volume.setText("0")
        self.label_material.setText("--")
        self.linetext_volume.setText("0")
        selection = self.combo_destination.currentText()
        for e in flush_tool.equipment:
            if e.name == selection:
                department = e.area
                break
        if department == 'Blending':
            self.label_cycle_volume.setText("0")
            self.linetext_volume.setEnabled(True)
            self.label_volume.setText('Blend Size (L)')
        elif department == 'Bulk Receiving':
            self.label_cycle_volume.setText("0")
            self.linetext_volume.setEnabled(True)
            self.label_volume.setText('Receipt Size (L)')
        else:
            self.label_cycle_volume.setText("0")
            self.linetext_volume.setEnabled(False)
            self.label_volume.setText('Volume (L)')


    def button_generate_clicked(self):
        """Controls the behaviour of the 'Generate' button."""
        # ensure integrity of user values
        prev_product_code = self.linetext_prev.text().strip()
        next_product_code = self.linetext_next.text().strip()
        equipment_destination_name = self.combo_destination.currentText()
        destination = None
        volume = 0
        for e in flush_tool.equipment:
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

        # we don't want to run calculations on identicla codes
        if prev_product_code == next_product_code:
            QtGui.QMessageBox.critical(self,
                   "Invalid Input",
                   "Product codes are identical.")
            return

        # check to make sure provided codes correspond to a product in the database
        prev_product = flush_tool.find_match(prev_product_code)
        if prev_product is None:
            QtGui.QMessageBox.critical(self,
                 "Invalid Input",
                 "No match found for Previous Material Code")
            return
     
        next_product = flush_tool.find_match(next_product_code)
        if next_product is None:
            QtGui.QMessageBox.critical(self,
                 "Invalid Input",
                 "No match found for Next Material Code")
            return

        # if everything is kosher so far, launch the calculating script
        if destination.area == 'Packaging':
            num_flush_cycles = flush_tool.generate_flush_factor(prev_product, next_product, destination)
        else:
            try:
                volume = float(self.linetext_volume.text())
                if volume <= 0:
                    QtGui.QMessageBox.critical(self,
                        "Invalid Input",
                        "Volume must be greater than zero.")
                    return
            except ValueError:
                QtGui.QMessageBox.critical(self,
                    "Invalid Input",
                    "Volume must be a number.")
                return

            num_flush_cycles = flush_tool.generate_flush_factor(prev_product, next_product, destination, volume)
            self.label_cycle_volume.setText("0")
            self.label_num_cycles.setValue(0)
            self.label_material.setText("--")

        if num_flush_cycles is None:
            logging.critical("Fatal error: unable to calculate flush factor.")
        elif num_flush_cycles < 0:
            logging.critical("Flush factor is less than 0.")
        elif num_flush_cycles == 0:
            self.label_num_cycles.setValue(int(num_flush_cycles))
            self.label_cycle_volume.setText("0")
            self.label_material.setText("--")
            QtGui.QMessageBox.critical(self,
                  "Similar Products",
                  "The flush result is equal to zero. No flush necessary!")
        else:
            self.label_cycle_volume.setText("0")
            self.label_num_cycles.setValue(int(num_flush_cycles))
            self.label_cycle_volume.setText(str(destination.cycle_size))
            self.label_material.setText(str(destination.flush_material))

def main():
    # initialize and show window
    app = QtGui.QApplication(sys.argv)
    
    # load backend before creating front end
    flush_tool.init_data()

    window = AppWindow(None)
    # start
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
