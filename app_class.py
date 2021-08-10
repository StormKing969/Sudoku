import sys
from settings import *
from buttons import *


##### HELPER FUNCTIONS #####

def drawGrid(window):
    pygame.draw.rect(window, BLACK, (gridPos[0], gridPos[1], WIDTH - 150, HEIGHT - 150), 2)
    for x in range(9):
        pygame.draw.line(window, BLACK, (gridPos[0] + (x * cellSize), gridPos[1]),
                         (gridPos[0] + (x * cellSize), gridPos[1] + 450), 2 if x % 3 == 0 else 1)
        pygame.draw.line(window, BLACK, (gridPos[0], gridPos[1] + (x * cellSize)),
                         (gridPos[0] + 450, gridPos[1] + (x * cellSize)), 2 if x % 3 == 0 else 1)


def drawSelection(window, pos):
    pygame.draw.rect(window, LIGHTBLUE,
                     ((pos[0] * cellSize) + gridPos[0], (pos[1] * cellSize) + gridPos[1], cellSize, cellSize))


def shadeLockedCells(window, locked):
    for cell in locked:
        pygame.draw.rect(window, LOCKEDCELLCOLOR, (cell[0] * cellSize + gridPos[0], cell[1] * cellSize + gridPos[1],
                                                   cellSize, cellSize))


def shadeIncorrectCells(window, incorrect):
    for cell in incorrect:
        pygame.draw.rect(window, INCORRECTCELLCOLOR, (cell[0] * cellSize + gridPos[0], cell[1] * cellSize + gridPos[1],
                                                      cellSize, cellSize))


def isInt(string):
    try:
        int(string)
        return True
    except:
        return False


class App:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.running = True
        self.grid = testBorder1
        self.selected = None
        self.mousePos = None
        self.state = "playing"
        self.finished = False
        self.cellChanged = False
        self.playingButtons = []
        self.menuButtons = []
        self.endButtons = []
        self.lockedCells = []
        self.incorrectCells = []
        self.font = pygame.font.SysFont("arial", int(cellSize / 2))
        self.load()

    def run(self):
        while self.running:
            if self.state == "playing":
                self.playing_events()
                self.playing_update()
                self.playing_draw()

        pygame.quit()
        sys.exit()

    ##### PLAYING STATE #####

    def playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # User's Mouse Click
            if event.type == pygame.MOUSEBUTTONDOWN:
                selected = self.mouseOnGrid()
                if selected:
                    self.selected = selected
                else:
                    self.selected = None

            # User Input
            if event.type == pygame.KEYDOWN:
                if self.selected is not None and self.selected not in self.lockedCells:
                    if isInt(event.unicode):
                        # Cell Changed
                        self.grid[self.selected[1]][self.selected[0]] = int(event.unicode)
                        self.cellChanged = True

    def playing_update(self):
        self.mousePos = pygame.mouse.get_pos()
        for button in self.playingButtons:
            button.update(self.mousePos)

        if self.cellChanged:
            self.incorrectCells = []
            if self.allCellsDone():
                # Corrects The Board
                self.checkAllCells()
                if len(self.incorrectCells) == 0:
                    print("YOU WON")

    def playing_draw(self):
        self.window.fill(WHITE)

        for button in self.playingButtons:
            button.draw(self.window)

        if self.selected:
            drawSelection(self.window, self.selected)

        shadeLockedCells(self.window, self.lockedCells)

        shadeIncorrectCells(self.window, self.incorrectCells)

        self.drawNumbers(self.window)

        drawGrid(self.window)
        pygame.display.update()
        self.cellChanged = False

    def mouseOnGrid(self):
        if self.mousePos[0] < gridPos[0] or self.mousePos[1] < gridPos[1]:
            return False
        if self.mousePos[0] > gridPos[0] + gridSize or self.mousePos[1] > gridPos[1] + gridSize:
            return False
        return (self.mousePos[0] - gridPos[0]) // cellSize, (self.mousePos[1] - gridPos[1]) // cellSize

    def loadButtons(self):
        self.playingButtons.append(Button(20, 40, 100, 40))

    def textToScreen(self, window, text, pos):
        font = self.font.render(text, False, BLACK)
        fontWidth = font.get_width()
        fontHeight = font.get_height()
        pos[0] += (cellSize - fontWidth) // 2
        pos[1] += (cellSize - fontHeight) // 2
        window.blit(font, pos)

    def drawNumbers(self, window):
        for y_index, row in enumerate(self.grid):
            for x_index, num in enumerate(row):
                if num != 0:
                    pos = [(x_index * cellSize) + gridPos[0], (y_index * cellSize) + gridPos[1]]
                    self.textToScreen(window, str(num), pos)

    ##### ORIGINAL BOARD NUMBER #####

    def load(self):
        self.loadButtons()
        for y_index, row in enumerate(self.grid):
            for x_index, num in enumerate(row):
                if num != 0:
                    self.lockedCells.append([x_index, y_index])

    ##### BOARD CORRECTION #####

    def allCellsDone(self):
        for row in self.grid:
            for num in row:
                if num == 0:
                    return False
        return True

    def checkAllCells(self):
        self.checkRows()
        self.checkColumns()
        self.checkSmallBoxes()

    def checkSmallBoxes(self):
        for x in range(3):
            for y in range(3):
                possibleNumber = [1, 2, 3, 4, 5, 6, 7, 8, 9]
                for i in range(3):
                    for j in range(3):
                        x_index = x * 3 + i
                        y_index = y * 3 + j
                        if self.grid[y_index][x_index] in possibleNumber:
                            possibleNumber.remove(self.grid[y_index][x_index])
                        else:
                            if [x_index, y_index] not in self.lockedCells and [x_index,
                                                                               y_index] not in self.incorrectCells:
                                self.incorrectCells.append([x_index, y_index])
                            if [x_index, y_index] in self.lockedCells:
                                for k in range(3):
                                    for l in range(3):
                                        x_index2 = x * 3 + k
                                        y_index2 = y * 3 + l
                                        if self.grid[y_index2][x_index2] == self.grid[y_index][x_index] and [x_index2,
                                                                                                             y_index2] \
                                                not in self.lockedCells:
                                            self.incorrectCells.append([x_index2, y_index2])

    def checkRows(self):
        for y_index, row in enumerate(self.grid):
            possibleNumber = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            for x_index in range(9):
                if self.grid[y_index][x_index] in possibleNumber:
                    possibleNumber.remove(self.grid[y_index][x_index])
                else:
                    if [x_index, y_index] not in self.lockedCells and [x_index, y_index] not in self.incorrectCells:
                        self.incorrectCells.append([x_index, y_index])
                    if [x_index, y_index] in self.lockedCells:
                        for k in range(9):
                            if self.grid[y_index][k] == self.grid[y_index][x_index] and [k,
                                                                                         y_index] not in self.lockedCells:
                                self.incorrectCells.append([k, y_index])

    def checkColumns(self):
        for x_index in range(9):
            possibleNumber = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            for y_index, row in enumerate(self.grid):
                if self.grid[y_index][x_index] in possibleNumber:
                    possibleNumber.remove(self.grid[y_index][x_index])
                else:
                    if [x_index, y_index] not in self.lockedCells and [x_index, y_index] not in self.incorrectCells:
                        self.incorrectCells.append([x_index, y_index])
                    if [x_index, y_index] in self.lockedCells:
                        for k, row in enumerate(self.grid):
                            if self.grid[k][x_index] == self.grid[y_index][x_index] and [x_index,
                                                                                         k] not in self.lockedCells:
                                self.incorrectCells.append([x_index, k])
