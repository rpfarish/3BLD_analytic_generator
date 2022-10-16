"""
Creates interactive buttons for pygame


basic usage:

 example_button

 light_gray = (175, 175, 175)
 bfs_b = Button(window, light_gray, x=100, y=100, width=100, height=25, win_w=win_width,
                   win_h=win_height, text="BFS", font_size=20, button_value="BFS")

 include: Button.update_all_buttons(mouse, click[0])


 resize on modular coordinates:
 bfs_b.draw_resize(win_width, win_height, -.05, .15)




"""

from collections import deque

import pygame

pygame.font.init()

# Grays
light_gray = (175, 175, 175)
medium_gray = (140, 140, 140)
dark_gray = (110, 110, 110)
very_dark_gray = (50, 50, 50)

# Primary, black and white colors
white = (230, 230, 230)
red = (255, 0, 0)
dark_red = (225, 0, 0)
yellow = (235, 235, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
black = (0, 0, 0)


class Button:
    """
    Creates responsive, interactive, versatile, and scalable buttons for pygame
    :param win: pygame display window
    :param color: color of the button in rgb
    :param x:  pixel coord pos (x location)
    :param y: pixel coord pos (y location)
    :param width: width of the button
    :param height: height of the button
    :param win_w: width of the display window
    :param win_h: height of the display window
    :param text: string of text displayed over the center of the button
    :param font_size: size of the font
    :param button_value: secondary identifier of the value of the button that
        can be a number or a string (or any) for external comparison.
    :param text_color: color of the displayed text
    :param font: name of font
    :param obj_li: list of strings to be cycled in the cycle_text method

    """
    buttons = deque([])  # registrar

    def __init__(self, win, color: tuple, x, y, width, height, win_w: int, win_h: int, text: str,
                 font_size: int, button_value: any = None, text_color: tuple = None, font: str = None,
                 obj_li: list = None, cycle_values: list = None):
        assert isinstance(win, pygame.Surface)
        self.__class__.buttons.append(self)
        self.Win = win
        self.color = color
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.text = text
        self.text_color = (0, 0, 0) if text_color is None else text_color
        self.font = "arial" if font is None else font
        self.font_size = font_size
        self.font_label = pygame.font.SysFont(self.font, self.font_size)
        self.text_label = self.font_label.render(str(self.text), True, self.text_color)
        self.clickable = True
        self.win_width = win_w
        self.win_height = win_h
        self.button_value = button_value
        self.timer = 0
        self.delay = 12
        self.toggle_bool = False
        self.cycle_num = 0
        self.text_cycle_len = 0
        self._click_lock = False
        # Change obj_li into a dict
        self.obj_li = [''] if obj_li is None else obj_li
        self.cycle_values = [0] if cycle_values is None else cycle_values

    @classmethod
    def clear_buttons(cls):
        """
        empties buttons list
        """
        cls.buttons.clear()

    @classmethod
    def update_all_buttons(cls, mouse, click):
        """
        Updates the can click state for all Button instances
        Should go close to the top of the main loop
        :param mouse:
        :param click:
        """
        for obj in cls.buttons:
            obj.handle_mouse(mouse, click)

    def draw(self) -> None:
        """
        draws the button rect and then the text centered over it
        """
        pygame.draw.rect(self.Win, self.color, (self.x, self.y, self.width, self.height))
        self.Win.blit(self.text_label, ((self.width // 2) + self.x - self.text_label.get_width() // 2,
                                        (self.height // 2) + self.y - self.text_label.get_height() // 2))

    def draw_resize(self, width: int, height: int, x_offset: float = 0, y_offset: float = 0) -> None:
        """

        :param width:
        :param height:
        :param x_offset:
        :param y_offset:
        """
        self.x = width // 2 - self.width // 2 + int(x_offset * width)
        self.y = height // 2 - self.height // 2 + int(y_offset * height)
        pygame.draw.rect(self.Win, self.color, (self.x, self.y, self.width, self.height))
        self.Win.blit(self.text_label, ((self.width // 2) + self.x - self.text_label.get_width() // 2,
                                        (self.height // 2) + self.y - self.text_label.get_height() // 2))

    def _hover(self, mouse: tuple) -> bool:
        if self.x < mouse[0] < self.x + self.width and self.y < mouse[1] < self.y + self.height:
            self.color = medium_gray
            return True
        else:
            self.color = light_gray
            return False

    def change_text(self, new_text: str) -> None:
        """

        :param new_text:
        """
        self.text_label = self.font_label.render(str(new_text), True, self.text_color)

    def change_font_size(self, size: int) -> None:
        """

        :param size:
        """
        self.font_size = int(size)
        self.font_label = pygame.font.SysFont(self.font, self.font_size)

    def toggle_text(self, click: bool, text1: str, text2: str) -> bool:
        """

        :param click:
        :param text1:
        :param text2:
        :return:
        """
        if self.clickable:
            self.change_text(text1 if self.toggle_bool else text2)
            if self.timer >= self.delay and click:
                self.toggle_bool = not self.toggle_bool
                self.timer = 0
                return self.toggle_bool
        self.timer += 1
        return self.toggle_bool

    def set_cycle_value(self, speed):
        """

        :param speed:
        """
        if not self.cycle_values:
            print('cycle_values is empty')
            raise ValueError
        for num, i in enumerate(self.cycle_values):
            if speed == i:
                self.cycle_num = num

    def get_cycle_value(self):
        """

        :return:
        """
        for i in range(len(self.obj_li)):
            if self.cycle_num == i:
                return self.cycle_values[i]

    def cycle_text(self, click: bool) -> None:
        """

        :param click:
        """
        if self.clickable:
            self.change_text(self.obj_li[self.cycle_num])
            if self.timer >= self.delay and click:
                if len(self.obj_li) - 1 > self.cycle_num:
                    self.cycle_num += 1
                else:
                    self.cycle_num = 0
                self.timer = 0
        self.timer += 1

    def alt_text_state(self, click: bool, text: str, color: tuple, size: int, alt_text: str,
                       alt_text_size: int) -> None:
        """
        MUST go after handle_mouse/update_all_buttons
        :param click:
        :param text:
        :param color:
        :param size:
        :param alt_text:
        :param alt_text_size:
        """
        if self.clickable and click:
            self.change_font_size(size)
            self.change_text(text)
            self.color = color
        else:
            self.change_font_size(alt_text_size)
            self.change_text(alt_text)

    def _can_click(self, mouse, click) -> bool:
        if not self._hover(mouse) and click:
            self.clickable = False
            return False
        if not self._hover(mouse) and not click:
            self.clickable = True
            return True

    def handle_mouse(self, mouse, click) -> None:
        """

        :param mouse:
        :param click:
        """
        self._can_click(mouse, click)
        self._hover(mouse)

    def call_func(self, func, click, *args, **kwargs) -> any:
        """

        :param func:
        :param click:
        :param args:
        :param kwargs:
        :return:
        """
        if self.clickable and click and not self._click_lock:
            self._click_lock = True
            self.color = dark_gray
            self.draw()
            pygame.display.update()
            return func(*args, **kwargs)
        elif self.clickable and click:
            self.color = dark_gray

        if not click:
            self._click_lock = False
