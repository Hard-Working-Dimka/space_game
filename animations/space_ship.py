import asyncio

from curses_tools import draw_frame, read_controls, get_frame_size
from itertools import cycle


async def animate_spaceship(canvas, start_row, start_column, *args):
    rows_canvas, columns_canvas = canvas.getmaxyx()
    for frame in cycle(args):
        rows_spaceship, columns_spaceship = get_frame_size(frame)

        for _ in range(2):
            rows_direction, columns_direction, _ = read_controls(canvas)

            rows_direction_validated = min(max(rows_direction + start_row, 1), rows_canvas - rows_spaceship - 1)
            columns_spaceship_validated = min(max(columns_direction + start_column, 1),
                                              columns_canvas - columns_spaceship - 1)

            start_row, start_column = rows_direction_validated, columns_spaceship_validated
            draw_frame(canvas, start_row, start_column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, start_row, start_column, frame, negative=True)
