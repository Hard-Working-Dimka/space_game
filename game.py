import random
import time
import curses
import asyncio

from animations.shot import fire
from animations.space_ship import animate_spaceship

TIC_TIMEOUT = 0.1
MAX_STARS = 30
MIN_STARS = 15
ICONS_OF_STARS = ['+', '*', '.', ':']
OFFSET_OF_ANIMATION = 10


def get_frame(path):
    with open(path, "r") as file:
        file_content = file.read()
    return file_content


async def blink(canvas, row, column, symbol='*'):
    while True:
        for _ in range(random.randint(0, OFFSET_OF_ANIMATION)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


def draw(canvas):
    canvas.nodelay(True)
    canvas.border('|', '|')
    curses.curs_set(False)

    rows, columns = canvas.getmaxyx()
    quantity_of_stairs = random.randint(MIN_STARS, MAX_STARS)

    coroutine_of_shot = (fire(canvas, rows // 2, columns // 2))

    spaceship_first_frame = get_frame('animations/frames/rocket_frame_1.txt')
    spaceship_second_frame = get_frame('animations/frames/rocket_frame_2.txt')
    coroutine_of_spaceship = animate_spaceship(canvas, 0, columns // 2, spaceship_first_frame,
                                               spaceship_second_frame)

    coroutines = [coroutine_of_spaceship]  # TODO: add shot courutine
    for _ in range(quantity_of_stairs):
        row = random.randint(1, rows - 2)
        column = random.randint(1, columns - 2)
        coroutines.append(blink(canvas, row, column, symbol=random.choice(ICONS_OF_STARS)))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
        if len(coroutines) == 0:
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
