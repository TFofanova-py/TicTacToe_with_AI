import itertools
import random
import copy
import numpy as np


class Game:
    states = ('X wins', 'O wins', 'Draw', 'Game not finished')

    def __init__(self, plr_1, plr_2):
        self.state = 'Game not finished'
        self.field = Field([['_', '_', '_'], ['_', '_', '_'], ['_', '_', '_']])
        self.turn = plr_1
        self.players = (plr_1, plr_2)

    def change_turn(self):
        if self.turn == self.players[0]:
            self.turn = self.players[1]
        else:
            self.turn = self.players[0]

    def play_turn(self, plyr):
        self.print_action()
        plyr.move(self.field.field)
        self.field.put_on_field(plyr.move_cells, self.turn.symbol)
        self.state = self.field.get_state()
        self.change_turn()

    def print_action(self):
        if type(self.turn) == User:
            print("Enter the coordinates:")
        if type(self.turn) == Easy:
            print('Making move level "easy"')
        if type(self.turn) == Medium:
            print('Making move level "medium"')
        if type(self.turn) == Hard:
            print('Making move level "hard"')


class Field:
    states = ('X wins', 'O wins', 'Draw', 'Game not finished')

    def __init__(self, fld_list):
        self.field = copy.deepcopy(fld_list)
        self.state = None

    def print_field(self):
        print('---------')
        for row in self.field:
            print('|', row[0], row[1], row[2], '|')
        print('---------')

    def put_on_field(self, coordinates, smb):
        x = coordinates[0]
        y = coordinates[1]
        self.field[3 - y][x - 1] = smb

    def get_state(self):
        if any(['_' in row for row in self.field]):
            result = self.states[3]  # game not finished
        else:
            result = self.states[2]  # draw

        rows = self.field
        columns = [[self.field[i][j] for i in range(3)] for j in range(3)]
        diagonals = [[self.field[i][i] for i in range(3)], [self.field[i][2 - i] for i in range(3)]]
        for line in itertools.chain(rows, columns, diagonals):
            if line.count('X') == 3:
                result = self.states[0]  # X wins
                break
            if line.count('O') == 3:
                result = self.states[1]  # O wins
                break
        return result


class Player:
    symbol = ''
    move_cells = ()

    def __init__(self, smb):
        self.symbol = smb

    def get_opponent(self):
        if self.symbol == 'X':
            return 'O'
        return 'X'


class User(Player):
    def move(self, game_field):
        movement = input()
        while not self.check_move(game_field, movement):
            movement = input()
        self.move_cells = [int(x) for x in movement.split()]

    def check_move(self, game_field, move_str):
        try:
            x, y = [int(x) for x in move_str.split()]
        except ValueError:
            print("You should enter numbers!")
        else:
            if not 0 <= x <= 3 or not 0 <= y <= 3:
                print("Coordinates should be from 1 to 3!")
                return False
            if game_field[3 - y][x - 1] is not '_':
                print("This cell is occupied! Choose another one!")
                return False
            return True
        return False


class Easy(Player):
    def avail_cells(self, game_field):
        empty_cells = []
        for i, row in enumerate(game_field):
            empty_cells += [(j + 1, 3 - i) for j in range(len(row)) if row[j] == '_']
        return empty_cells

    def move(self, game_field):
        self.move_cells = list(random.choice(self.avail_cells(game_field)))


class Medium(Easy):
    def check_positions(self, game_field, smb):
        avail_cells = self.avail_cells(game_field)
        for cell in avail_cells:
            temp_field = Field(game_field)
            temp_field.put_on_field(cell, smb)
            if temp_field.get_state() in temp_field.states[:2]:
                return cell
        return None

    def move(self, game_field):
        if self.check_positions(game_field, self.symbol) is not None:  # win_cell exists
            self.move_cells = self.check_positions(game_field, self.symbol)
        elif self.check_positions(game_field, self.get_opponent()) is not None:  # loss_cell exists
            self.move_cells = self.check_positions(game_field, self.get_opponent())
        else:
            super().move(game_field)


class Hard(Medium):
    def move(self, game_field):
        ind = self.calc_values(game_field, self.symbol)[1]
        self.move_cells = self.avail_cells(game_field)[ind]

    def calc_values(self, game_field, smb):
        avail_cells = self.avail_cells(game_field)
        values = []
        for cell in avail_cells:
            temp_field = Field(game_field)
            temp_field.put_on_field(cell, smb)
            state = temp_field.get_state()
            if state in temp_field.states[:2]:
                if self.symbol == smb:
                    return (10, 0)
                else:
                    return (-10, 0)
            elif state == temp_field.states[2]:
                return (0, 0)
            else:
                next_smb = lambda x: 'X' if x == 'O' else 'O'
                value = self.calc_values(temp_field.field, next_smb(smb))[0]
                values.append(value)
        if self.symbol == smb:
            return (max(values), int(np.argmax(values)))
        else:
            return (min(values), int(np.argmin(values)))


def input_command():
    command_dict = {'start': ('user', 'easy', 'medium', 'hard'), 'exit': ()}
    cmd_is_correct = False
    cmd_list = None
    while not cmd_is_correct:
        cmd_list = input("Input command: ").split()
        if len(cmd_list) > 0:
            cmd = cmd_list[0]
            if cmd in command_dict:
                if cmd == 'start' and len(cmd_list) == 3 \
                        and all(param in command_dict['start'] for param in cmd_list[1:]):
                    cmd_is_correct = True
                elif cmd == 'exit' and len(cmd_list) == 1:
                    cmd_is_correct = True
            if not cmd_is_correct:
                print('Bad parameters!')
    return cmd_list


def create_player(smb, plr_type):
    if plr_type == 'user':
        return User(smb)
    if plr_type == 'easy':
        return Easy(smb)
    if plr_type == 'medium':
        return Medium(smb)
    if plr_type == 'hard':
        return Hard(smb)


command = input_command()
if command[0] == 'start':
    plr_x = create_player('X', command[1])
    plr_o = create_player('O', command[2])
    game = Game(plr_x, plr_o)
    game.field.print_field()
    while game.state not in (game.states[:3]):  # finish game
        game.play_turn(game.turn)
        game.field.print_field()
        if game.state in (game.states[:3]):
            print(game.state)