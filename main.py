import json
import random

import numpy as np
from PIL import Image

ISLAND_SIZE = 20


class Tile:
    def __init__(self, codeSides, img):

        self.codeSides = codeSides
        self.img = img
        self.size = self.img.size

    def show(self):
        bg = Image.new("RGBA", self.size, (255, 255, 255))

        bg.paste(self.img, (0, 0), self.img)

        bg.show()

    @staticmethod
    def fromFolder(tilePath):
        tileMap = []

        tilesData = {}

        with open(tilePath + "/tiles.json", "r") as read_file:
            tilesData = json.load(read_file)

        for tile in tilesData["tiles"]:
            codeSides = tile["codeSides"]
            img = Image.open(tilePath + "/" + tile["imgPath"])

            tileMap.append(Tile(codeSides, img))

            # generate variantes
            for var in tile["variantes"]:
                varCodeSides = []
                varImg = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
                varType, *opt = var.split("-")

                if varType == "rotation":
                    varCodeSides = [codeSides[(i - int(opt[0])) % 4] for i in range(4)]
                    varImg = img.rotate(-90 * int(opt[0]))

                    tileMap.append(Tile(varCodeSides, varImg))
        return tileMap


TILES = Tile.fromFolder("tiles")


class Case:
    def __init__(self, x, y, board):
        self.x = x
        self.y = y
        self.r = np.sqrt(x**2 + y**2)

        self.board = board

        self.defined = False

        self.tile = None

        self.entropy = len(TILES)

    def getPossibleTile(self):

        if self.defined:
            self.entropy = 0
            return []

        out = []

        neighbors = [
            self.board[self.x, self.y - 1],
            self.board[self.x + 1, self.y],
            self.board[self.x, self.y + 1],
            self.board[self.x - 1, self.y],
        ]

        for tile in TILES:
            valid = True
            for i in range(4):
                if neighbors[i].tile is not None:
                    valid = (
                        valid
                        and neighbors[i].tile.codeSides[(i + 2) % 4]
                        == tile.codeSides[i][::-1]
                    )

            if valid:
                out.append(tile)
        self.entropy = len(out)
        return out

    def define(self):
        tiles = self.getPossibleTile()
        # print(tiles[0].codeSides)
        # print([max(1, 5*tile.coeff(self.x, self.y, self.r)) for tile in tiles])
        self.tile = random.choices(tiles)[0]
        self.defined = True
        pass


class Board:
    def __init__(self, w, h):
        self.totalEntropy = w * h * 16

        self.width = w
        self.height = h

        self.tileSize = 32

        self.grid = [[Case(i, j, self) for i in range(w)] for j in range(h)]
        pass

    def __getitem__(self, key):
        if type(key) == int:
            return self.grid[key]
        elif type(key) == tuple and len(key) == 2:
            if (
                key[0] == -1
                or key[1] == -1
                or key[0] >= self.height
                or key[1] >= self.width
            ):
                case = Case(key[0], key[1], self)
                case.defined = True
                case.tile = TILES[0]
                return case
            else:
                return self.grid[key[1]][key[0]]

    def __setitem__(self, key, value):
        if type(key) == int:
            self.grid[key] = value
        elif type(key) == tuple and len(key) == 2:
            self.grid[key[1]][key[0]] = value

    def show(self):
        bg = Image.new(
            "RGBA",
            (self.tileSize * self.width, self.tileSize * self.height),
            (255, 122, 0),
        )

        for row in self.grid:
            for case in row:
                if case.defined:
                    bg.paste(
                        case.tile.img, (case.x * self.tileSize, case.y * self.tileSize)
                    )

        bg.show()

    def update(self):

        totalEntropy = 0
        for row in self.grid:
            for case in row:
                case.getPossibleTile()
                totalEntropy += case.entropy
        self.totalEntropy = totalEntropy

    def getCaseByEntropy(self):

        out = []

        self.update()

        for row in self.grid:
            for case in row:
                if not case.defined:
                    out.append(case)

        out.sort(key=lambda case: case.entropy)
        return out

    def getCaseByCenterDist(self):

        out = []

        self.update()

        for row in self.grid:
            for case in row:
                if not case.defined:
                    out.append(case)

        out.sort(key=lambda case: case.r)
        return out


b = Board(ISLAND_SIZE, ISLAND_SIZE)

while b.totalEntropy != 0:
    cases = b.getCaseByEntropy()

    # cases = b.getCaseByCenterDist()

    candidates = list(filter(lambda case: case.entropy == cases[0].entropy, cases))

    case = random.choice(candidates)
    case.define()

    b.update()

b.show()

# time.sleep(3)


# b.show()
