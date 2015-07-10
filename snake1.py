#!/usr/bin/python
# Autor: David Odenwald, 8/5/14

import curses
import curses.textpad
import time
import random

screen = curses.initscr()
dims = screen.getmaxyx()
curses.curs_set(0)
curses.noecho()
curses.cbreak()
screen.nodelay(1)
screen.border()
screen.keypad(1)
random.seed()

curses.start_color()
curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

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
    gameover = False
    direction = 0  # 0:right 1:down 2:left 3:up
    deadcell = body[-1][:]
    foodmade = False
    from_menu = False

    while not gameover:
        while not foodmade:
            x, y = random.randrange(1, dims[0] - 1), random.randrange(1, dims[1] - 1)
            if screen.inch(y, x) == ord(' '):
                foodmade = True
                screen.addch(y, x, ord('@'))
        if deadcell not in body:
            screen.addch(deadcell[0], deadcell[1], ' ')
        screen.addch(head[0], head[1], 'X')

        action = screen.getch()
        if action == curses.KEY_UP and direction != 1:
            direction = 3
        elif action == curses.KEY_DOWN and direction != 3:
            direction = 1
        elif action == curses.KEY_RIGHT and direction != 2:
            direction = 0
        elif action == curses.KEY_LEFT and direction != 0:
            direction = 2

        if direction == 0:
            head[1] += 1
        elif direction == 2:
            head[1] -= 1
        elif direction == 1:
            head[0] += 1
        elif direction == 3:
            head[0] -= 1

        deadcell = body[-1][:]

        for z in range(len(body) - 1, 0, -1):
            body[z] = body[z - 1]

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

    screen.clear()
    screen.nodelay(0)
    message1 = 'Game Over'
    message2 = 'You got ' + str(len(body) - start_length) + ' points'
    message3 = 'Is your name ' + player_name + '? (Press E to edit)'
    message4 = 'Press -Space- to play again'
    message5 = 'Press -M- to enter the menu'
    message6 = 'Press -Q- to quit'
    screen.addstr(int(dims[0] / 2 - 3), int((dims[1] - len(message1)) / 2), message1)
    screen.addstr(int(dims[0] / 2 - 1), int((dims[1] - len(message2)) / 2), message2)
    screen.addstr(int(dims[0] / 2 + 1), int((dims[1] - len(message3)) / 2), message3)
    screen.addstr(int(dims[0] / 2 + 3), int((dims[1] - len(message4)) / 2), message4)
    screen.addstr(int(dims[0] / 2 + 4), int((dims[1] - len(message5)) / 2), message5)
    screen.addstr(int(dims[0] / 2 + 5), int((dims[1] - len(message6)) / 2), message6)
    screen.refresh()
    q = 0
    while q not in [32, 113, 81, 109, 77, 101, 69]:
        q = screen.getch()
    if q == 32 or q == 81:
        high_score_set(len(body) - start_length)
        game()
    elif q == 109 or q == 77:
        high_score_set(len(body) - start_length)
        menu()
    elif q == 101 or q == 69:
        change_name(from_menu)
        high_score_set(len(body) - start_length)
        high_score()
    else:
        high_score_set(len(body) - start_length)
        curses.endwin()


def menu():
    a = True
    screen.nodelay(0)
    screen.clear()
    selection = -1
    option = 0

    while selection < 0:
        graphics = [0] * 6
        graphics[option] = curses.A_REVERSE
        screen.addstr(1, 10, 'Snake 1.0')
        screen.addstr(1, dims[1] - 17, 'Player: ' + player_name)
        screen.addstr(int(dims[0] / 2 - 2), 10, 'Play', graphics[0])
        screen.addstr(int(dims[0] / 2 - 1), 10, 'Instructions', graphics[1])
        screen.addstr(int(dims[0] / 2), 10, 'Difficulty', graphics[2])
        screen.addstr(int(dims[0] / 2 + 1), 10, 'High Scores', graphics[3])
        screen.addstr(int(dims[0] / 2 + 2), 10, 'Edit Name', graphics[4])
        screen.addstr(int(dims[0] / 2 + 3), 10, 'Exit', graphics[5])
        screen.addstr(int(dims[0] - 2), 10, 'Difficulty: ' + difficulty)
        screen.refresh()
        action = screen.getch()
        if action == curses.KEY_UP:
            option = (option - 1) % 6
        elif action == curses.KEY_DOWN:
            option = (option + 1) % 6
        elif action == ord('\n'):
            selection = option

    if selection == 0:
        game()
    elif selection == 1:
        instructions()
    elif selection == 2:
        game_options()
    elif selection == 3:
        high_score()
    elif selection == 4:
        change_name(a)
    elif selection == 5:
        curses.endwin()


def instructions():
    screen.clear()
    screen.nodelay(0)
    lines = ['Use the arrow keys to move', 'Dont run into the wall or the snake', '', 'Press any key to go back']
    for z in range(len(lines)):
        screen.addstr(int((dims[0] - len(lines)) / 2 + z), int((dims[1] - len(lines[z])) / 2), lines[z])
    screen.refresh()
    screen.getch()
    menu()


def game_options():
    screen.nodelay(0)
    screen.clear()
    selection = -1
    option = 0

    while selection < 0:
        graphics = [0] * 3
        graphics[option] = curses.A_REVERSE
        screen.addstr(1, 10, 'Difficulty')
        screen.addstr(int(dims[0] / 2 - 1), 10, 'Normal', graphics[0])
        screen.addstr(int(dims[0] / 2), 10, 'Hard', graphics[1])
        screen.addstr(int(dims[0] / 2 + 1), 10, 'Extrem', graphics[2])

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


def high_score():
    screen.clear()
    screen.nodelay(0)
    screen.addstr(1, 10, 'Top 10 Players')
    screen.addstr(int(dims[0] / 2) - 6, 10, 'Rank' + '\t' + 'Name' + '\t' + 'Score')

    data = open('highScore.list', 'r')
    scores = data.readlines()
    data.close()
    score = []
    name = []
    sort_name = [0] * len(scores)

    for x in range(len(scores)):
        if '\n' in scores[x]:
            scores[x] = scores[x][:-1]
        score.append(int(scores[x][:scores[x].find(':')]))
        name.append(scores[x][scores[x].find(':') + 1:])

    sort_score = score.copy()
    sort_score.sort()
    sort_score.reverse()

    for z in range(len(score)):
        for y in range(len(score)):
            if sort_score[z] == score[y]:
                sort_name[z] = name[y]
                score[y] = 0
                break

    if len(score) > 10:
        for j in range(10):
            screen.addstr(int(dims[0] / 2) + (j - 5), 10,
                          str(j + 1) + '\t' + str(sort_name[j]) + '\t' + str(sort_score[j]))
    else:
        for j in range(len(score)):
            screen.addstr(int(dims[0] / 2) + (j - 5), 10,
                          str(j + 1) + '\t' + str(sort_name[j]) + '\t' + str(sort_score[j]))

    screen.refresh()
    screen.getch()
    menu()


def high_score_set(score):
    data = open('highScore.list', 'a')
    data.writelines(str(score) + ':' + player_name + '\n')
    data.close()


def change_name(a):
    screen.clear()
    screen.nodelay(0)
    screen.addstr(10, 10, 'Name:')
    textwin = curses.newwin(1, 8, 10, 16)
    text = curses.textpad.Textbox(textwin)
    textwin.bkgd(curses.color_pair(1))
    screen.refresh()
    global player_name
    player_name = text.edit()
    if a:
        menu()


menu()
curses.endwin()
