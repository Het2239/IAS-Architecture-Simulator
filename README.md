# IAS Architecture Simulator

A Python-based graphical simulator for the IAS (Institute for Advanced Study) computer architecture, featuring a PyQt5 GUI interface for interactive learning and experimentation.

## Overview

The IAS Architecture Simulator provides a visual and interactive way to understand and work with the IAS computer architecture. It simulates the fundamental components of the IAS machine, including its registers, memory system, and instruction set.

## Features

- Full implementation of the IAS instruction set
- Interactive GUI with multiple panels:
  - Instruction input editor
  - Data memory table
  - Memory viewer
  - Execution output console
  - Register status display
- Real-time memory inspection
- Register state monitoring
- Step-by-step execution logging
- Comprehensive help system

## Requirements

- Python 3.x
- PyQt5

## Installation

1. Ensure Python 3.x is installed on your system
2. Install PyQt5 using pip:
   ```bash
   pip install PyQt5
   ```
3. Clone or download the source code
4. Run the main script:
   ```bash
   python IAS.py
   ```

## Usage

### Main Interface

The simulator interface is divided into three main panels:

1. Left Panel:
   - Assembly instruction input
   - Data memory table

2. Center Panel:
   - Memory viewer
   - Address input for memory inspection

3. Right Panel:
   - Control buttons (Run, Clear)
   - Execution output console
   - Register status display

### Instruction Format

Enter instructions one per line using the following format:
```
INSTRUCTION ADDRESS
```
Example:
```
LOAD 100
ADD 101
STOR 102
```

### Supported Instructions

| Instruction | Description | Opcode |
|-------------|-------------|---------|
| HALT        | Halt execution | 0x00 |
| LOAD        | Load M(X) | 0x01 |
| LOAD-       | Load -M(X) | 0x02 |
| LOAD\|      | Load \|M(X)\| | 0x03 |
| LOAD\|-     | Load -\|M(X)\| | 0x04 |
| ADD         | Add M(X) | 0x05 |
| SUB         | Subtract M(X) | 0x06 |
| ADD\|       | Add \|M(X)\| | 0x07 |
| SUB\|       | Subtract \|M(X)\| | 0x08 |
| LOADMQM     | Load MQ,M(X) | 0x09 |
| LOADMQ      | Load MQ | 0x0A |
| MUL         | Multiply M(X) | 0x0B |
| DIV         | Divide M(X) | 0x0C |
| JUMPL       | Jump M(X,0:19) | 0x0D |
| JUMPR       | Jump M(X,20:39) | 0x0E |
| JUMPL+      | Jump+ M(X,0:19) | 0x0F |
| JUMPR+      | Jump+ M(X,20:39) | 0x10 |
| STORL       | Store M(X,8:19) | 0x12 |
| STORR       | Store M(X,28:39) | 0x13 |
| LSH         | Left Shift | 0x14 |
| RSH         | Right Shift | 0x15 |
| STOR        | Store M(X) | 0x21 |

### Memory Management

- Total memory size: 1000 locations (0-999)
- Default data entry limit: 500 entries
- Recommended data address range: 500-999
- Maximum instruction count: 999 (with 1000th as HALT)

### Important Notes

1. For LSH and RSH instructions, use:
   ```
   LSH 0
   RSH 0
   ```

2. Memory Usage Guidelines:
   - Use data addresses wisely to avoid conflicts with instruction storage
   - When using maximum data entries (500), start data addresses from 500
   - Adjust storage management based on actual data entry count

## Architecture Components

The simulator implements the following IAS components:

- PC (Program Counter)
- MAR (Memory Address Register)
- MBR (Memory Buffer Register)
- AC (Accumulator)
- MQ (Multiplier Quotient)
- IBR (Instruction Buffer Register)
- IR (Instruction Register)
- Memory (1000 locations)

## Error Handling

The simulator includes comprehensive error checking for:
- Invalid memory addresses
- Incorrect instruction formats
- Division by zero
- Out-of-range memory access

## Contributing

Contributions to improve the simulator are welcome. Please ensure to:
1. Follow the existing code style
2. Add comments for new functionality
3. Update the help documentation as needed
4. Test thoroughly before submitting changes

## License

This project is available for educational and research purposes. Please provide appropriate attribution when using or modifying the code.
