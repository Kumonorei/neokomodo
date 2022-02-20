from typing import Iterable, List, Reversible, Tuple
import textwrap

import tcod

import color

class Message:
    def __init__(self, text: str, fg: Tuple[int, int, int]):
        self.plain_text = text
        self.fg = fg
        self.count = 1

    @property
    def full_text(self) -> str:
        """The full text of this message, including the count if required"""
        if self.count > 1:
            return f"{self.plain_text} (x{self.count})"
        return self.plain_text

class MessageLog:
    def __init__(self) -> None:
        self.messages: List[Message] = []

    def add_message(
        self,
        text: str,
        fg: Tuple[int, int, int] = color.white,
        *,
        stack: bool = True,
    ) -> None:
        """
        Add a message to this log
        'text' is the message text, 'fg' is the text color
        if 'stack' is true, then message can stack with a 
        previous message of the same text
        """
        if stack and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count +=1
        else:
            self.messages.append(Message(text, fg))

    def render(
        self,
        console: tcod.Console,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        """
        Render this log over the given area
        'x', 'y', 'width', 'height' is the rectangle region
        to render the messages
        """
        self.render_messages(console, x, y, width, height, self.messages)

    def render_in_frame(
        self,
        console: tcod.Console,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        """
        Render this log inside the given frame
        'x', 'y', 'width', 'height' is the rectangle region
        to render the frame
        """

        console.draw_frame(
            x=x, 
            y=y, 
            width=width, 
            height=height, 
            title="Message History", 
            clear=True, 
            fg=(255, 255, 255), 
            bg=(0, 0, 0),
        )

        self.render_messages(console, x+1, y+1, width-2, height-2, self.messages)

    @staticmethod
    def wrap(string: str, width: int) -> Iterable[str]:
        """Return a wrapped text message"""
        for line in string.splitlines(): # handle newlines in messages
            yield from textwrap.wrap(
                line, width, expand_tabs=True,
            )

    @classmethod
    def render_messages(
        cls,
        console: tcod.Console,
        x: int,
        y: int,
        width: int,
        height: int,
        messages: Reversible[Message],
    ) -> None:
        """
        Render the messages provided.
        The 'messages' are rendered starting at the latest 
        and working backwards
        """
        y_offset = height-1

        for message in reversed(messages):
            for line in reversed(list(cls.wrap(message.full_text, width))):
                console.print(x=x, y=y + y_offset, string=line, fg=message.fg)
                y_offset -= 1
                if y_offset < 0:
                    return # as there is no more space to print