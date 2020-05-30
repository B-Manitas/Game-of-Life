"""
It's an application used to create a simulation of Conway's Game of Life.
This Python script contains two Class : - Cell : Create new cell.
                                        - MainApplication : It's the main window of the application 
                                          where all the cells are managed.

Packages used:
    - Ctypes
    - Itertools
    - Numpy
    - PyQt5
"""

__author__ = ("Manitas Bahri")
__date__ = "2020/03"

try:
    import ctypes
    import itertools
    import numpy as np
    
    from PyQt5 import QtCore, QtGui, QtWidgets, uic
    from PyQt5.QtCore import Qt
    
    import sys

except ImportError as e_import:
    ctypes.windll.user32.MessageBoxW(0, f"Error: {e_import}.\nCan't import necessary modules. \
                                          Please check if modules are installed correctly.", 
                                          "Module Import Error")
    print("ImportError", e_import)
    sys.exit()


class Cell(QtWidgets.QWidget):
    """
    Create new cell.
    
    Args: 
        - state_cell (int): 1 or 0 to represent whether the cell is alive or no.
    """
    def __init__(self, state_cell:int):
        super().__init__()
        self.is_alive = state_cell

        # Check if the cell is alive and changes the color.
        if self.is_alive == 0:
            self.state_color = QtGui.QColor(255, 255, 255)
        elif self.is_alive == 1:
            self.state_color = QtGui.QColor(235, 84, 84)

    def dead(self):
        """The cell dies."""
        self.is_alive = 0
        self.state_color = QtGui.QColor(255, 255, 255)
        self.update()
    
    def born(self):
        """The cell born."""
        self.is_alive = 1
        self.state_color = QtGui.QColor(235, 84, 84)
        self.update()
    
    def paintEvent(self, event):
        """Draw a rectangle that represents the cell."""
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(Qt.gray, 1))
        painter.setBrush(self.state_color)
        painter.drawRect(0, 0, 30, 30)
    
    def mousePressEvent(self, event):
        """When the user clicks on the cell, changes the state of the cell."""
        if self.is_alive == 0:
            self.born()
        
        elif self.is_alive == 1:
            self.dead()
            

class MainApplication(QtWidgets.QWidget):
    """
    It's the main window of the application where all the cells are managed.
    
    Args:
        - size_window (int): The size of the application window in pixels.
        - interval_update (int): The time between to update of the world.
        - percentage_alive (int): The percentage of cell life.
        - n (int): The number of boxes in a row and a column.
    """
    def __init__(self, size_window:int=500, interval_update:int=50, percentage_alive:int=20, n:int=50):
        super().__init__()
        
        self.size_window = size_window
        self.interval_update = interval_update
        self.percentage_alive = percentage_alive
        self.n = n

        self.pause = True
        self.cells = np.array([])
        self.state_cells = [0, 1]
        self.state_world = self.random_world()
        
        self.init_ui()

    def init_ui(self):
        """Create User Interface"""
        self.setWindowTitle("Game of Life")
        self.setFixedSize(self.size_window, self.size_window)

        # Create the tools layout at the top of the window.
        self.tools_layout = QtWidgets.QGridLayout()
        
        # Create buttons.
        self.btn_random = QtWidgets.QPushButton("Random")
        self.btn_start_pause = QtWidgets.QPushButton("Start")
        self.btn_clean = QtWidgets.QPushButton("Clean")

        # Create a slider to get the percentage of living cells.
        txt_prob_alive = "Probability of living cells : {}%".format(self.percentage_alive)
        self.lbl_prob_alive = QtWidgets.QLabel(txt_prob_alive)
        self.sldr_prob_alive = QtWidgets.QSlider(Qt.Horizontal)
        self.sldr_prob_alive.setMinimum(0)
        self.sldr_prob_alive.setMaximum(100)
        self.sldr_prob_alive.setTickInterval(10)
        self.sldr_prob_alive.setValue(self.percentage_alive)
        
        # Connect button and slider.
        self.btn_random.clicked.connect(self.new_world)
        self.btn_start_pause.clicked.connect(self.start_pause)
        self.btn_clean.clicked.connect(self.clean_world)
        self.sldr_prob_alive.valueChanged.connect(self.change_value)

        # Add widgets to the tools layout.
        self.tools_layout.addWidget(self.btn_random, 0, 0)
        self.tools_layout.addWidget(self.btn_start_pause, 0, 1)
        self.tools_layout.addWidget(self.btn_clean, 0, 2)
        
        self.tools_layout.addWidget(self.lbl_prob_alive, 0, 3)
        self.tools_layout.addWidget(self.sldr_prob_alive, 0, 4)

        # Create a grid layout where in each box creates a new cell.
        self.board_layout = QtWidgets.QGridLayout()
        self.board_layout.setSpacing(0)
        self.grid = [(i, j) for i in range(self.n) for j in range(self.n)]
        for position in self.grid:
            self.cell = Cell(self.state_world[position])
            self.board_layout.addWidget(self.cell, *position)
            self.cells = np.append(self.cells, self.cell)

        self.cells = self.cells.reshape(self.n, self.n)

        # Add child layout to main layout.
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.tools_layout)
        self.main_layout.addLayout(self.board_layout)
        self.setLayout(self.main_layout)

    def change_value(self, value):
        """
        Changes the percentage of alive cells.
        
        Args:
            - value (float): the new percentage value.
        """
        self.percentage_alive = value
        self.lbl_prob_alive.setText("Probability of living cells : {}%".format(self.percentage_alive))

    def evolution(self):
        """Create a new world and apply the GoL rules to return the state of the world to the next generation."""
        new_state_world = self.state_world.copy()
        
        for r, c in itertools.product(range(self.n), range(self.n)):
                # Count living neighbors to the cell.
                neighbors = int(self.state_world[r][(c-1)%self.n] + self.state_world[(r-1)%self.n][c] + 
                                self.state_world[r][(c+1)%self.n] + self.state_world[(r+1)%self.n][c] +
                                self.state_world[(r+1)%self.n][(c+1)%self.n] + self.state_world[(r-1)%self.n][(c-1)%self.n] +
                                self.state_world[(r-1)%self.n][(c+1)%self.n] + self.state_world[(r+1)%self.n][(c-1)%self.n])
                
                # Apply rules Conway's Game of Life.
                if self.state_world[r][c] == 1:
                    if (neighbors < 2) or (neighbors > 3):
                        new_state_world[r][c] = 0
                
                elif self.state_world[r][c] == 0:
                    if neighbors == 3:
                        new_state_world[r][c] = 1
        
        return new_state_world

    def update_world(self):
        """
        To update the state of the world.
        Firstly, check if user has changed state of cell. Then, calculate the state of the next generation,
        And finaly, change the state of each cell.
        """
        self.state_world = self.check_state_cell()
        self.state_world = self.evolution()
        self.change_state_cell()
    
    def random_world(self):
        """Return random array of 0 and 1 where 1 represents the living cell."""
        self.prob_alive = self.percentage_alive / 100
        return np.random.choice(self.state_cells, size=self.n*self.n, 
                                p=[1-self.prob_alive, self.prob_alive]).reshape(self.n, self.n)

    def new_world(self):
        """Uses to create new random world."""
        self.state_world = self.random_world()
        self.change_state_cell()
    
    def clean_world(self):
        """Clean the world, all cells die and all boxes became white."""
        if self.pause == False:
            self.start_pause()

        self.state_world = np.zeros((self.n, self.n))
        self.change_state_cell()

    def check_state_cell(self):
        """Checks if user has changed the state of cell."""
        check_state = np.array([])
        
        # Create new array with the state of each cell.
        for r, c in itertools.product(range(self.n), range(self.n)):
            check_state = np.append(check_state, self.cells[r][c].is_alive)
        
        return check_state.reshape(self.n, self.n)

    def change_state_cell(self):
        """Change the state of each cell."""
        for r, c in itertools.product(range(self.n), range(self.n)):
            # The cell die or born.
            if self.state_world[r][c] == 0:
                self.cells[r][c].dead()
            
            elif self.state_world[r][c] == 1:
                self.cells[r][c].born()

    def start_pause(self):
        """Uses to start and stop world evolution."""
        if self.pause == True:
            self.btn_start_pause.setText("Pause")

            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.update_world)
            self.timer.start(self.interval_update)
            
            self.pause = False
        
        else:
            self.btn_start_pause.setText("Start")
            self.timer.stop()
            self.pause = True


if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = MainApplication()
        window.show()
        app.exec_() 
    
    except TypeError as e_type:
        ctypes.windll.user32.MessageBoxW(0, f"Error: {e_type}. Please check if the type of parameter are correct.", 
                                            "Type Error")
        print("TypeError :", e_type)

    except OSError as e_os:
        ctypes.windll.user32.MessageBoxW(0, f"Error: {e_os}.", "Os Error")
        print("OSError :", e_os)
    
    except Exception as e:
        ctypes.windll.user32.MessageBoxW(0, f"Error: {e}.", "Error")
        print("Error :", e)