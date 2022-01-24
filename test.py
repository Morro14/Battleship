import random


class Error(Exception):
    pass


class MaxIterError(Error):

    def __init__(self, limit):
        self.limit = limit

    def __str__(self):
        return str(f"A maximum number of iterations {self.limit} has been reached. Trying again..")


class TileError(Error):
    def __init__(self):
        pass

    def __str__(self):
        return str("Tile is occupied")


class Dot:

    def __init__(self, *args):
        if type(args[0]) == tuple:
            self.x = args[0][0]
            self.y = args[0][1]
        else:
            self.x = args[0]
            self.y = args[1]

    def __str__(self):
        return str(f"({self.x}, {self.y})")

    def __eq__(self, other):
        if type(other) == tuple:
            return tuple((self.x, self.y)) == other
        return (self.x, self.y) == (other.x, other.y)

    def t(self):
        """Returns x, y as a tuple"""
        return tuple((self.x, self.y))

    def rand(self, size):
        self.x = random.randrange(1, size + 1)
        self.y = random.randrange(1, size + 1)


class Ship:
    def __init__(self, length, bow, direction, health):
        self.health = health
        self.direction = direction
        self.bow = bow
        self.length = length

    def dots(self):
        dots_list = [self.bow]
        if self.direction == "vertical":
            for i in range(1, self.length):
                dots_list.append((self.bow[0], self.bow[1] + i))
        if self.direction == "horizontal":
            for i in range(1, self.length):
                dots_list.append((self.bow[0] + i, self.bow[1]))
        return dots_list


class Board:

    def __init__(self, size):
        self.size = size
        self.matrix = [[0 for n in range(self.size)] for m in range(self.size)]
        self.ship_list = []
        self.non_empty = []

    def add_ship(self, ship: Ship):
        """Tries to put the ship in the matrix """
        dots = ship.dots()
        try:
            for coord in dots:
                dot = Dot(coord)
                if dot in self.non_empty:
                    raise TileError
                if self.matrix[dot.y - 1][dot.x - 1] is not None:
                    pass
        except IndexError:
            return 1
        except TileError:
            return 1
        else:
            for coord in dots:
                dot = Dot(coord)
                self.matrix[dot.y - 1][dot.x - 1] = 1

    def contour(self, ship):
        """Marks the cells surrounding the ship"""
        ship_dots = ship.dots()
        for i in range(ship.length):
            d = Dot(ship_dots[i][0], ship_dots[i][1])
            con_list = [(d.x - 1, d.y - 1), (d.x, d.y - 1), (d.x + 1, d.y - 1), (d.x - 1, d.y), (d.x + 1, d.y),
                        (d.x - 1, d.y + 1), (d.x, d.y + 1), (d.x + 1, d.y + 1)]
            for n in con_list:
                con_dot = Dot(n)
                if (con_dot.t() not in self.non_empty) and (con_dot.x <= self.size) and (con_dot.y <= self.size):
                    self.non_empty.append(con_dot.t())

    #                    self.matrix[con_dot.y - 1][con_dot.x - 1] = 2

    def print_field(self):
        """Prints out the matrix based on the "hid" parameter"""
        print('      ', end='')

        for n in range(self.size):
            print(f' {n + 1}  ', end='')
        print('\n', end='')
        for y in range(self.size):
            print(f'  {y + 1}  ', end='')
            for x in range(self.size):
                if self.matrix[y][x] == 0:
                    print('| ~ ', end='')
                if self.matrix[y][x] == 1:
                    print('| ∎ ', end='')
                if self.matrix[y][x] == 2:
                    print('| X ', end='')
            print('|', '\n', end='')

    def strike(self, dot):
        for n in range(self.ship_list):
            if dot in self.ship_list[n] and len(self.ship_list[n]) == 1:
                print("Destroyed")

            if dot in self.ship_list[n]:
                self.ship_list[n].remove(dot)
                return True

        return False


class Player:
    def __init__(self, player_board, enemy_board):
        self.enemy_board = enemy_board
        self.player_board = player_board

    def ask(self):
        pass

    def move(self):
        self.ask()
        if self.enemy_board.strike() == True:
            self.move()


class User(Player):
    def __init__(self):
        pass

    def ask(self):
        dot = Dot(tuple(input("Enter coordinates for a strike (x, y): ")))




class AI(Player):
    def __init__(self):
        pass

    def ask(self):
        n = random.randrange(1, self.player_board.size + 1)
        dot = Dot(random.randrange(n, n))
        hits, misses = [], []
        hit_count = 0

        misses.append(dot)

    def move(self):
        n = random.randrange(1, self.player_board.size + 1)
        dot = Dot(random.randrange(n, n))
        hits, misses = [], []
        hit_count = 0

        misses.append(dot)


class Game:

    def __init__(self) -> None:

        pass

    def random_board(self):
        """Generating random ships and placing them on the board"""
        board = Board(6)
        length = [1, 1, 1, 1, 2, 2, 3]
        loop_count = 0

        while len(length) != 0:
            try:
                if loop_count == 1000:
                    raise MaxIterError(1000)
            except MaxIterError:
                length = [1, 1, 1, 1, 2, 2, 3]
                board = Board(6)
                print(f"A maximum number of iterations ({loop_count}) has been reached. Trying again..")
                loop_count = 0
                continue
            else:
                x = random.randrange(1, 7)
                y = random.randrange(1, 7)
                direction = random.choice(("vertical", "horizontal"))
                ship = Ship(length[-1], (x, y), direction, length[-1])
                if board.add_ship(ship) == 1:
                    loop_count += 1
                    continue
                else:
                    board.non_empty += ship.dots()
                    board.contour(ship)
                    length.pop()
                    board.ship_list.append(ship.dots())
        print(board.print_field())


game = Game()
for i in range(20):
    game.random_board()
