from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QPushButton, QLabel, 
                           QTableWidget, QTableWidgetItem, QScrollArea, 
                           QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QDialog, QVBoxLayout, QTextEdit, QPushButton
from PyQt5.QtGui import QFont 

import sys

class IAS_arch:
    def __init__(self):
        self.PC = 0      # Program Counter
        self.MAR = 0     # Memory Address Register
        self.MBR = 0     # Memory Buffer Register
        self.AC = 0      # Accumulator
        self.MQ = 0      # Multiplier Quotient
        self.IBR = 0     # Instruction Buffer Register
        self.IR = 0      # Instruction Register
        self.MEMORY = [0] * 1000  # Memory with 1000 lines
        self.execution_log = []

    def load_data(self, data_l, ins_val):
        # Load data into memory
        for i in data_l:
            if 0 <= i[1] < len(self.MEMORY):
                self.MEMORY[i[1]] = i[0]
            else:
                self.log_execution(f"Error: Memory address {i[1]} out of range.")

        # Handle instructions
        if len(ins_val) % 2 != 0:
            ins_val.append(("HALT", 0))
            
        ins_dic = {
            "HALT": 0x00, "LOAD": 0x01, "JUMPR+": 0x10, "LOADMQM": 0x09,
            "STOR": 0x21, "LOAD-": 0x02, "LOAD|": 0x03, "LOAD|-": 0x04,
            "JUMPL": 0x0D, "JUMPR": 0x0E, "JUMPL+": 0x0F, "LOADMQ": 0x0A,
            "ADD": 0x05, "SUB": 0x06, "ADD|": 0x07, "SUB|": 0x08,
            "LSH": 0x14, "RSH": 0x15, "MUL": 0x0B, "DIV": 0x0C,
            "STORL": 0x12, "STORR": 0x13
        }

        i = 0
        for j in range(0, len(ins_val), 2):
            if j < len(self.MEMORY):
                if i+1 < len(ins_val):
                    self.MEMORY[j//2] = ((ins_dic[ins_val[i][0]] << 32) | 
                                       (ins_val[i][1] << 20) | 
                                       (ins_dic[ins_val[i+1][0]] << 12) | 
                                       ins_val[i+1][1])
                    i += 2
                else:
                    self.MEMORY[j//2] = ((ins_dic[ins_val[i][0]] << 32) | 
                                       (ins_val[i][1] << 20))
            else:
                self.log_execution(f"Error: Memory address {j} out of range.")

    def log_execution(self, message):
        self.execution_log.append(message)

    def fetch(self):
        self.MAR = self.PC
        if 0 <= self.MAR < len(self.MEMORY):
            self.MBR = self.MEMORY[self.MAR]
            self.log_execution(f"Fetched instruction from memory address {self.MAR}")
            self.fetch_inst_l()
        else:
            self.log_execution(f"Error: Program Counter {self.MAR} out of range.")

    def fetch_inst_l(self):
        ir_dic = {
            0: "HALT", 1: "LOAD M(X)", 2: "LOAD -M(X)", 3: "LOAD |M(X)|",
            4: "LOAD -|M(X)|", 5: "ADD M(X)", 6: "SUB M(X)", 7: "ADD |M(X)|",
            8: "SUB |M(X)|", 9: "LOAD MQ,M(X)", 10: "LOAD MQ", 11: "MUL M(X)",
            12: "DIV M(X)", 13: "JUMP M(X,0:19)", 14: "JUMP M(X,20:39)",
            15: "JUMP+ M(X,0:19)", 16: "JUMP+ M(X,20:39)", 18: "STOR M(X,8:19)",
            19: "STOR M(X,28:39)", 20: "LSH", 21: "RSH", 33: "STOR M(X)"
        }

        l_INS = (self.MBR >> 20) & 0xFFFFF
        self.IR = (l_INS >> 12) & 0xFF
        l_ADR = l_INS & 0xFFF

        self.IBR = self.MBR & 0xFFFFF
        self.log_execution(f"Executing {ir_dic.get(self.IR, 'Unknown')} : {l_ADR}")
        if self.IR == 0x00:
            return

        self.execute_ins(self.IR, l_ADR)
        self.fetch_inst_r()

    def fetch_inst_r(self):
        ir_dic = {
            0: "HALT", 1: "LOAD M(X)", 2: "LOAD -M(X)", 3: "LOAD |M(X)|",
            4: "LOAD -|M(X)|", 5: "ADD M(X)", 6: "SUB M(X)", 7: "ADD |M(X)|",
            8: "SUB |M(X)|", 9: "LOAD MQ,M(X)", 10: "LOAD MQ", 11: "MUL M(X)",
            12: "DIV M(X)", 13: "JUMP M(X,0:19)", 14: "JUMP M(X,20:39)",
            15: "JUMP+ M(X,0:19)", 16: "JUMP+ M(X,20:39)", 18: "STOR M(X,8:19)",
            19: "STOR M(X,28:39)", 20: "LSH", 21: "RSH", 33: "STOR M(X)"
        }

        r_INS = self.IBR
        self.IR = (r_INS >> 12) & 0xFF
        r_ADR = r_INS & 0xFFF

        self.log_execution(f"Executing {ir_dic.get(self.IR, 'Unknown')} : {r_ADR}")

        if self.IR == 0x00:
            return
        
        self.execute_ins(self.IR, r_ADR)

        self.PC += 1
        self.fetch()

    def execute_ins(self, OPC, ADR):
        if OPC == 0x00:
            pass
        elif OPC == 0x01:  # LOAD M(X)
            self.AC = self.MEMORY[ADR]
        elif OPC == 0x0A:  # LOAD MQ
            self.AC = self.MQ
        elif OPC == 0x09:  # LOAD MQ, M(X)
            self.MQ = self.MEMORY[ADR]
        elif OPC == 0x21:  # STOR M(X)
            self.MEMORY[ADR] = self.AC
        elif OPC == 0x02:  # LOAD -M(X)
            self.AC = -self.MEMORY[ADR]
        elif OPC == 0x03:  # LOAD |M(X)|
            self.AC = abs(self.MEMORY[ADR])
        elif OPC == 0x04:  # LOAD -|M(X)|
            self.AC = -abs(self.MEMORY[ADR])
        elif OPC == 0x0D:  # JUMP LEFT
            self.PC = ADR
            self.fetch()
        elif OPC == 0x0E:  # JUMP RIGHT
            self.PC = ADR
            self.MAR = self.PC
            if 0 <= self.MAR < len(self.MEMORY):
                self.log_execution(f"Fetched instruction from memory address {self.MAR}")
                self.MBR = self.MEMORY[self.MAR]
                l_INS = (self.MBR >> 20) & 0xFFFFF
                self.IBR = self.MBR & 0xFFFFF
                self.fetch_inst_r()
            else:
                print(f"Error: Program Counter {self.MAR} out of range.")
            
        elif OPC == 0x0F:  # JUMP LEFT IF AC > 0
            if self.AC > 0:
                self.PC = ADR
                self.fetch_inst_l()
        elif OPC == 0x10:  # JUMP RIGHT IF AC > 0
            if self.AC > 0:
                self.PC = ADR
                self.MAR = self.PC
                if 0 <= self.MAR < len(self.MEMORY):
                    self.log_execution(f"Fetched instruction from memory address {self.MAR}")
                    self.MBR = self.MEMORY[self.MAR]
                    l_INS = (self.MBR >> 20) & 0xFFFFF
                    self.IBR = self.MBR & 0xFFFFF
                else:
                    print(f"Error: Program Counter {self.MAR} out of range.")
                self.fetch_inst_r()
        elif OPC == 0x05:  # ADD M(X)
            self.AC += self.MEMORY[ADR]
        elif OPC == 0x07:  # ADD |M(X)|
            self.AC += abs(self.MEMORY[ADR])
        elif OPC == 0x06:  # SUB M(X)
            self.AC -= self.MEMORY[ADR]
        elif OPC == 0x08:  # SUB |M(X)|
            self.AC -= abs(self.MEMORY[ADR])
        elif OPC == 0x14:  # LSH
            self.AC = self.AC << 1
        elif OPC == 0x15:  # RSH
            self.AC = self.AC >> 1
        elif OPC == 0x0B:  # MUL M(X)
            result = self.MQ * self.MEMORY[ADR]
            # Split result into most and least significant bits
            self.AC = result >> 32  # Most significant bits
            self.MQ = result & 0xFFFFFFFF  # Least significant bits
        elif OPC == 0x0C:  # DIV M(X)
            if self.MEMORY[ADR] != 0:
                self.MQ = self.AC // self.MEMORY[ADR]  # Quotient
                self.AC = self.AC % self.MEMORY[ADR]   # Remainder
            else:
                print("Error: Division by zero")
        elif OPC == 0x12:  # STOR M(X,8:19) - Modify left instruction (bits 8-19 of first 20 bits)
            # Create mask for bits 8:19 within the left instruction (first 20 bits)
            left_part = (self.MEMORY[ADR] >> 20) & 0xFFFFF  # Extract left 20 bits
            right_part = self.MEMORY[ADR] & 0xFFFFF         # Extract right 20 bits
            
            # Clear bits 8:19 in left instruction and set with AC
            left_part = (left_part & ~(0xFFF << 8)) | ((self.AC & 0xFFF) << 8)
            
            # Recombine the parts
            self.MEMORY[ADR] = (left_part << 20) | right_part

        elif OPC == 0x13:  # STOR M(X,28:39) - Modify right instruction (bits 8-19 of second 20 bits)
            left_part = (self.MEMORY[ADR] >> 20) & 0xFFFFF  # Extract left 20 bits
            right_part = self.MEMORY[ADR] & 0xFFFFF         # Extract right 20 bits
            
            # Clear bits 8:19 in right instruction and set with AC
            right_part = (right_part & ~(0xFFF << 8)) | ((self.AC & 0xFFF) << 8)
            
            # Recombine the parts
            self.MEMORY[ADR] = (left_part << 20) | right_part

class IASSimulatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ias = IAS_arch()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("IAS Architecture Simulator")
        self.setGeometry(100, 100, 1400, 800)  # Made window wider to accommodate memory viewer
        # self.setAutoFillBackground(True)
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel for input (previous code remains the same until right panel)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Instruction input
        instruction_label = QLabel("Assembly Instructions:")
        instruction_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.instruction_editor = QTextEdit()
        self.instruction_editor.setPlaceholderText("Enter instructions (one per line)\nFormat: INSTRUCTION ADDRESS\nExample: LOAD 100")
        
        # Data input table
        data_label = QLabel("Data Memory:")
        data_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.data_table = QTableWidget(500, 2)
        self.data_table.setHorizontalHeaderLabels(["Value", "Address"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        left_layout.addWidget(instruction_label)
        left_layout.addWidget(self.instruction_editor)
        left_layout.addWidget(data_label)
        left_layout.addWidget(self.data_table)

        # Center panel for memory viewer
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        
        # Memory viewer section
        memory_viewer_label = QLabel("Memory Viewer:")
        memory_viewer_label.setFont(QFont('Arial', 10, QFont.Bold))
        
        # Memory address input layout
        memory_input_layout = QHBoxLayout()
        self.memory_address_input = QTextEdit()
        self.memory_address_input.setPlaceholderText("Enter memory addresses (one per line)")
        self.memory_address_input.setMaximumHeight(100)
        self.view_memory_button = QPushButton("View Memory")
        self.view_memory_button.clicked.connect(self.view_memory)
        memory_input_layout.addWidget(self.memory_address_input)
        memory_input_layout.addWidget(self.view_memory_button)
        
        # Memory display table
        self.memory_display = QTableWidget(0, 2)  # Start with 0 rows
        self.memory_display.setHorizontalHeaderLabels(["Address", "Value"])
        self.memory_display.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        center_layout.addWidget(memory_viewer_label)
        center_layout.addLayout(memory_input_layout)
        center_layout.addWidget(self.memory_display)

        # Right panel (modified to be more compact)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Control buttons
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Run Simulation")
        self.run_button.clicked.connect(self.run_simulation)
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_all)
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.clear_button)

        # Output console
        output_label = QLabel("Execution Output:")
        output_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)

        # Register display
        register_label = QLabel("Registers:")
        register_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.register_display = QTextEdit()
        self.register_display.setReadOnly(True)
        self.register_display.setMaximumHeight(150)

        right_layout.addLayout(button_layout)
        right_layout.addWidget(output_label)
        right_layout.addWidget(self.output_console)
        right_layout.addWidget(register_label)
        right_layout.addWidget(self.register_display)

        # Add all panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(center_panel)
        main_layout.addWidget(right_panel)

        # Set size policies for panels
        left_panel.setMinimumWidth(300)
        center_panel.setMinimumWidth(300)
        right_panel.setMinimumWidth(300)

        # Add help button
        self.create_help_button()

    def view_memory(self):
        try:
            # Clear existing display
            self.memory_display.setRowCount(0)
            
            # Get addresses to view
            addresses = self.memory_address_input.toPlainText().strip().split('\n')
            valid_addresses = []
            
            # Validate addresses
            for addr in addresses:
                try:
                    addr_int = int(addr)
                    if 0 <= addr_int < len(self.ias.MEMORY):
                        valid_addresses.append(addr_int)
                    else:
                        self.output_console.append(f"Warning: Address {addr} out of range (0-999)")
                except ValueError:
                    if addr.strip():  # Only show warning if the line isn't empty
                        self.output_console.append(f"Warning: Invalid address format: {addr}")
            
            # Sort addresses for better display
            valid_addresses.sort()
            
            # Update table
            self.memory_display.setRowCount(len(valid_addresses))
            for i, addr in enumerate(valid_addresses):
                # Add address
                addr_item = QTableWidgetItem(str(addr))
                addr_item.setFlags(addr_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                self.memory_display.setItem(i, 0, addr_item)
                
                # Add value
                value_item = QTableWidgetItem(str(self.ias.MEMORY[addr]))
                value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                self.memory_display.setItem(i, 1, value_item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while viewing memory: {str(e)}")

    # def clear_all(self):
    #     super_clear_all(self)  # Call the original clear_all method
    #     self.memory_address_input.clear()
    #     self.memory_display.setRowCount(0)

    def run_simulation(self):
        try:
            # Parse instructions
            instructions = []
            for line in self.instruction_editor.toPlainText().strip().split('\n'):
                if line.strip():
                    ins, addr = line.strip().split()
                    instructions.append((ins.upper(), int(addr)))

            # Parse data
            data = []
            for row in range(self.data_table.rowCount()):
                value_item = self.data_table.item(row, 0)
                addr_item = self.data_table.item(row, 1)
                if value_item and addr_item and value_item.text() and addr_item.text():
                    data.append((int(value_item.text()), int(addr_item.text())))

            # Reset and load data
            self.ias = IAS_arch()
            self.ias.load_data(data, instructions)
            
            # Execute
            self.output_console.clear()
            self.output_console.append("Starting execution...\n")
            self.ias.fetch()
            
            # Update output
            for log in self.ias.execution_log:
                self.output_console.append(log)
            self.output_console.append("\nExecution completed.")
            
            # Update registers
            self.update_register_display()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def clear_all(self):
        self.instruction_editor.clear()
        self.data_table.clearContents()
        self.output_console.clear()
        self.register_display.clear()
        self.ias = IAS_arch()
        self.update_register_display()

    def create_help_button(self):
        help_button = QPushButton("Help")
        help_button.clicked.connect(self.show_help)
        help_button.setMaximumWidth(100)  # Adjust width as needed
        self.statusBar().addWidget(help_button)  # Add to the status bar


    def update_register_display(self):
        register_text = f"""
Program Counter (PC): {self.ias.PC}
Memory Address Register (MAR): {self.ias.MAR}
Memory Buffer Register (MBR): {self.ias.MBR}
Accumulator (AC): {self.ias.AC}
Multiplier Quotient (MQ): {self.ias.MQ}
Instruction Buffer Register (IBR): {self.ias.IBR}
Instruction Register (IR): {self.ias.IR}
"""
        self.register_display.setText(register_text)
    def show_help(self):
        help_text = f""" 
        IAS Architecture Simulator Help
        
        Warning:
        -Use data and memory wisely
        -the max data entry is set to 500 by default so it 
         would be good if you start your data addresses from
         500 (i.e. 500-999) with this the max instructions
         you can write is 999 (with the 1000th as HALT ).
        -Keep in mind the above setting is only if you
         have 500 data entries else you can manage the 
         storage as you like.

        Instructions Format:
        - Enter one instruction per line
        - Format: INSTRUCTION ADDRESS
        - Example: LOAD 100
        - In case of LSH and RSH instructions enter them as:
          LSH 0  OR RSH 0

        Available Instructions:
        ins. to be entered |      original ins.     | opcode
        ----------------------------------------------------
               HALT        |         HALT           |  0x00
               LOAD        |      LOAD M(X)         |  0x01
               LOAD-       |      LOAD -M(X)        |  0x02
               LOAD|       |     LOAD |M(X)|        |  0x03
               LOAD|-      |     LOAD -|M(X)|       |  0x04
               ADD         |     ADD M(X)           |  0x05
               SUB         |     SUB M(X)           |  0x06
               ADD|        |     ADD |M(X)|         |  0x07
               SUB|        |     SUB |M(X)|         |  0x08
               LOADMQM     |     LOAD MQ,M(X)       |  0x09
               LOADMQ      |     LOAD MQ            |  0x0A
               MUL         |     MUL M(X)           |  0x0B
               DIV         |     DIV M(X)           |  0x0C
               JUMPL       |     JUMP M(X,0:19)     |  0x0D
               JUMPR       |     JUMP M(X,20:39)    |  0x0E
               JUMPL+      |     JUMP+ M(X,0:19)    |  0x0F
               JUMPR+      |     JUMP+ M(X,20:39)   |  0x10
               STORL       |     STOR M(X,8:19)     |  0x12
               STORR       |     STOR M(X,28:39)    |  0x13
               LSH         |     LSH                |  0x14
               RSH         |     RSH                |  0x15
               STOR        |     STOR M(X)          |  0x21

        Data Entry:
        - Enter values and addresses in the data table
        - Values are integers
        - Addresses must be within memory range (0-999)

        Tips:
        - Clear button resets all inputs and memory
        - Register values are updated after each execution
        - Check the output console for execution details
        """

        dialog = QDialog(self)
        dialog.setWindowTitle("Help")
        dialog.resize(600, 500)  # Set width and height

        layout = QVBoxLayout()

        text_edit = QTextEdit()
        text_edit.setText(help_text)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Courier", 10))  # Monospaced font for better formatting
        text_edit.setMinimumSize(680, 680)  # Ensure it fits well inside dialog

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)

        layout.addWidget(text_edit)
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec_()



def main():
    app = QApplication(sys.argv)
    window = IASSimulatorGUI()
    window.show()
    sys.exit(app.exec_())


main()
