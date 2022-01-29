import random
import time


class MyExceptions(Exception):
    pass


class MaxIterException(MyExceptions):
    """An exception for a maximum number of iterations"""

    def __init__(self, limit):
        self.limit = limit

    def __str__(self):
        return str(f"A maximum number of iterations {self.limit} has been reached.")


class TileBusyException(MyExceptions):
    def __str__(self):
        return str("The tile is occupied")


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
        self.dot_list = self.dots()

    def dots(self):
        """Returns a list of the ship's coordinates in tuples"""
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
            raise ValueError(f"{health_} value is not correct")


class Board:
    @staticmethod
    def print(*args):
        """Prints out both fields in a row."""
        boards_list = args

        def column(boards):
            boards_ = boards
            y = 0
            while True:
                error_check = row_of_rows(boards_, y)
                if error_check == 1:
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
                    space(board)
                    print('      ', end='')
                else:
                    row(board, y_)
                    print('      ', end='')
            print('\n', end='')
            if error_count >= len(boards):
                return 1

        def space(board):
            print(f'      ', end='')
            for i in range(board.size):
                print('    ', end='')

        def head(boards):
            print(' ')
            for b in boards:
                print(' ' * (b.size * 2) + f'{b.name}' + ' ' * (b.size * 2) + '', end='')

            print('\n')

        def row(board, y):
            if y == 0:
                print('      ', end='')
                for n in range(board.size):
                    print(f' {n + 1}  ', end='') if n < 9 else print(f'{n + 1}  ', end='')
                return

            print('  %2d ' % (y), end='')
            """0 - empty, 1 - ship, 2 - hit, 3 - destroyed, 4 - miss"""
            for x in range(board.size):
                if board.matrix[y - 1][x] == 0:
                    print('  ~ ', end='')
                if board.matrix[y - 1][x] == 1 and (board.hid == 0):
                    print('  ■ ', end='')
                if board.matrix[y - 1][x] == 1 and (board.hid == 1):
                    print('  ~ ', end='')
                if board.matrix[y - 1][x] == 2:
                    print('  □ ', end='')
                if board.matrix[y - 1][x] == 3:
                    print('  X ', end='')
                if board.matrix[y - 1][x] == 4:
                    print('  O ', end='')
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

    def out(self, dot):
        return dot.x < 1 or dot.x > self.size or dot.y < 1 or dot.y > self.size

    def add_ship(self, ship: Ship):
        """Attempts to put the ship dots in the matrix and adds them into self.non_empty list if successful."""
        dots = ship.dots()
        for coord in dots:
            dot = Dot(coord)
            if dot in self.non_empty or self.out(dot):
                raise TileBusyException

        self.non_empty += ship.dots()
        for coord in dots:
            dot = Dot(coord)
            self.matrix[dot.y - 1][dot.x - 1] = 1

    def contour(self, ship):
        """Adds the cells surrounding the ship into self.non_empty list"""
        for tuple_ in ship.dots():
            d = Dot(tuple_)
            con_list = [(d.x - 1, d.y - 1), (d.x, d.y - 1), (d.x + 1, d.y - 1), (d.x - 1, d.y), (d.x + 1, d.y),
                        (d.x - 1, d.y + 1), (d.x, d.y + 1), (d.x + 1, d.y + 1)]
            for n in con_list:
                con_dot = Dot(n)
                if (con_dot.t() not in self.non_empty) and (con_dot.x <= self.size) and (con_dot.y <= self.size):
                    self.non_empty.append(con_dot.t())

    def strike(self, dot):
        """Checks if the strike coordinates match any ship tile, adds the result into the matrix, and returns it"""
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
                    for d in ship.dots():
                        self.matrix[d[1] - 1][d[0] - 1] = destroyed
                    self.ship_list.remove(ship)
                    print(f"The ship has been destroyed!")
                    return destroyed

        self.matrix[dot.y - 1][dot.x - 1] = miss
        print("Miss")
        return miss


class Player:
    def __init__(self, player_board, enemy_board, name):
        self.name = name
        self.enemy_board = enemy_board
        self.player_board = player_board

    def win_check(self):
        for n in range(7):
            if len(self.enemy_board.ship_list) == 0:
                print(f"{self.name} wins!")
                return True

    def ask(self):
        pass

    def move(self):
        print(f"{self.name}'s turn...")
        time.sleep(1)

        result = self.enemy_board.strike(self.ask())
        return result


class User(Player):
    def __init__(self, player_board, enemy_board, name):
        self.name = name
        self.enemy_board = enemy_board
        self.player_board = player_board
        self.turns_list = []

    def ask(self):
        while True:
            dot = input("Enter coordinates for a strike (x y): ").split(" ")
            time.sleep(1)
            try:
                dot = Dot(tuple(map(int, dot)))
                if self.enemy_board.out(dot):
                    print("Coordinates are outside of the board.")
                    continue
                if dot in self.turns_list:
                    print("You have already fired at these coordinates.")
                    continue
                self.turns_list.append(dot)
                return dot
            except ValueError:
                print("Incorrect coordinates.")
                continue

        time.sleep(1)
        print(f"User is firing at {dot}..")
        time.sleep(1)
        return dot


class AI(Player):
    def __init__(self, player_board, enemy_board, name):
        self.name = name
        self.enemy_board = enemy_board
        self.player_board = player_board
        self.turns_list = []

    def ask(self):
        x = random.randrange(1, self.player_board.size + 1)
        y = random.randrange(1, self.player_board.size + 1)
        dot = Dot(x, y)
        while dot in self.turns_list:
            x = random.randrange(1, self.player_board.size + 1)
            y = random.randrange(1, self.player_board.size + 1)
            dot = Dot(x, y)
        self.turns_list.append(dot)
        print(f"AI is firing at {dot}..")
        time.sleep(1)
        return dot


class Game:

    def __init__(self):
        self.ai_board = self.random_board(6, 1, "AI's board")
        self.user_board = self.random_board(6, 0, "User's board")
        self.user = User(self.user_board, self.ai_board, "User")
        self.ai = AI(self.ai_board, self.user_board, "AI")

    def random_board(self, size, hid, name):
        """Generates random ships, a board, and trying to place the ships onto the board"""

        ship_x11 = ship_x12 = ship_x13 = ship_x14 = ship_x21 = ship_x22 = ship_x3 = None
        ship_names = [ship_x11, ship_x12, ship_x13, ship_x14, ship_x21, ship_x22, ship_x3]

        board = Board(size, hid, name)
        length = [1, 1, 1, 1, 2, 2, 3]
        loop_count = 0
        ship_count = 0

        while len(length) != ship_count:

            try:
                if loop_count == 1000:
                    raise MaxIterException(1000)
            except MaxIterException:
                length = [1, 1, 1, 1, 2, 2, 3]
                board = Board(size, hid, name)
                print(f"A maximum number of iterations ({loop_count}) has been reached while generating the "
                      f"boards. Trying again..")
                loop_count = 0
                ship_count = 0
                continue
            else:
                x = random.randrange(1, size + 1)
                y = random.randrange(1, size + 1)
                direction = random.choice(("vertical", "horizontal"))
                ship = Ship(length[-1 - ship_count], (x, y), direction)
                try:
                    board.add_ship(ship)

                except TileBusyException:
                    loop_count += 1
                    continue
                else:
                    ship_count += 1
                    ship_names[-ship_count] = ship
                    board.ship_list.append(ship_names[-ship_count])
                    board.contour(ship)

        return board

    def greet(self):
        print(f'\nWelcome to Battleship! The game will be going against AI on a {self.user_board.size}x'
              f'{self.ai_board.size} field. \nDuring your turn, enter the coordinates of your strike in a '
              f'"x y" format.')

    def start(self):
        game.greet()
        game.loop()

    def loop(self):
        win = False
        while True:
            Board.print(self.user_board, self.ai_board, )
            while True:
                result = self.user.move()
                time.sleep(1)
                Board.print(self.user_board, self.ai_board, )
                time.sleep(1)
                win = self.user.win_check()
                if win or (result == 4):  # 4 - miss
                    break
            if win:
                break

            while True:
                result = self.ai.move()
                time.sleep(1)
                win = self.ai.win_check()
                if win or (result == 4):  # 4 - miss
                    break
            if win:
                break
#            time.sleep(1)


game = Game()
game.start()
