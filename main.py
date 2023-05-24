from GUI_P4 import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QLabel,QSlider,QLineEdit,QComboBox,QPushButton,QInputDialog,QMessageBox
from PyQt5.QtCore import Qt,QThread, pyqtSignal
from RWP import*
import sys
import serial.tools.list_ports
import serial

class SerialThread(QThread):
    response_received = pyqtSignal(str)

    def __init__(self, port, baud_rate, data, parent=None):
        super().__init__(parent)
        self.port = port
        self.baud_rate = baud_rate
        self.data = data
        self.serial_port = None
        self.transmitting = False

    def open_serial_port(self):
        self.serial_port = serial.Serial(self.port, self.baud_rate)

    def close_serial_port(self):
        try:
            if self.serial_port is not None:
                self.serial_port.cancel_read()
                self.serial_port.close()
                self.serial_port = None
                
        except Exception as e:
            error_message = f"An error occurred while closing the serial port:\n\n{str(e)}"
            QtWidgets.QMessageBox.warning(None, "Error", error_message)

    def run(self):
        try:
            self.open_serial_port()
            self.transmitting = True
            self.serial_port.write(self.data.encode('utf-8'))  # Send the data to the board

            # Wait for response
            try:
                response = self.serial_port.read().decode('utf-8')
            except UnicodeDecodeError as e:
                response = self.serial_port.read().decode('utf-8', errors='ignore')

            self.transmitting = False
            self.response_received.emit(response)
            self.close_serial_port()
        except serial.SerialException as e:
            error_message = str(e)
            self.transmitting = False
            self.response_received.emit(error_message)


    def stop_transmission(self):
        if self.transmitting:
            self.serial_port.write(b's\n')  # Send 's\n' to the board to stop transmission
            self.transmitting = False
            self.close_serial_port()

class MyWindow(QtWidgets.QMainWindow):

    def __init__(self):
      
        super(MyWindow, self).__init__()
        
        self.serial_thread = None
        # Load the ui file
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(800, 600)
        #Define our widgets
        self.mode = self.findChild(QLabel,"Mode")
        self.slider_laps = self.findChild(QSlider,"slidelaps")
        self.label_laps = self.findChild(QLineEdit,"ShowLaps")
        self.slider_speed = self.findChild(QSlider,"slidespeed")
        self.label_speed = self.findChild(QLineEdit,"Showspeed")
        self.label_diameter = self.findChild(QLineEdit,"Diameter")
        self.combo = self.findChild(QComboBox, "listport")
        self.listprofile = self.findChild(QComboBox, "listprofile")
        self.start_btn = self.findChild(QPushButton,"Start")
        self.stop_btn = self.findChild(QPushButton,"Stop")
        self.save_btn = self.findChild(QPushButton,"Save")
        self.load_btn = self.findChild(QPushButton,"Load")
        self.delete_btn = self.findChild(QPushButton,"Delete")
        self.refresh_btn = self.findChild(QPushButton,"Refresh")

        self.stop_btn.clicked.connect(self.stop_transmission)
        self.stop_btn.setEnabled(False)  # Disable the "Stop" button initially

        self.label_laps.setText("0")
        self.label_speed.setText("0")
        self.label_diameter.setText("0")
        #self.label_laps.hide()
        self.listprofile.addItem("New")
        self.listprofile.setCurrentIndex(-1)
        self.listprofile.activated.connect(self.onComboboxActivated)

        readProfile()
        for name in readProfile():
            self.listprofile.addItem(name)

        # Set the validator for line_edit to allow only integer input
        validator = QIntValidator()
        validator_laps = QIntValidator(0,99)
        validator_speed = QIntValidator(0,999)
        self.label_diameter.setValidator(validator)
        self.label_laps.setValidator(validator_laps)
        self.label_speed.setValidator(validator_speed)
        
        # Set the initial value of laps
        self.slide_laps(0)
        self.slide_speed(0)

        # Initialize the serial port variable
        self.ser = None

        self.start_btn.clicked.connect(self.send_data)
        self.stop_btn.clicked.connect(self.stop_transmission)
        self.stop_btn.setEnabled(False)  # Disable the "Stop" button initially
        self.refresh_btn.clicked.connect(self.refresh_ports)
        self.save_btn.clicked.connect(self.save)
        self.delete_btn.clicked.connect(self.delete)
        # Get a list of available serial ports
        ports = serial.tools.list_ports.comports()

        # Create an empty list to store the port descriptions
        port_descriptions = []

        # Add each port description to the list
        for port in ports:
            port_name = port.device
            port_descriptions.append(port_name)

        # Sort the list of port descriptions
        port_descriptions.sort()

        # Add the sorted port descriptions to the combo box
        for description in port_descriptions:
            self.combo.addItem(description)

        #Set don't choose at open
        self.combo.setCurrentIndex(-1)

        #Center the label
        self.label_laps.setAlignment(QtCore.Qt.AlignCenter)
        self.label_speed.setAlignment(QtCore.Qt.AlignCenter)
        
        # Connect signals to slots
        self.label_laps.textChanged.connect(self.updateSliderLaps)
        self.label_speed.textChanged.connect(self.updateSliderSpeed)
        self.slider_laps.valueChanged.connect(self.updateLineEditLaps)
        self.slider_speed.valueChanged.connect(self.updateLineEditSpeed)
        
    #Function when click profile in profile combobox it gonna input data autom
    def onComboboxActivated(self, index):
        selected_item = self.combo.currentText()
        parameters = self.load(selected_item)

        if parameters is not None:
            diameter = parameters["Diameter"]
            speed = parameters["Speed"]
            laps = parameters["Lap"]

            self.label_diameter.setText(f"Diameter: {diameter}")
            self.label_speed.setText(f"Speed: {speed}")
            self.label_laps.setText(f"Laps: {laps}")    

        if self.combo.currentText() == "New":
            pass
    #Save profile
    def save(self):

        selected_name = self.listprofile.currentText()
        
        if selected_name == "New":
            name, ok = QInputDialog.getText(self, "Enter Name", "Please enter the name:")

            if ok and name and self.listprofile.currentText() == "New":

                diameter = self.label_diameter.text()
                speed = self.slider_speed.value()
                laps = self.slider_laps.value()
                data = diameter + str(speed) + str(laps)
                print(data)
                updateProfile(name, int(diameter), speed, laps)
                QMessageBox.information(self, "Saved", "Profile saved successfully.")
                self.refresh_profile()
                #self.refresh_ports()

        elif self.listprofile.currentText() == "":

            QMessageBox.information(self, "Warning", "Please select Profile.")

        elif selected_name is not None:

            name = self.listprofile.currentText()
            laps = self.slider_laps.value()
            diameter = self.label_diameter.text()
            speed = self.slider_speed.value()

            updateProfile(name, int(diameter), speed, laps)
            QMessageBox.information(self, "Saved", "Profile saved successfully.")
            self.refresh_profile()
            #self.refresh_ports()
        
        else:
            QMessageBox.information(self, "Warning", "Please select Profile.")
    #load profiel
    def load(self,selected_name):
       
        selected_name = self.listprofile.currentText()

        if self.listprofile.currentText() == "":
             
             QMessageBox.information(self, "Warning", "Please select Profile.")

        elif self.listprofile.currentText() == "New":

            pass

        else:

            data = selectedProfile(selected_name)
            Diameter = data['Diameter']
            Speed = data['Speed']
            Lap = data['Lap']
            self.label_diameter.setText(str(Diameter))
            self.slider_speed.setValue(Speed)
            self.slider_laps.setValue(Lap)
            #print(selectedProfile(selected_name))
    #deleter profile
    def delete(self):
        
        selected_name = self.listprofile.currentText()

        if self.listprofile.currentText() == "":
             
             QMessageBox.information(self, "Warning", "Please select Profile.")

        elif self.listprofile.currentText() == "New":
             
             QMessageBox.information(self, "Warning", "Please select Other Profile.")
        
        else:
            reply = QMessageBox.question(self, "Confirmation", "Are you sure you want to Delete?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
            # User clicked "Yes"
                deleteProfile(selected_name)
                self.refresh_profile()
                print("Confirmed")
            else:
                # User clicked "No" or closed the message box
                print("Cancelled")
        
    def updateSliderLaps(self, text):
        # Convert the text to an integer value
        try:
            value = int(text)
        except ValueError:
            # If the conversion fails, set the value to 0
            value = 0

        if value > 0:
            self.label_laps.show()
            self.mode.setGeometry(550, 164, 141, 33)
            self.mode.setAlignment(QtCore.Qt.AlignCenter)
            self.mode.setText("Laps")
        else:
            #self.label_laps.hide()
            self.mode.setGeometry(550, 164, 141, 33)
            self.mode.setAlignment(QtCore.Qt.AlignCenter)
            self.mode.setText("Continuos")
        # Set the value of the slider
        self.slider_laps.setValue(value)

        # Set the focus to the line edit to allow further editing
        self.label_laps.setFocus(Qt.OtherFocusReason)

    def updateLineEditLaps(self, value):
        # Update the text in the line edit
        self.label_laps.setText(str(value))

    def updateSliderSpeed(self, text):
        # Convert the text to an integer value
        try:
            value = int(text)
        except ValueError:
            # If the conversion fails, set the value to 0
            value = 0

        # Set the value of the slider
        self.slider_speed.setValue(value)

        # Set the focus to the line edit to allow further editing
        self.label_speed.setFocus(Qt.OtherFocusReason)

    def updateLineEditSpeed(self, value):
        # Update the text in the line edit
        self.label_speed.setText(str(value))

    def slide_laps(self,value):
        value = self.slider_laps.value()
        self.label_laps.setText(str(value))
        self.laps = value
        
    def slide_speed(self,value):
        value = self.slider_speed.value()
        self.label_speed.setText(str(value))
        self.speed = value

    def refresh_profile(self):

        #self.combo.clear()
        self.listprofile.clear()
        self.listprofile.addItem("New")
        self.listprofile.setCurrentIndex(-1)
        readProfile()
        for name in readProfile():
            self.listprofile.addItem(name)

    def refresh_ports(self):

        self.combo.clear()
        # Get a list of available serial ports
        ports = sorted(serial.tools.list_ports.comports(), key=lambda x: x.device)

        # Add each port to the combo box
        for port in ports:
            port_name = port.device
            port_description = port_name
            self.combo.addItem(port_description)
            self.combo.setCurrentIndex(-1)

    def send_data(self):
        #Block click 
        self.start_btn.setEnabled(False)  # Disable the "Send" button
        self.stop_btn.setEnabled(True)  # Enable the "Stop" button

        if not self.serial_thread or not self.serial_thread.isRunning():
            #Get value 
            port = self.combo.currentText()
            laps = self.laps
            speed = self.speed        
            diameter = self.label_diameter.text()

            speed = self.slider_speed.value() or 0

            diameter = int(diameter)
            speed_f = float(16*speed*diameter/60)
            dist = float(16*diameter)

            if not port:
                QMessageBox.warning(self, "Warning", "Please enter the port.")
                self.start_btn.setEnabled(True)  # Enable the "Send" button
                self.stop_btn.setEnabled(False)  # Disable the "Stop" button
                return

            if diameter == "0":
                QMessageBox.warning(self, "Invalid Input", "Please enter a diameter.")
                self.start_btn.setEnabled(True)  # Enable the "Send" button
                self.stop_btn.setEnabled(False)  # Disable the "Stop" button
                return
            
            if speed == 0:
                QMessageBox.warning(self, "Speed Warning", "Please set speed.")
                self.start_btn.setEnabled(True)  # Enable the "Send" button
                self.stop_btn.setEnabled(False)  # Disable the "Stop" button
                return

            laps = self.slider_laps.value() or 0
            
            data = str(speed_f) + "," + str(dist) + "," + str(laps) + "\n"
            self.serial_thread = SerialThread(port, 115200, data)  
            self.serial_thread.response_received.connect(self.handle_response)
            self.serial_thread.start()

    def handle_response(self, response):
        if "PermissionError" in response:
            QMessageBox.warning(self, "Serial Port Error", "Cannot configure port. Please check the device connection and permissions.")
        else:
            pass

        self.start_btn.setEnabled(True)  # Enable the "Send" button
        self.stop_btn.setEnabled(False)  # Disable the "Stop" button

    def stop_transmission(self):
        if self.serial_thread and self.serial_thread.isRunning():
            self.serial_thread.stop_transmission()
            print("Transmission stopped.")

            self.start_btn.setEnabled(True)  # Enable the "Send" button
            self.stop_btn.setEnabled(False)  # Disable the "Stop" button

if __name__ == "__main__":
    
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
