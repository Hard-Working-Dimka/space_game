import time
import curses
import asyncio
import os, random

from animations.animations import animate_spaceship, fly_garbage

TIC_TIMEOUT = 0.1
MAX_STARS = 30
MIN_STARS = 15
ICONS_OF_STARS = ['+', '*', '.', ':']
OFFSET_OF_ANIMATION = 10
COROUTINES = []


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


def get_frame(path):
    with open(path, "r") as file:
        file_content = file.read()
    return file_content


async def fill_orbit_with_garbage(canvas, garbage_filenames, columns):
    while True:
        await sleep(random.randint(1, 30))
        garbage_filename = random.choice(garbage_filenames)
        garbage_frame = get_frame(f'animations/frames/garbage/{garbage_filename}')
        COROUTINES.append(fly_garbage(canvas, column=random.randint(2, columns - 2), garbage_frame=garbage_frame))


async def blink(canvas, row, column, offset_tics, symbol='*'):
    while True:
        await sleep(offset_tics)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


def draw(canvas):
    canvas.nodelay(True)
    canvas.border('|', '|')
    curses.curs_set(False)

    rows, columns = canvas.getmaxyx()
    quantity_of_stairs = random.randint(MIN_STARS, MAX_STARS)

    spaceship_first_frame = get_frame('animations/frames/rocket_frame_1.txt')
    spaceship_second_frame = get_frame('animations/frames/rocket_frame_2.txt')
    COROUTINES.append(animate_spaceship(canvas, 0, columns // 2, spaceship_first_frame,
                                        spaceship_second_frame))

    offset_tics = random.randint(0, OFFSET_OF_ANIMATION)
    for _ in range(quantity_of_stairs):
        row = random.randint(1, rows - 2)
        column = random.randint(1, columns - 2)
        COROUTINES.append(blink(canvas, row, column, offset_tics, symbol=random.choice(ICONS_OF_STARS)))

    garbage_filenames = os.listdir('animations/frames/garbage')
    COROUTINES.append(fill_orbit_with_garbage(canvas, garbage_filenames, columns))

    while True:
        for coroutine in COROUTINES.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
        if len(COROUTINES) == 0:
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
