import asyncio
import curses

from curses_tools import draw_frame, read_controls, get_frame_size
from itertools import cycle

ACCELERATION_OF_SHIP = 10


async def animate_spaceship(canvas, start_row, start_column, *args):
    rows_canvas, columns_canvas = canvas.getmaxyx()
    for frame in cycle(args):
        rows_spaceship, columns_spaceship = get_frame_size(frame)

        for _ in range(2):
            rows_direction, columns_direction, _ = read_controls(canvas)

            rows_direction_validated = min(max(rows_direction * ACCELERATION_OF_SHIP + start_row, 1),
                                           rows_canvas - rows_spaceship - 1)
            columns_spaceship_validated = min(max(columns_direction * ACCELERATION_OF_SHIP + start_column, 1),
                                              columns_canvas - columns_spaceship - 1)

            start_row, start_column = rows_direction_validated, columns_spaceship_validated
            draw_frame(canvas, start_row, start_column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, start_row, start_column, frame, negative=True)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
