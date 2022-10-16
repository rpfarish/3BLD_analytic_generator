"""UI interface for putting letter pair times into the database"""

import pygame

from database.button import Button
from database.database import get_all, insert_pair

pygame.font.init()
WIDTH, HEIGHT = 400, 200
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f"Insert Letter Pairs into the Database")
pygame.display.set_icon(WIN)
FPS = 60
light_gray = (175, 175, 175)

FONT = pygame.font.Font(None, 32)


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('lightskyblue3')
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width


def main():
    """Gets main window running"""
    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont("mscomicsans", 20)
    label = main_font.render(f"Put a ',' between the pair and number", True, (255, 255, 255))
    bfs_b = Button(WIN, light_gray, x=100, y=100, width=200, height=25, win_w=WIDTH,
                   win_h=HEIGHT, text="Insert/update pair in database", font_size=15, button_value="BFS")

    input_box1 = InputBox(x=100, y=100, w=140, h=32)
    input_boxes = [input_box1]
    user_label = FONT.render(input_box1.text, True, (255, 0, 0))

    def redraw_window():
        """redraws the entire display"""
        WIN.fill((0, 0, 0))
        # Put updating objects here
        WIN.blit(label, (10, 10))
        bfs_b.draw_resize(WIDTH, HEIGHT, -.05, .2)
        WIN.blit(user_label, ((WIDTH // 2) - user_label.get_width() // 2, HEIGHT // 2))
        pygame.display.update()

    while True:
        redraw_window()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            for box in input_boxes:
                box.handle_event(event)

        for box in input_boxes:
            box.update()

        keys = pygame.key.get_pressed()
        click = pygame.mouse.get_pressed(num_buttons=3)
        mouse = pygame.mouse.get_pos()
        Button.update_all_buttons(mouse, click[0])
        user_label = FONT.render(input_box1.text, True, (255, 0, 0))

        if input_box1.text.count(',') == 1:
            a, b = input_box1.text.split(',')
            print(a, b)
            try:
                b = float(b)
            except ValueError:
                continue

            can_insert = click[0] or keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER]
            inserted = bfs_b.call_func(insert_pair, can_insert, 'edges_cycle_averages', a, b)
            r = get_all('edges_cycle_averages')

            # todo add to api
            if r is not None and a in dict(r):
                label = main_font.render(f"'{input_box1.text}' is in the database!!", True, (255, 255, 255))
            else:
                label = main_font.render(f"'{input_box1.text}' is not in the database!!", True, (255, 255, 255))

        if keys[pygame.K_ESCAPE]:
            return


if __name__ == '__main__':
    main()
