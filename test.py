import random
import time


class Error(Exception):
    pass


class MaxIterError(Error):

    def __init__(self, limit):
        self.limit = limit

    def __str__(self):
        return str(f"A maximum number of iterations {self.limit} has been reached.")


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


class Ship:
    def __init__(self, length, bow, direction):
        self.health = length
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

    def get_health(self):
        return self.health

    def set_health(self, health_):
        if 1 <= health_ <= 3:
            self.health = health_
        else:
            raise ValueError("health_ value is not correct")


class Board:
    @staticmethod
    def print(*args):
        boards_list = args

        def column(boards):
            boards_ = boards
            y = 0
            while True:
                check = row_of_rows(boards_, y)
                if check == 1:
                    break
                y += 1

        def row_of_rows(boards, y):
            error_count = 0

            y_ = y
            for board in boards:
                try:
                    board.matrix[y - 1][0]
                except IndexError:
                    error_count += 1
                else:
                    row(board, y_)
                    print('      ', end='')
            print('\n', end='')
            if error_count >= len(boards):
                return 1

        def head(boards):
            print(' ')
            for b in boards:
                print(f'            {b.name}            ', end='')
            print('\n')

        def row(board, y):
            if y == 0:
                print('      ', end='')
                for n in range(board.size):
                    print(f' {n + 1}  ', end='')
                return

            print(f'  {y}  ', end='')

            for x in range(board.size):
                if board.matrix[y - 1][x] == 0:
                    print('  □ ', end='')
                if board.matrix[y - 1][x] == 1 and (board.hid == 0):
                    print('  ■ ', end='')
                if board.matrix[y - 1][x] == 1 and (board.hid == 1):
                    print('  □ ', end='')
                if board.matrix[y - 1][x] == 2:
                    print('  H ', end='')
                if board.matrix[y - 1][x] == 3:
                    print('  D ', end='')
                if board.matrix[y - 1][x] == 4:
                    print('  - ', end='')
            print(' ', end='')

        head(boards_list)
        column(boards_list)

    def __init__(self, size, hid, name):
        self.hid = hid
        self.size = size
        self.matrix = [[0 for n in range(self.size)] for m in range(self.size)]
        self.ship_list = []
        self.non_empty = []
        self.name = name

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

    def strike(self, dot):
        hit, destroyed, miss = 2, 3, 4
        for ship in self.ship_list:

            if dot in ship.dots():

                if ship.health != 1:
                    self.matrix[dot.y - 1][dot.x - 1] = hit
                    hp = ship.get_health()
                    ship.set_health(hp - 1)
                    print("Hit")
                    return hit
                else:
                    self.matrix[dot.y - 1][dot.x - 1] = destroyed
                    self.ship_list.remove(ship)
                    print(f"A ship has been destroyed!")
                    return destroyed

        self.matrix[dot.y - 1][dot.x - 1] = miss
        print("Miss")
        return miss


class Player:
    def __init__(self, player_board, enemy_board):
        self.enemy_board = enemy_board
        self.player_board = player_board
        self.win = None

    def ask(self):
        pass

    def move(self):
        for n in range(7):
            if len(self.enemy_board.ship_list) == 0:
                print("win")
        result = self.enemy_board.strike(self.ask())
        return result


class User(Player):
    def __init__(self, player_board, enemy_board):
        super().__init__(player_board, enemy_board)
        self.enemy_board = enemy_board
        self.player_board = player_board

    def ask(self):
        dot = input("Enter coordinates for a strike (x y): ").split(" ")
        while len(dot) != 2 and not all([dot[0].isdigit(), dot[1].isdigit()]):
            dot = input("Enter coordinates for a strike (x y): ").split(" ")
        dot = Dot(tuple(map(int, dot)))
        print(f"User is firing at {dot}..")
        return dot


class AI(Player):
    def __init__(self, player_board, enemy_board):
        self.enemy_board = enemy_board
        self.player_board = player_board

    def ask(self):
        x = random.randrange(1, self.player_board.size + 1)
        y = random.randrange(1, self.player_board.size + 1)
        dot = Dot(x, y)
        #  hits, misses = [], []
        #  hit_count = 0
        print(f"AI is firing at {dot}..")
        return dot
        #  misses.append(dot)


class Game:

    def __init__(self):

        self.ai_board = self.random_board(6, 1, "AI's board")
        self.user_board = self.random_board(6, 0, "User's board")
        self.user = User(self.user_board, self.ai_board)
        self.ai = AI(self.ai_board, self.user_board)
        self.size_ = 6

    def random_board(self, size, hid, name):
        """Generating random ships and placing them on the board"""

        ship_x11 = ship_x12 = ship_x13 = ship_x14 = ship_x21 = ship_x22 = ship_x3 = None
        ship_names = [ship_x11, ship_x12, ship_x13, ship_x14, ship_x21, ship_x22, ship_x3]

        board = Board(size, hid, name)
        length = [1, 1, 1, 1, 2, 2, 3]
        loop_count = 0
        ship_count = 0

        while len(length) != ship_count:

            try:
                if loop_count == 1000:
                    raise MaxIterError(1000)
            except MaxIterError:
                length = [1, 1, 1, 1, 2, 2, 3]
                board = Board(size, hid, name)
                print(f"A maximum number of iterations ({loop_count}) has been reached. Trying again..")
                loop_count = 0
                ship_count = 0
                continue
            else:
                x = random.randrange(1, 7)
                y = random.randrange(1, 7)
                direction = random.choice(("vertical", "horizontal"))
                ship = Ship(length[-1 - ship_count], (x, y), direction)
                if board.add_ship(ship) == 1:
                    loop_count += 1
                    continue
                else:
                    ship_count += 1
                    ship_names[-ship_count] = ship
                    board.ship_list.append(ship_names[-ship_count])
                    board.non_empty += ship.dots()
                    board.contour(ship)

        return board

    def greet(self):
        print('')
        print(f'Welcome to Battleship! The game will be going against AI on a {game.size_}x{game.size_} '
              f'field. \nDuring your turn, enter the coordinates of your strike in a "x y" format.')

    def start(self):
        game.greet()
        game.loop()

    def loop(self):
        Board.print(self.user_board, self.ai_board, )

        while True:
            while self.user.move() != 4:  # 4 - miss
                Board.print(self.user_board, self.ai_board, )
            Board.print(self.user_board, self.ai_board, )
            while self.ai.move() != 4:  # 4 - miss
                time.sleep(3)
                Board.print(self.user_board, self.ai_board, )
                time.sleep(3)
            Board.print(self.user_board, self.ai_board, )


game = Game()
game.start()
