import random
import os.path
from queue import Queue


class MinesweeperField:
    def __init__(self, size_x=None, size_y=None, mines=None, file_name=None):
        if file_name is None:
            self.size_x = size_x  # lines
            self.size_y = size_y  # columns
            self.mines = mines
        else:
            # loading data from file
            f = open(file_name + '.ms', 'rb')
            self.size_x = int(f.readline())  # lines
            self.size_y = int(f.readline())  # columns
            self.mines = int(f.readline())

        self.main_field = [[0 for _ in range(self.size_y)] for _ in range(self.size_x)]
        self.__is_opened__ = [[0 for _ in range(self.size_y)] for _ in range(self.size_x)]
        # __is_opened__[x][y] = 1 if player has opened (x; y)
        # __is_opened__[x][y] = 2 if player has put flag in (x; y)

        self.mines_left = self.mines  # how many mines left
        self.total_flags = 0  # player wins only if mines == total_flags

        if file_name is None:
            self.__create_mines__()
        else:
            self.__load_mines__(f)
            self.__load_opened__(f)
            f.close()

    def __create_mines__(self):
        # shifts for updating numbers on the field
        dx_coords = [-1, -1, -1, 0, 1, 1, 1, 0]
        dy_coords = [1, 0, -1, -1, -1, 0, 1, 1]

        # creating mines
        for _ in range(self.mines):
            x = random.randint(0, self.size_x - 1)
            y = random.randint(0, self.size_y - 1)
            while self.main_field[x][y] == '*':
                x = random.randint(0, self.size_x - 1)
                y = random.randint(0, self.size_y - 1)
            self.main_field[x][y] = '*'

            # updating the numbers on the field
            for i in range(len(dx_coords)):
                dx = dx_coords[i]
                dy = dy_coords[i]
                if 0 <= x + dx < self.size_x and 0 <= y + dy < self.size_y and self.main_field[x + dx][y + dy] != '*':
                    self.main_field[x + dx][y + dy] += 1

    def __load_mines__(self, file):
        # shifts for updating numbers on the field
        dx_coords = [-1, -1, -1, 0, 1, 1, 1, 0]
        dy_coords = [1, 0, -1, -1, -1, 0, 1, 1]

        for _ in range(self.mines):
            cur_mine_x = int(file.readline())
            cur_mine_y = int(file.readline())
            self.main_field[cur_mine_x][cur_mine_y] = '*'

            # updating the numbers on the field
            for i in range(len(dx_coords)):
                dx = dx_coords[i]
                dy = dy_coords[i]
                if 0 <= cur_mine_x + dx < self.size_x and 0 <= cur_mine_y + dy < self.size_y \
                        and self.main_field[cur_mine_x + dx][cur_mine_y + dy] != '*':
                    self.main_field[cur_mine_x + dx][cur_mine_y + dy] += 1

    def __load_opened__(self, file):
        """
        Loads __is_opened__ matrix from the file
        """
        for i in range(self.size_x):
            for j in range(self.size_y):
                self.__is_opened__[i][j] = int(file.readline())
                if self.__is_opened__[i][j] == 2:  # there's a flag
                    self.total_flags += 1
                    if self.main_field[i][j] == '*':  # there's a mine under the flag
                        self.mines_left -= 1

    def show(self, mode=None):
        """
        Prints the field. Only opened points are visible for player
        If mode = "all" then all points will be visible for player
        """
        # printing a coordinate axis (letters)
        print(' ' * 3, '| ', end='')
        for i in range(ord('A'), ord('A') + self.size_y):
            print(chr(i), end=' ')
        print()
        print('-' * (self.size_y * 2 + 5))

        for i in range(self.size_x):
            # printing a coordinate axis (number)
            print("{:>3} | ".format(i + 1), end='')
            for j in range(self.size_y):
                if self.__is_opened__[i][j] != 0 or mode == 'all':
                    if self.__is_opened__[i][j] == 2:
                        print('F', end=' ')
                    else:
                        print(self.main_field[i][j], end=' ')
                else:
                    print('X', end=' ')
            print()

    def is_opened(self, x, y):
        """
        Checks if (x; y) is already opened
        """
        if self.__is_opened__[x][y] == 1:
            return True
        else:
            return False

    def open(self, x, y):
        """
        Opens (x; y).
        Returns True if a point was opened correctly.
        Returns False if there were a mine.
        """
        if self.main_field[x][y] == '*':
            return False
        if self.__is_opened__[x][y] == 2:
            self.total_flags -= 1

        self.__is_opened__[x][y] = 1

        # player picked an empty point (without any mines nearby) -> we should open adjacent empty points and
        # points without mines
        if self.main_field[x][y] == 0:
            self.bfs(x, y)
        return True

    def bfs(self, x, y):
        """
        Marks all adjacent free points as opened with BFS
        """
        # shifts for field traversal
        dx_coords = [-1, 0, 1, 0]
        dy_coords = [0, -1, 0, 1]

        q = Queue()
        q.put((x, y))
        visited = [[0 for _ in range(self.size_y)] for _ in range(self.size_x)]
        visited[x][y] = 1

        while not(q.empty()):
            cur_x, cur_y = q.get()
            for i in range(len(dx_coords)):
                dx = dx_coords[i]
                dy = dy_coords[i]
                new_x = cur_x + dx
                new_y = cur_y + dy
                if 0 <= new_x < self.size_x and 0 <= new_y < self.size_y \
                        and self.main_field[new_x][new_y] != '*' and visited[new_x][new_y] == 0:
                    visited[new_x][new_y] = 1
                    self.__is_opened__[new_x][new_y] = 1
                    if self.main_field[new_x][new_y] == 0:
                        q.put((new_x, new_y))

    def put_flag(self, x, y):
        """
        Puts flag in (x; y) or removes flag if it was put before.
        Returns True if all mines were covered with flags (player has won)
        Returns False if there are still some mines to find
        """
        if self.__is_opened__[x][y] == 2:
            # there was a flag -> removing it
            self.__is_opened__[x][y] = 0
            self.total_flags -= 1
            if self.main_field[x][y] == '*':
                self.mines_left += 1
        elif self.__is_opened__[x][y] == 0:
            # there were no flags -> putting it
            self.__is_opened__[x][y] = 2
            self.total_flags += 1

            if self.main_field[x][y] == '*':
                self.mines_left -= 1

        if self.mines_left == 0 and self.total_flags == self.mines:
            return True
        else:
            return False

    def save(self, file):
        f = open(file + '.ms', 'wb')

        # writing sizes of our field and amount of mines
        f.write((str(self.size_x) + '\n').encode())
        f.write((str(self.size_y) + '\n').encode())
        f.write((str(self.mines) + '\n').encode())

        # writing the coordinates of mines
        for i in range(self.size_x):
            for j in range(self.size_y):
                if self.main_field[i][j] == '*':
                    f.write((str(i) + '\n').encode())
                    f.write((str(j) + '\n').encode())

        # writing the info about opened cells and flags (__is_opened__)
        for i in range(self.size_x):
            for j in range(self.size_y):
                f.write((str(self.__is_opened__[i][j]) + '\n').encode())

        f.close()


def print_menu():
    print("1. Start a game")
    print("2. Load a game")
    print("3. Open instructions")
    print("0. Exit")


def print_rules():
    print("Welcome to console minesweeper - a classic game but in the console!")
    print("The rules are the same as in the original game - you have to find all mines and mark them with a flag.")
    print("You can open any cell. If there's no mine, then you'll see the amount of mines in 3x3 square around cell.")
    print("If there're no mines in 3x3 square, then I'll open the nearest cells with some numbers inside.")
    print("If you pick a cell with a mine, then you'll be blown up.. I'm sorry.")
    print("To open a cell use a command like: X Y open (where X and Y are the cell's coordinates written in any order.)")
    print("If you want to mark a cell with a flag, type in a command like: X Y flag.")
    print("You can remove your flag from the cell by using the same command.")
    print("Note, that you have to put exactly as many flags as the amount of mines in the field.")
    print("You can save a game and come back to it later. Just use 'save' command and think of the name for a save.")
    print("You can return to the main menu by typing 'menu' command.")
    print("I hope you'll have a great time! May the luck be with you!")
    print("Made by Ilya Moiseenkov aka mosik for Tinkoff DL course entrance exam.")


def check_step(player_step, cur_field):
    """
    Checks if user's step is correct
    """
    if len(player_step) != 3:
        return False

    x = player_step[0]
    y = player_step[1]
    action = player_step[2]

    if x.isalpha() and y.isnumeric():
        x, y = int(y), x
    elif x.isnumeric() and y.isalpha():
        x = int(x)
    else:
        return False

    # X is number, Y is letter
    if len(y) != 1:
        return False

    if not(ord('A') <= ord(y.upper()) < ord('A') + cur_field.size_y and 1 <= x <= cur_field.size_x):
        return False
    if action.lower() != "open" and action.lower() != "flag":
        return False
    return True


def check_sizes(sizes):
    """
    Checks if sizes of field are entered correctly
    Returns True if everything is correct, returns False otherwise
    """
    if len(sizes) != 2:
        return False
    if not (str(sizes[0]).isnumeric() and str(sizes[1]).isnumeric()):
        return False
    else:
        size_x, size_y = int(sizes[0]), int(sizes[1])
        if not (3 <= size_x <= 26 and 3 <= size_y <= 26):
            return False
    return True


def check_mines(mines, sizes):
    """
    sizes = (size_x, size_y)
    Checks if amount of mines is entered correctly
    Returns True if everything is correct, returns False otherwise
    """
    if not (str(mines).isnumeric()):
        return False
    mines = int(mines)
    if not (2 <= mines <= sizes[0] * sizes[1] // 3):
        return False
    return True


if __name__ == '__main__':
    print("Hello, player! Welcome to minesweeper!")
    print("Choose an option: ")
    print_menu()
    print()

    is_game_preloaded = False

    request = '1'
    while request != '0':
        if is_game_preloaded:
            # player has loaded the game and is ready to start
            request = '1'
        else:
            request = input(">>> ")

        if request == '0':  # Exiting
            print("See you soon!")
            break

        elif request == '1':  # Starting a game
            if not is_game_preloaded:
                size_x = 0
                size_y = 0
                sizes = ()
                while not check_sizes(sizes):
                    print("Enter the lengths of the field's sides (two numbers between 3 and 26 in one line)")
                    sizes = input(">>> ").split()
                    if not check_sizes(sizes):
                        print("Incorrect input! Try again.")
                    else:
                        size_x, size_y = int(sizes[0]), int(sizes[1])

                mines = ''
                while not check_mines(mines, (size_x, size_y)):
                    print("Enter the amount of mines (two numbers between 2 and {})".format(size_x * size_y // 3))
                    mines = input(">>> ")
                    if check_mines(mines, (size_x, size_y)):
                        mines = int(mines)

                field = MinesweeperField(size_x, size_y, mines)


            print("Enter your steps like [X Y Action], where X, Y - coords, Action = 'Open' or 'Flag'")
            print("Example: 2 A Open or B 10 Flag")
            print("You can save the game. Just type in 'Save'")
            print("Type 'Menu' to return to main menu")
            if is_game_preloaded:
                print("Total mines:", field.mines)
            print()

            is_game_preloaded = False  # now there's no difference if the game was preloaded or not

            is_game_finished = False
            while not is_game_finished:
                field.show()
                step = input(">>> ").split()
                if len(step) == 1 and step[0].lower() == 'save':
                    print("Enter the name for this save")
                    file_name = input(">>> ")
                    field.save(file_name)
                    print("Game saved!")
                    continue

                if len(step) == 1 and step[0].lower() == 'menu':
                    break

                while not(check_step(step, field)):
                    print("Incorrect input! Try again.")
                    step = input(">>> ").split()

                cur_x, cur_y, cur_action = step[0], step[1], step[2].lower()
                if cur_x.isalpha() and cur_y.isnumeric():
                    cur_x, cur_y = int(cur_y), cur_x
                else:
                    cur_x = int(cur_x)

                # X is number, Y is letter
                cur_x -= 1
                cur_y = int(ord(cur_y.upper()) - ord('A'))

                if field.is_opened(cur_x, cur_y):
                    print("This point was already opened")

                if cur_action == 'open':
                    result = field.open(cur_x, cur_y)
                    if not result:
                        is_game_finished = True
                        field.show(mode='all')
                        print("You have picked a mine! Game over!")

                elif cur_action == 'flag':
                    result = field.put_flag(cur_x, cur_y)
                    if result:
                        is_game_finished = True
                        field.show()
                        print("You have found all mines! Congratulations!")
            print_menu()

        elif request == '2':  # loading the game
            print("Enter the name of the save")
            save = input(">>> ")
            if not(os.path.exists(save + '.ms')):
                print("There's no such save. Try another one.")
                print_menu()
            else:
                field = MinesweeperField(file_name=save)
                is_game_preloaded = True

        elif request == '3':  # print rules
            print_rules()
            print()
            print_menu()
        else:
            print("Incorrect input! Try again.")
