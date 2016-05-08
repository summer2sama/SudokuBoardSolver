#!/usr/bin/env python
import struct, string, math
from copy import *
import time

class SudokuBoard:
    """This will be the sudoku board game object your player will manipulate."""

    def __init__(self, size, board):
      """the constructor for the SudokuBoard"""
      self.BoardSize = size #the size of the board
      self.CurrentGameBoard= board #the current state of the game board
      domain = set()
      for x in range(1, size + 1):
          domain.add(x)
      self.CurrentDomains = [ [ set(domain) for i in range(size) ] for j in range(size) ]

    def set_value(self, row, col, value):
        """This function will create a new sudoku board object with the input
        value placed on the GameBoard row and col are both zero-indexed"""

        #add the value to the appropriate position on the board
        self.CurrentGameBoard[row][col]=value
        #return a new board of the same size with the value added
        return SudokuBoard(self.BoardSize, self.CurrentGameBoard)


    def print_board(self):
        """Prints the current game board. Leaves unassigned spots blank."""
        div = int(math.sqrt(self.BoardSize))
        dash = ""
        space = ""
        line = "+"
        sep = "|"
        for i in range(div):
            dash += "----"
            space += "    "
        for i in range(div):
            line += dash + "+"
            sep += space + "|"
        for i in range(-1, self.BoardSize):
            if i != -1:
                print "|",
                for j in range(self.BoardSize):
                    if self.CurrentGameBoard[i][j] > 9:
                        print self.CurrentGameBoard[i][j],
                    elif self.CurrentGameBoard[i][j] > 0:
                        print "", self.CurrentGameBoard[i][j],
                    else:
                        print "  ",
                    if (j+1 != self.BoardSize):
                        if ((j+1)//div != j/div):
                            print "|",
                        else:
                            print "",
                    else:
                        print "|"
            if ((i+1)//div != i/div):
                print line
            else:
                print sep

    def backtracking(self, count, forward_checking = False, MRV = False, Degree = False,
        LCV = False):
        """Solve the Current Game Board Using Backtracking"""
        if is_complete(self):
            print "IS COMPLETED"
            return True, count
        #Using Heuristics for Picking up Variable
        if MRV or Degree:
            if MRV:
                i, j = self.MRV()
            if Degree:
                i, j = self.Degree()
            if self.CurrentGameBoard[i][j] == 0:#pick up variable
                if LCV:
                    values = self.LCV(i, j)
                else:
                    values = self.CurrentDomains[i][j]
                for v in values:
                    count += 1
                    print count
                    if self.is_consistent(i, j, v):
                        sudoku_board = fastcopy(self)
                        sudoku_board.set_value(i, j, v)
                        if forward_checking:
                            sudoku_board.do_forward_checking(i, j, v)
                        is_over, count = sudoku_board.backtracking(count, forward_checking, MRV, Degree, LCV)
                        if is_over:
                            self.CurrentGameBoard = sudoku_board.CurrentGameBoard
                            return is_over, count
                return False, count
        else:
            #Normal Order of Picking up Variable
            for i in range(self.BoardSize):
                for j in range(self.BoardSize):
                    if self.CurrentGameBoard[i][j] == 0:#pick up variable
                        if LCV:
                            values = self.LCV(i, j)
                        else:
                            values = self.CurrentDomains[i][j]
                        for v in values:
                            count += 1
                            print count
                            if self.is_consistent(i, j, v):
                                sudoku_board = fastcopy(self)
                                sudoku_board.set_value(i, j, v)
                                if forward_checking:
                                    sudoku_board.do_forward_checking(i, j, v)
                                is_over, count = sudoku_board.backtracking(count, forward_checking, MRV, Degree, LCV)
                                if is_over:
                                    self.CurrentGameBoard = sudoku_board.CurrentGameBoard
                                    return is_over, count
                        return False, count
        return False


    def is_consistent(self, row, col, v):
        """Decide if letting board[i][j] = v is consistent with CurrentGameBoard"""
        for i in range(self.BoardSize):
            if ((self.CurrentGameBoard[row][i] == v) and i != col):
                return False
            if ((self.CurrentGameBoard[i][col] == v) and i != row):
                return False
        subsquare = int(math.sqrt(self.BoardSize))
        SquareRow = row // subsquare
        SquareCol = col // subsquare
        for i in range(subsquare):
            for j in range(subsquare):
                if((self.CurrentGameBoard[SquareRow*subsquare+i][SquareCol*subsquare+j]
                        == v)
                    and (SquareRow*subsquare + i != row)
                    and (SquareCol*subsquare + j != col)):
                        return False
        return True

    def do_forward_checking(self, row, col, v):
        """Do Forward Checking After board[i][j] = v"""
        self.CurrentDomains[row][col].clear()
        for i in range(self.BoardSize):
            self.CurrentDomains[row][i].discard(v)
            self.CurrentDomains[i][col].discard(v)
        subsquare = int(math.sqrt(self.BoardSize))
        SquareRow = row // subsquare
        SquareCol = col // subsquare
        for i in range(subsquare):
            for j in range(subsquare):
                self.CurrentDomains[SquareRow*subsquare+i][SquareCol*subsquare+j].discard(v)

    def LCV(self, row, col):
        """Apply LCV Heuristic on [row][col]. Return an Array of Values in Corresponding Order."""
        value_constraints = []
        for v in self.CurrentDomains[row][col]:
            count = 0;
            for i in range(self.BoardSize):
                if((v in self.CurrentDomains[row][i]) and i != col):
                    count += 1
                if((v in self.CurrentDomains[i][col]) and i != row):
                    count += 1
            subsquare = int(math.sqrt(self.BoardSize))
            SquareRow = row // subsquare
            SquareCol = col // subsquare
            for i in range(subsquare):
                for j in range(subsquare):
                    if((v in self.CurrentDomains[SquareRow*subsquare+i][SquareCol*subsquare+j])
                        and (SquareRow*subsquare + i != row)
                        and (SquareCol*subsquare + j != col)):
                        count += 1
            value_constraints.append((v, count))
        value_constraints = sorted(value_constraints, key=lambda x: x[1])
        values = []
        for v, c in value_constraints:
            values.append(v)
        return values

    def MRV(self):
        """Apply MRV Heuristic on Current Board. Return an Array of Variable Index in Corresponding Order."""
        row = 0
        col = 0
        min_count = self.BoardSize * self.BoardSize + 1
        for i in range(self.BoardSize):
            for j in range(self.BoardSize):
                if self.CurrentGameBoard[i][j] == 0:
                    if len(self.CurrentDomains[i][j]) < min_count:
                        min_count = len(self.CurrentDomains[i][j])
                        row = i
                        col = j
        return row, col

    def Degree(self):
        """Apply Degree Heuristic on Current Board. Return an Array of Variable Index in Corresponding Order."""
        row_return = 0
        col_return = 0
        max_count = -1
        for row in range(self.BoardSize):
            for col in range(self.BoardSize):
                if self.CurrentGameBoard[row][col] == 0:
                    count = 0;
                    for k in range(self.BoardSize):
                        if(self.CurrentGameBoard[row][k] == 0 and k != col):
                            count += 1
                        if(self.CurrentGameBoard[k][col] == 0 and k != row):
                            count += 1
                    subsquare = int(math.sqrt(self.BoardSize))
                    SquareRow = row // subsquare
                    SquareCol = col // subsquare
                    for i in range(subsquare):
                        for j in range(subsquare):
                            if((self.CurrentGameBoard[SquareRow*subsquare+i][SquareCol*subsquare+j] == 0)
                                and (SquareRow*subsquare + i != row)
                                and (SquareCol*subsquare + j != col)):
                                count += 1
                    if count > max_count:
                        max_count = count
                        row_return = row
                        col_return = col
        return row_return, col_return

def fastcopy(sudoku_board):
    newboard = [[0 for x in range(sudoku_board.BoardSize)] for y in range(sudoku_board.BoardSize)]
    for i in range(sudoku_board.BoardSize):
        for j in range(sudoku_board.BoardSize):
            newboard[i][j] = sudoku_board.CurrentGameBoard[i][j]
    new_sudoku_board = SudokuBoard(sudoku_board.BoardSize, newboard)
    for i in range(new_sudoku_board.BoardSize):
        for j in range(new_sudoku_board.BoardSize):
            new_sudoku_board.CurrentDomains[i][j] = set(sudoku_board.CurrentDomains[i][j])
    return new_sudoku_board

def parse_file(filename):
    """Parses a sudoku text file into a BoardSize, and a 2d array which holds
    the value of each cell. Array elements holding a 0 are considered to be
    empty."""

    f = open(filename, 'r')
    BoardSize = int( f.readline())
    NumVals = int(f.readline())

    #initialize a blank board
    board= [ [ 0 for i in range(BoardSize) ] for j in range(BoardSize) ]

    #populate the board with initial values
    for i in range(NumVals):
        line = f.readline()
        chars = line.split()
        row = int(chars[0])
        col = int(chars[1])
        val = int(chars[2])
        board[row-1][col-1]=val

    return board

def is_complete(sudoku_board):
    """Takes in a sudoku board and tests to see if it has been filled in
    correctly."""
    BoardArray = sudoku_board.CurrentGameBoard
    size = len(BoardArray)
    subsquare = int(math.sqrt(size))

    #check each cell on the board for a 0, or if the value of the cell
    #is present elsewhere within the same row, column, or square
    for row in range(size):
        for col in range(size):
            if BoardArray[row][col]==0:
                return False
            for i in range(size):
                if ((BoardArray[row][i] == BoardArray[row][col]) and i != col):
                    return False
                if ((BoardArray[i][col] == BoardArray[row][col]) and i != row):
                    return False
            #determine which square the cell is in
            SquareRow = row // subsquare
            SquareCol = col // subsquare
            for i in range(subsquare):
                for j in range(subsquare):
                    if((BoardArray[SquareRow*subsquare+i][SquareCol*subsquare+j]
                            == BoardArray[row][col])
                        and (SquareRow*subsquare + i != row)
                        and (SquareCol*subsquare + j != col)):
                            return False
    return True

def init_board(file_name):
    """Creates a SudokuBoard object initialized with values from a text file"""
    board = parse_file(file_name)
    return SudokuBoard(len(board), board)

def solve(initial_board, forward_checking = False, MRV = False, Degree = False,
    LCV = False):
    """Takes an initial SudokuBoard and solves it using back tracking, and zero
    or more of the heuristics and constraint propagation methods (determined by
    arguments). Returns the resulting board solution. """
    if forward_checking:
        for i in range(initial_board.BoardSize):
            for j in range(initial_board.BoardSize):
                if initial_board.CurrentGameBoard[i][j] != 0:
                    initial_board.do_forward_checking(i, j, initial_board.CurrentGameBoard[i][j])

    t0 = time.clock()
    is_over, count = initial_board.backtracking(0, forward_checking, MRV, Degree, LCV)
    t1 = time.clock()
    print t1 - t0, "seconds to move"
    if is_over != True:
        print "Can't Find Solution Using Backtracking!"
        return initial_board
    #print "Your code will solve the initial_board here!"
    #print "Remember to return the final board (the SudokuBoard object)."
    #print "I'm simply returning initial_board for demonstration purposes."
    print "number of consistency checks utilized: "
    print count
    return initial_board
