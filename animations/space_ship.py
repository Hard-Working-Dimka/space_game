import asyncio

from curses_tools import draw_frame
from itertools import cycle


async def animate_spaceship(canvas, start_row, start_column, *args):
    for frame in cycle(args):
        draw_frame(canvas, start_row, start_column, frame)
        for _ in range(5):
            await asyncio.sleep(0)
        draw_frame(canvas, start_row, start_column, frame, negative=True)
