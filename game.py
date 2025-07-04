import time
import curses
import asyncio
import os, random
from itertools import cycle

from animations.animations import fly_garbage, fire
from animations.game_scenario import get_garbage_delay_tics, PHRASES
from animations.physics_of_ship import update_speed
from curses_tools import get_frame_size, draw_frame, read_controls
from game_over import show_gameover

TIC_TIMEOUT = 0.1
MAX_STARS = 30
MIN_STARS = 15
ICONS_OF_STARS = ['+', '*', '.', ':']
OFFSET_OF_ANIMATION = 10
CHANGE_YEAR_AFTER = 10
SHIFT_YEAR_STEP = 10

coroutines = []
obstacles = []
obstacles_in_last_collisions = []
year = 1957


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def restore_frame(canvas):
    while True:
        canvas.border('|', '|')
        await sleep(1)


async def timer(tiks):
    await sleep(tiks)
    return SHIFT_YEAR_STEP


def get_frame(path):
    with open(path, "r") as file:
        file_content = file.read()
    return file_content


async def fill_orbit_with_garbage(canvas, garbage_filenames, columns):
    global year
    while True:
        time = get_garbage_delay_tics(year)
        if time is None:
            year = year + await timer(CHANGE_YEAR_AFTER)
            continue
        await sleep(time)
        garbage_filename = random.choice(garbage_filenames)
        garbage_frame = get_frame(f'animations/frames/garbage/{garbage_filename}')
        column = random.randint(2, columns - 2)

        coroutines.append(
            fly_garbage(canvas, column=column, garbage_frame=garbage_frame, obstacles=obstacles,
                        obstacles_in_last_collisions=obstacles_in_last_collisions))
        year = year + await timer(CHANGE_YEAR_AFTER)


async def run_spaceship(canvas, start_row, start_column, sub_window, *args):
    rows_canvas, columns_canvas = canvas.getmaxyx()
    row_speed = column_speed = 0
    is_over = False

    for frame in cycle(args):
        rows_spaceship, columns_spaceship = get_frame_size(frame)

        for _ in range(2):
            sub_window.refresh()
            sub_window.addstr(1, 2, f'year - {year} ---- {PHRASES.get(year) or ''}')
            if not is_over:
                rows_direction, columns_direction, fire_on = read_controls(canvas)
                row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)

                start_row += row_speed
                start_column += column_speed

                rows_direction_validated = min(max(start_row, 1), rows_canvas - 2 - rows_spaceship - 1)
                columns_spaceship_validated = min(max(start_column, 1), columns_canvas - columns_spaceship - 1)

                start_row, start_column = rows_direction_validated, columns_spaceship_validated

                draw_frame(canvas, start_row, start_column, frame)

                if fire_on and year >= 2000:
                    coroutines.append(
                        fire(canvas, start_row, start_column + 2, obstacles, obstacles_in_last_collisions))

                for obstacle in obstacles:
                    if obstacle.has_collision(start_row, start_column + 2):
                        draw_frame(canvas, start_row, start_column, frame, negative=True)
                        show_gameover(canvas, rows_canvas // 3, columns_canvas // 4)
                        is_over = True
            else:
                show_gameover(canvas, rows_canvas // 3, columns_canvas // 4)

            await asyncio.sleep(0)
            draw_frame(canvas, start_row, start_column, frame, negative=True)


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

    sub_window = canvas.derwin(3, columns, rows - 3, 0)
    sub_window.border('|', '|')

    coroutines.append(restore_frame(canvas))
    coroutines.append(restore_frame(sub_window))

    spaceship_first_frame = get_frame('animations/frames/rocket_frame_1.txt')
    spaceship_second_frame = get_frame('animations/frames/rocket_frame_2.txt')
    coroutines.append(run_spaceship(canvas, 0, columns // 2, sub_window, spaceship_first_frame,
                                    spaceship_second_frame))

    offset_tics = random.randint(0, OFFSET_OF_ANIMATION)
    for _ in range(quantity_of_stairs):
        row = random.randint(1, rows - 4)
        column = random.randint(1, columns - 2)
        coroutines.append(blink(canvas, row, column, offset_tics, symbol=random.choice(ICONS_OF_STARS)))

    garbage_filenames = os.listdir('animations/frames/garbage')
    coroutines.append(fill_orbit_with_garbage(canvas, garbage_filenames, columns))

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
