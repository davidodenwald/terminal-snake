#!/usr/bin/python3
# Autor: David Odenwald, 08.05.14

import curses
import curses.textpad
import time
import random
import json
import datetime
import os

screen = curses.initscr()

curses.curs_set(0)
curses.noecho()
curses.cbreak()
screen.nodelay(1)
screen.border()
screen.keypad(1)
random.seed()

score_file = 'scores.json'

curses.start_color()
curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

window_height, window_width = screen.getmaxyx()

player_name = 'Player'
start_length = 4
grow_length = 1
speed = {'Normal': 0.1, 'Hard': 0.07, 'Extrem': 0.05}
difficulty = 'Normal'


def game():
    screen.clear()
    screen.nodelay(1)
    screen.border()

    head = [1, 1]
    body = [head[:]] * start_length
    deadcell = body[-1][:]

    gameover = False
    direction = 'right'
    foodmade = False

    while not gameover:
        while not foodmade:
            x_cord, y_cord = (random.randrange(1, window_width - 1),
                              random.randrange(1, window_height - 1))
            if screen.inch(y_cord, x_cord) == ord(' '):
                foodmade = True
                screen.addch(y_cord, x_cord, ord('@'))

        action = screen.getch()
        direction = change_direction(action, direction)

        if action == ord('q'):
            gameover = True

        if deadcell not in body:
            screen.addch(deadcell[0], deadcell[1], ' ')
        screen.addch(head[0], head[1], 'X')

        head = next_head_pos(head, direction)

        deadcell = body[-1][:]

        for x in range(len(body) - 1, 0, -1):
            body[x] = body[x - 1]

        body[0] = head[:]

        screen.refresh()
        time.sleep(speed[difficulty] - ((len(body) - start_length) * 0.001))

        if screen.inch(head[0], head[1]) != ord(' '):
            if screen.inch(head[0], head[1]) == ord('@'):
                foodmade = False
                for z in range(grow_length):
                    body.append(body[-1])
            else:
                gameover = True

    score = len(body) - start_length
    game_over_screen(score)


def change_direction(action, direction):
    if action == curses.KEY_UP and direction != 'down':
        direction = 'up'
    elif action == curses.KEY_DOWN and direction != 'up':
        direction = 'down'
    elif action == curses.KEY_RIGHT and direction != 'left':
        direction = 'right'
    elif action == curses.KEY_LEFT and direction != 'right':
        direction = 'left'

    return direction


def next_head_pos(head, direction):
    if direction == 'right':
        head[1] += 1
    elif direction == 'left':
        head[1] -= 1
    elif direction == 'down':
        head[0] += 1
    elif direction == 'up':
        head[0] -= 1
    return head


def game_over_screen(score):
    screen.clear()
    screen.nodelay(0)

    lines = ['Game Over',
             'You got {0} points'.format(score),
             '',
             'Is your name ' + player_name + '? (Press E to edit)',
             '',
             'Press -Space- to play again',
             'Press -M- to enter the menu',
             'Press -Q- to quit']

    for x in range(len(lines)):
        screen.addstr(int((window_height - len(lines)) / 2 + x),
                      int((window_width - len(lines[x])) / 2), lines[x])

    screen.refresh()

    key = 0
    while key not in [32, 113, 81, 109, 77, 101, 69]:
        key = screen.getch()

    if key == 32 or key == 81:
        high_score_set(score)
        game()
    elif key == 109 or key == 77:
        high_score_set(score)
        menu()
    elif key == 101 or key == 69:
        change_name(from_menu=False)
        high_score_set(score)
        show_high_score()
    else:
        high_score_set(score)
        curses.endwin()


def menu():
    screen.nodelay(0)
    screen.clear()
    selection = -1
    option = 0

    while selection < 0:

        items = ['Play',
                 'Instructions',
                 'Difficulty',
                 'High Scores',
                 'Edit Name',
                 'Exit']

        graphics = [0] * len(items)
        graphics[option] = curses.A_REVERSE

        screen.addstr(1, 5, 'Snake 1.0 by David Odenwald')
        screen.addstr(1, window_width - 17, 'Player: ' + player_name)

        for x in range(len(items)):
            screen.addstr(int(window_height / 2 + x), 5, items[x], graphics[x])

        screen.addstr(int(window_height - 2), 5, 'Difficulty: ' + difficulty)
        screen.refresh()

        action = screen.getch()
        if action == curses.KEY_UP:
            option = (option - 1) % 6
        elif action == curses.KEY_DOWN:
            option = (option + 1) % 6
        elif action == ord('\n'):
            selection = option
        elif action == ord('q'):
            curses.endwin
            break

    if selection == 0:
        game()
    elif selection == 1:
        instructions()
    elif selection == 2:
        game_options()
    elif selection == 3:
        show_high_score()
    elif selection == 4:
        change_name(from_menu=True)
    elif selection == 5:
        curses.endwin()


def instructions():
    screen.clear()
    screen.nodelay(0)
    lines = ['Use the arrow keys to move',
             'Dont run into the wall or the snake',
             'Eat food to grow and get points',
             '',
             'Press any key to go back']
    for x in range(len(lines)):
        screen.addstr(int((window_height - len(lines)) / 2 + x),
                      int((window_width - len(lines[x])) / 2), lines[x])
    screen.refresh()
    screen.getch()
    menu()


def game_options():
    screen.clear()
    screen.nodelay(0)

    selection = -1
    option = 0

    while selection < 0:
        graphics = [0] * 3
        graphics[option] = curses.A_REVERSE
        screen.addstr(1, 10, 'Difficulty')
        screen.addstr(int(window_height / 2 - 1), 10, 'Normal', graphics[0])
        screen.addstr(int(window_height / 2), 10, 'Hard', graphics[1])
        screen.addstr(int(window_height / 2 + 1), 10, 'Extrem', graphics[2])

        screen.refresh()
        action = screen.getch()
        if action == curses.KEY_UP:
            option = (option - 1) % 3
        elif action == curses.KEY_DOWN:
            option = (option + 1) % 3
        elif action == ord('\n'):
            selection = option

    if selection == 0:
        global difficulty
        global grow_length
        difficulty = 'Normal'
        grow_length = 1
        menu()
    elif selection == 1:
        difficulty = 'Hard'
        grow_length = 2
        menu()
    elif selection == 2:
        difficulty = 'Extrem'
        grow_length = 3
        menu()


def show_high_score():
    screen.clear()
    screen.nodelay(0)
    height = int(window_height / 2) - 6

    screen.addstr(1, 10, 'Top 10 Players')
    screen.addstr(height, 5, 'Rank')
    screen.addstr(height, 14, 'Name')
    screen.addstr(height, 23, 'Score')
    screen.addstr(height, 33, 'Difficulty')
    screen.addstr(height, 48, 'Date')

    if not os.path.exists(score_file):
        open(score_file, 'w+')

    # load the highscores.json file
    with open(score_file) as file_handle:
        try:
            highscores = json.load(file_handle)
        except ValueError:
            highscores = None

    rank = 1
    if highscores:
        for high_score in sorted(highscores, key=lambda k: k['score'],
                                 reverse=True):
            height = int(window_height / 2) - 6 + rank

            screen.addstr(height, 5, str(rank))
            screen.addstr(height, 14, high_score['name'])
            screen.addstr(height, 28 - len(str(high_score['score'])),
                          str(high_score['score']))
            screen.addstr(height, 43 - len(difficulty), difficulty)
            screen.addstr(height, 48, high_score['time'])

            rank += 1

            # break if 10 entries are displayed
            if rank > 10:
                break

    screen.refresh()
    screen.getch()
    menu()


def high_score_set(score):
    now = datetime.datetime.now()
    time_stamp = now.strftime('%H:%M %d.%m.%Y')
    new_entry = {'name': player_name,
                 'score': score,
                 'time': time_stamp,
                 'difficulty': difficulty}

    if not os.path.exists(score_file):
        open(score_file, 'w+')

    with open(score_file, mode='r') as file_handle:
        try:
            highscores = json.load(file_handle)
        except ValueError:
            highscores = []

    highscores.append(new_entry)

    with open(score_file, mode='w') as file_handle:
        json.dump(highscores, file_handle, indent=4)


def change_name(from_menu):
    screen.clear()
    screen.nodelay(0)
    screen.addstr(10, 10, 'Name:')
    textwin = curses.newwin(1, 8, 10, 16)
    text = curses.textpad.Textbox(textwin)
    textwin.bkgd(curses.color_pair(1))
    screen.refresh()

    global player_name
    player_name = text.edit()
    if from_menu:
        menu()

if __name__ == "__main__":
    menu()
