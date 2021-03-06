import tkinter as tk
from PIL import Image, ImageTk

class Board:
    def __init__(self):
        # Window settings
        self.root = tk.Tk()
        self.root.resizable(0,0)
        self.root.title('Chess')
        # Size of window - 80% percent of least dimension of screen
        self.size = 8 * (min(self.root.winfo_screenheight(), self.root.winfo_screenwidth()) // 10)
        # Size of cells
        self.cellSize = self.size // 8
        self.canvas = tk.Canvas(width = self.size, height = self.size)
        self.canvas.pack()
        self.canvas.bind('<Button-1>',self.Click())
        self.root.bind('<Return>',self.NewGameEventHandler())
        # Label for showing message about result of game
        self.alert = None
        # Colors for cells background
        self.cellBg = ('bisque', 'brown')
        # Drawing Board
        self.drawBoard()
        # Global game vars
        self.Player1 = None
        self.Player2 = None
        self.Players = (0,1)
        self.ActivePlayer = None
        self.ActiveFigure = None
        # Starting first game
        self.NewGame()
        # Starting window process. Upd: to early to start mainloop. Firstly we need to render all objects
        #self.root.mainloop()
    
    # Draws all cells. Actually runs only 1 timer per program executing
    def drawBoard(self):
        for i in range(8):
            for j in range(8):
                x1 = self.cellSize * i
                y1 = self.cellSize * j
                x2 = x1 + self.cellSize
                y2 = y1 + self.cellSize
                self.canvas.create_rectangle(x1,y1,x2,y2,fill = self.cellBg[(i + j)%2])
    
    # Invokes, when user clicks on board
    def Click(self):
        def _Click(event):
            # Calculate position of clicked Cell
            i, j = self.GetCell(event.x, event.y)
            # If we cliced on one of Active Player's figures:
            if (i,j) in self.Players[self.ActivePlayer].figures:
                # If is previously selected figure - we need to unselect it
                if self.ActiveFigure:
                    self.Players[self.ActivePlayer].figures[self.ActiveFigure].Deactivate()
                # Activate selected figure
                self.Players[self.ActivePlayer].figures[(i,j)].Activate()
                self.ActiveFigure = (i,j)
            else:
                # So, we clicked on empty cell or cell, located by enemy
                # We can continue, only in case if some figure was selected
                if self.ActiveFigure:
                    # Here must be a logic which will define:
                    # If Active figure can make move to (i,j) position - then run next block, else return for exit from function
                    self.Players[self.ActivePlayer].figures[self.ActiveFigure].SetPosition(i, j)
                    # Change Active Player to opposite
                    self.ActivePlayer = abs(1 - self.ActivePlayer)
                    self.ActiveFigure = None
        return _Click
    
    # Logic for restarting or running first game
    def NewGame(self):
        # If first game happened - clean Board after it
        if self.Player1:
            self.Player1.CleanFigures()
            self.Player2.CleanFigures()
        self.Player1 = Player(self,0)
        self.Player2 = Player(self,1)
        self.Players = (self.Player1, self.Player2)
        self.ActivePlayer = 0
        self.ActiveFigure = None

    # Wrapper, event handler, that runs NewGame function, when Enter pressed
    def NewGameEventHandler(self):
        def _NewGame(event):
            self.NewGame()
        return _NewGame

    # Returns coordinates of cell by coordinates of cursor
    def GetCell(self,x,y):
        i = x // self.cellSize
        j = y // self.cellSize
        return i, j

class Player:
    def __init__(self, board, side):
        # I think it's better from OOP conceptions:
        # - Player plays on Board - so Player has Board field to comunicate with Board
        # - Figure belong to player - so Figure has Player field, and can comunicate with him
        # - Also Figure can communicate with Board - through Player.
        # In my opinion, such Ierarchy more natural
        self.side = side
        self.board = board
        self.figures = {}
        self.SetFigures()

    # Draws Player's Figures on Board.
    # Also it pushes figures to dictionary with keys whic is a coordinates
    # It will easy to acces to figure after clicking on Board
    def SetFigures(self):
        # Drawing Infantry, Calculating of j - fucking magic of boolean algebra
        j = 1 + 5 * (1 - self.side)
        # Cicle for X coordinate
        for i in range(8):
            self.figures[(i, j)] = Figure(self, 0, self.side, i, j)
        # Drawing Towers, Horses, Officers
        j = 7 * (1 - self.side)
        for i in range(3):
            self.figures[(i,j)] = Figure(self, i + 1, self.side, i, j)
            self.figures[(7 - i,j)] = Figure(self, i + 1, self.side, 7 - i, j)
        # Drawing of Queen
        self.figures[(3, j)] = Figure(self, 4, self.side, 3, j)
        # Drawing of King
        self.figures[(4, j)] = Figure(self, 5, self.side, 4, j)

    # Cleans all Players's Figures from Board
    def CleanFigures(self):
        for key, figure in self.figures.items():
            self.board.canvas.delete(figure.id)

class Figure:
    # Initializating of figure, it takes kind of figure and side, and coordinates on Board
    # Kind: { 0 - Infantry, 1 - Tower, 2 - Horse, 3 - Officer, 4 - Queen, 5 - King }
    # Side: 0 - White, 1 - Black. White - means, side which goes first
    def __init__(self, player, kind, side, x, y):
        self.player = player
        self.kind = kind
        self.side = side
        # Figure coordinates. It means cell coordinates, tot pixel
        self.x = x
        self.y = y
        # We need to store image, else garbage collector will clean it
        self.img = None
        # Id for canvas
        self.id = None
        self.Draw()

    def Draw(self):
        img = Image.open('resources/{}/{}.png'.format(self.side, self.kind))
        # Resizing, so it will fit for cell size on any screens
        size = self.player.board.cellSize
        img = img.resize((size,size), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(img)
        self.id = self.player.board.canvas.create_image(self.x * size,self.y * size,image = self.img, anchor=tk.NW)

    # Litle shifting, it indicates that this figure is active now
    def Activate(self, p=1):
        self.player.board.canvas.move(self.id, 0, p * (2 * self.player.side - 1) * (self.player.board.cellSize // 5))

    # Undoing of activating for activated figure
    def Deactivate(self):
        self.Activate(-1)

    # Change position from (self.x, self.y) to new (x,y)
    def SetPosition(self, x, y):
        cellSize = self.player.board.cellSize
        # Changing position on canvas
        self.player.board.canvas.coords(self.id, cellSize * x, cellSize * y)
        # Update dictionary of figures: create new key for this Figure and delete old one
        self.player.figures[(x,y)] = self
        del self.player.figures[(self.x, self.y)]
        # Update cooordinates
        self.x = x
        self.y = y

Board = Board()

# Since we didn't render all objects inside Board initializing
# And now we just testing - we need to run mainloop outside the Board class

#Board.Player2.figures[(0,0)].SetPosition(3,3)
Board.root.mainloop()