from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import random


class ApplicationWindow(QtWidgets.QWidget):
    """
    Class representing the main Application window.

    Attributes
    ----------

    Methods
    ---------
    
    """

    GRID_SIZE = 20
    NUMBER_OF_MINES = 40
    M = 0

    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.setGeometry(0, 0, 600, 400)
        self.setWindowTitle('MineSweeper')
        
        self.top_menu = TopMenu()
        self.grid = Grid(self.GRID_SIZE, self.NUMBER_OF_MINES)

        self.layout = QtWidgets.QVBoxLayout()

        self.grid_wrapper = QtWidgets.QHBoxLayout()
        self.grid_wrapper.addStretch(1)
        self.grid_wrapper.addWidget(self.grid)
        self.grid_wrapper.addStretch(1)


        self.layout.addWidget(self.top_menu)
        self.layout.addLayout(self.grid_wrapper)
        self.setLayout(self.layout)



class TopMenu(QtWidgets.QWidget):
    """
    Class representing the top menu for placing timer and mines left info.

    Attributes
    ----------

    Methods
    ---------
    
    """

    def __init__(self):
        super(TopMenu, self).__init__()
        self.menu_layout = QtWidgets.QHBoxLayout()
        self.menu_layout.setAlignment(QtCore.Qt.AlignTop)

        self.time_passed_label = QtWidgets.QLabel('Time passed:')
        self.time_img = QtWidgets.QLabel('TIME')       
        self.mines_left_label = QtWidgets.QLabel('Mines marked:')
        self.mines_left_edit = QtWidgets.QLabel('N-')

        self.menu_layout.addWidget(self.time_passed_label)
        self.menu_layout.addWidget(self.time_img)
        self.menu_layout.addWidget(self.mines_left_label)
        self.menu_layout.addWidget(self.mines_left_edit)
        self.setLayout(self.menu_layout)

    def update_mine_count(self, count):
        self.mines_left_edit.setText('N = {}'.format(count))


class Grid(QtWidgets.QWidget):
    """
    Class representing the grid for placing buttons in.

    Attributes
    ----------
    size : int
        defines the size of the grid

    Methods
    ---------
    create_grid():
        Create a grid of given size using QPushButtons.
    create_mines():
        Create mines at random positions into already existing grid
    check_neighbours():
        Check neighbouring buttons of a mine, increase their value by one
    uncover():
        Uncover all zeroes in neighbourhood
    """

    def __init__(self, size, mines):
        super(Grid, self).__init__()
        self.size = size    # integer
        self.mines = mines
        self.grid_layout = QtWidgets.QGridLayout()   
        self.grid_layout.setSpacing(0)
        self.create_grid()
        self.create_mines()
        self.check_neighbours()    
        self.setLayout(self.grid_layout)

    def create_grid(self):
        """Creates a grid of given size using QPushButtons"""
        for row in range(self.size):
            for col in range(self.size):
                self.grid_button = Button(state='unclicked', is_mine=False, value=0)
                self.grid_button.clicked.connect(self.grid_button.left_button_clicked)
                self.grid_button.clicked.connect(lambda _, r=row, c=col: self.uncover(r, c))
                self.grid_button.setFixedSize(30, 30)
                self.grid_button.setStyleSheet('background-color : rgba(0, 0, 0, 100); border :1px solid rgba(0, 0, 0, 150)')
                self.grid_layout.addWidget(self.grid_button, row, col)

    def create_mines(self):
        """Creates mines at random positions into already existing grid"""
        random_positions = random.sample(range(0, self.size*self.size), self.mines)
        for position in random_positions:
            self.grid_layout.itemAt(position).widget().is_mine = True

    def check_neighbours(self):
        """Check neighbouring buttons of a mine, increase their value by one"""
        for row in range(self.size):
            for col in range(self.size):
                if self.grid_layout.itemAtPosition(row, col).widget().is_mine:
                    neighbour_list = [self.grid_layout.itemAtPosition(row-1, col-1), self.grid_layout.itemAtPosition(row-1, col),
                                      self.grid_layout.itemAtPosition(row-1, col+1), self.grid_layout.itemAtPosition(row, col+1),
                                      self.grid_layout.itemAtPosition(row, col-1), self.grid_layout.itemAtPosition(row+1, col-1),
                                      self.grid_layout.itemAtPosition(row+1, col), self.grid_layout.itemAtPosition(row+1, col+1)]
                    for widget in neighbour_list:
                        try:
                            widget.widget().value += 1
                        except AttributeError:
                            pass
    
    def uncover(self, row, col):
        """Uncover all zeroes in neighbourhood"""
        btn = self.grid_layout.itemAtPosition(row, col).widget()
        if btn.value == 0 and btn.state=='clicked':
                    coords = [[row-1, col], [row, col+1], [row+1, col], [row, col-1]] # UP RIGHT DOWN LEFT
                    orthogonal_neighbours = [self.grid_layout.itemAtPosition(coords[0][0], coords[0][1]), self.grid_layout.itemAtPosition(coords[1][0], coords[1][1]),
                                             self.grid_layout.itemAtPosition(coords[2][0], coords[2][1]), self.grid_layout.itemAtPosition(coords[3][0], coords[3][1])]
                    for widget, coord in zip(orthogonal_neighbours, coords):
                        try:
                            if widget.widget().value == 0 and widget.widget().state == 'unclicked':
                                widget.widget().left_button_clicked()
                                self.uncover(coord[0], coord[1])
                        except AttributeError:
                            pass


class Button(QtWidgets.QPushButton):
    """
    Class representing a button in the grid.

    Attributes
    ----------
    state : str
        defines if the button is clicked or not
    is_mine : boolean
        defines if the button is a mine or not
    value : int
        defines how many mines are in the neighbourhood of this button

    Methods
    ---------
    mousepressEvent():
        Override to include both left and right clicks
    left_button_clicked():
        Specifies what happens after a button is clicked depending on its state and if it is a mine or not
    """
    MINES_MARKED = 0

    def __init__(self, state, is_mine, value):
        super(Button, self).__init__()
        self.state = state     
        self.is_mine = is_mine
        self.value = value
        self.installEventFilter(self)
    
    def eventFilter(self, QObject, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.RightButton:
                self.right_button_clicked()
        return False
        
    def left_button_clicked(self):
        """Specificies what happens if button is clicked depending on its state and if it is a mine or not"""
        if self.state == 'unclicked' or self.state == 'flagged':
            if self.is_mine:
                self.setIcon(QtGui.QIcon('C:\\Users\\Martin\\projects\\minesweeper\\images\\mine.png'))
                self.setIconSize(QtCore.QSize(25,25))  
                self.setStyleSheet('background-color : white; border :1px solid rgba(0, 0, 0, 50)')
                self.state = 'clicked'
            else:
                self.setIcon(QtGui.QIcon())
                self.setStyleSheet('background-color : rgba(0, 0, 0, 0); border :1px solid rgba(0, 0, 0, 50)')
                self.setText('{}'.format(self.value))
                self.state = 'clicked'
        else:
            pass

    def right_button_clicked(self):
        """Do action when right mouse click is pressed"""
        if self.state == 'unclicked':
            self.state = 'flagged'
            self.setIcon(QtGui.QIcon('C:\\Users\\Martin\\projects\\minesweeper\\images\\flag.png'))
            self.setIconSize(QtCore.QSize(25,25))   
            # TODO: Get this number to top menu edit 
            ApplicationWindow.M += 1
            print(ApplicationWindow.M)  

        elif self.state == 'flagged':
            self.state = 'unclicked'
            self.setIcon(QtGui.QIcon())
            # TODO: what happens when you unflag - reduce the number of marked

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = ApplicationWindow()
    window.show()
    sys.exit(app.exec())
