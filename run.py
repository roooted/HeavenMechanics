import pygame as pg
import pygame_menu as pg_menu
from math import hypot
import json
import ctypes
import random
import os
pg.init()

# Create the main stuffs
ctypes.windll.user32.SetProcessDPIAware()
face = pg.display.set_mode((0, 0), pg.FULLSCREEN)
W, H = face.get_size()
pg.display.set_caption("Небесная механика")
font = pg.font.SysFont('Verdana', 40)
clock = pg.time.Clock()

# Load the background image
back = pg.image.load(r'images\back.jpg')

# Create 2 extra transparent surface for dragging screen
face2 = pg.Surface((W * 3, H * 3), pg.SRCALPHA)
face2_x, face2_y = -W, -H
face3 = pg.Surface((W, H), pg.SRCALPHA)

bodies = pg.sprite.Group()
pixar1 = pg.PixelArray(face2.copy())


# ------------------------------ Variables ------------------------------ #


# Переменные
FPS = 25
dt = 1 / FPS

x0 = W * 3 // 2
y0 = H * 3 // 2 

start = False
drag = False
I = 0
delay = FPS // 6
dI = -delay

BACK_COLOR = (10, 15, 100)
BORDER_COLOR = (50, 15, 150)
FONT_COLOR = (50, 15, 200)


# ------------------------------ Classes ------------------------------ #


# Translate (x, y) to a new coords system
shift_coords = lambda x, y: (x0 + x, y0 - y)
unshift_coords = lambda x, y: (x - x0, y0 - y)
shift_speed = lambda Vx, Vy: (Vx, -Vy)

class Button:
    ''' Button class is used to create buttons to control running frame.
        This class is not associated with menu buttons '''
    def __init__(self, text, x, y, menu = 0):
        if menu != 0:
            self.menu = menu
        # 1. determine text size
        text_face = font.render(text, 0, FONT_COLOR)
        text_w, text_h = text_face.get_rect()[2:]
        
        # 2. draw button rectangle
        self.rect = pg.draw.rect(face3, BACK_COLOR, 
            (x, y, text_w + 2*10, text_h + 2*10))

        pg.draw.rect(face3, BORDER_COLOR, 
            (x, y, text_w + 2*10, text_h + 2*10),
            width = 5)
            
        # 3. depict text on the button
        face3.blit(text_face, (x + 10, y + 10))


    def is_pressed(self) -> bool:
        # determine if mouse in button's rect
        mouse_x, mouse_y = pg.mouse.get_pos()
        x, y, w, h = self.rect
        proper_x = x < mouse_x < x + w
        proper_y = y < mouse_y < y + h

        # determine if mouse left button is down
        clicked = pg.mouse.get_pressed()[0]

        if proper_x and proper_y and clicked:
            return True
        else:
            return False


class Body(pg.sprite.Sprite):
    ''' Body class allows to create some cosmos objects like planet and star'''
    
    def __init__(self, type, name, mass, coords, speed) -> None:
        global bodies
        # pg.sprite.Sprite.__init__(self)
        super().__init__()
        if type == 'Star':
            body_image = r'images\star.png'
        elif type == 'Planet':
            n = random.randint(1, 5)
            body_image = rf'images\planet_{n}.png'

        self.type = type
        self.image = pg.image.load(body_image)
        self.rect = self.image.get_rect(center = shift_coords(*coords))
        self.trace_color = random.choice(['Green', 'Blue', 'Purple', 'Gray'])

        self.start_mass = mass
        self.start_coords = shift_coords(*coords)
        self.start_speed = shift_speed(*speed)

        self.name = name
        self.mass = mass
        self.coords = shift_coords(*coords)
        self.speed = shift_speed(*speed)
        self.add(bodies)

    def erase(self, pixar) -> None:
        pixar2 = pg.PixelArray(face2)
        xp, yp, wp, hp = self.rect
        for i in range(xp, xp + wp + 1):
            for j in range(yp, yp + hp + 1):
                try:
                    pixar2[i][j] = pixar[i][j]
                except IndexError:
                    self.remove()
        del pixar2


# ------------------------------ Functions ------------------------------ #


def change_coords(body1) -> None:
    ''' Compute gravitation impact of the bodies on body1 in "bodies" group '''
    
    global dt, bodies
    G = 10000
    x1, y1 = body1.coords
    v1_x, v1_y = body1.speed

    a1_x, a1_y = 0, 0
    bodies_copy = list(bodies)
    bodies_copy.remove(body1)

    for body in bodies_copy:
        x_inf, y_inf = body.coords
        m_inf = body.mass

        # determine distance between body1 and body2
        lx, ly = x_inf - x1, y_inf - y1
        l = hypot(lx, ly)

        # determine acceleration of body1 in x-axis and y-axis
        a = G * m_inf / l**2
        a1_x += a * lx / l
        a1_y += a * ly / l

    # determine new coords of body1
    x2 = x1 + v1_x * dt + a1_x * dt**2 / 2
    y2 = y1 + v1_y * dt + a1_y * dt**2 / 2

    # determine velocity of body1 in x-axis and y-axis
    v2_x = v1_x + a1_x * dt
    v2_y = v1_y + a1_y * dt

    # change attributes of body1
    w, h = body1.rect[2:]
    body1.rect = pg.Rect(x2 - round(w/2), y2 - round(h/2), w, h)
    body1.coords = (x2, y2)
    body1.speed = (v2_x, v2_y)


def load_bodies(frame: str) -> None:
    ''' frame.json data => new bodyes in "bodies" group '''
    print('load:', frame)
    with open(rf'frames\{frame}.json') as json_file:
        frame_bodies = json.load(json_file)

    bodies.empty()
    for name, args in frame_bodies.items():
        Body(args['type'], name, args['mass'], args['coords'], args['speed'])

    bodies.draw(face2)
    face.blit(face2, (face2_x, face2_y))
    face.blit(face3, (0, 0))
    pg.display.update()


def add_body() -> None:
    ''' add_menu input => new budy in "bodies" group '''
    # Create new body
    Body(
        sel.get_value()[0][0],
        inp1.get_value(),
        int(inp2.get_value()),
        tuple(map(int, inp3.get_value().split(','))),
        tuple(map(int, inp4.get_value().split(',')))
    )
    
    # Clear data from add_menu
    for i in range(1, 5):
        eval(f'inp{i}').clear()

    # Clear add_menu from face3
    pixar3 = pg.PixelArray(face3)
    x, y, w, h = add_menu.get_rect()
    for i in range(x - 4, x + w + 4):
        for j in range(y, y + h + 4):
            pixar3[i][j] = 0
    del pixar3
    add_menu.disable()


def save_frame() -> None:
    ''' "bodies" group => frame_name.json '''
    frame_name = inp5.get_value()
    with open(fr'.\frames\{frame_name}.json', 'w') as json_file:
        bodies_dict = dict()
        for body in bodies:
            bodies_dict[body.name] = {
                'type': body.type,
                'mass': body.start_mass,
                'coords': unshift_coords(*body.start_coords),
                'speed': body.start_speed
            }
        json.dump(bodies_dict, json_file, indent=4)
    
    # Clear save_menu from face3
    pixar3 = pg.PixelArray(face3)
    x, y, w, h = save_menu.get_rect()
    for i in range(x - 4, x + w + 4):
        for j in range(y, y + h + 4):
            pixar3[i][j] = 0
    del pixar3
    save_menu.disable()


def update_bodies() -> None:
    ''' 1. Erase bodies from face2
        2. Change bodies coords 
        3. Draw bodies on a new place on face2'''
    global bodies, pixar1, face2, start
    for body in bodies:
        # 1. Erase old body image on face2
        body.erase(pixar1)
        
        # 2. Set new coords for body
        if start == True:
            change_coords(body)

        # 3. Draw body trace on face2 on old coords
        pg.draw.circle(face2, body.trace_color, body.rect.center, 1)

    # 4. Save current area of face2
    pixar1 = pg.PixelArray(face2.copy())

    # 5. Draw new body on face2
    bodies.draw(face2)


def run(use_current_group = True) -> None:
    ''' Run existing or empty frame '''
    global I, dI, dt, exit_but, obj_but, run_but, add_but, bodies_but, start, bodies_menu, \
    face2_x, face2_y, drag, add_menu, sub_menu

    if not use_current_group:
        # determine wich button on sub_menu was pressed
        mouse_x, mouse_y = pg.mouse.get_pos()
        menu_x, menu_y = sub_menu.get_position()
        mouse_menu_x, mouse_menu_y = mouse_x - menu_x, mouse_y - menu_y
        for button in sub_menu._widgets:
            x, y, w, h = button._rect
            if x < mouse_menu_x < x + w and y < mouse_menu_y < y + h:
                frame = button.get_title()
        load_bodies(frame)

    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT or exit_but.is_pressed():
                exit()

            # let drag screen
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x1 , mouse_y1 = event.pos
                drag = True

            # drag screen
            elif event.type == pg.MOUSEMOTION and drag == True:
                mouse_x2 , mouse_y2 = event.pos
                dx = mouse_x2 - mouse_x1
                dy = mouse_y2 - mouse_y1
                new_face2_x, new_face2_y = face2_x + dx, face2_y + dy  

                # Check bounds escape
                if -2*W < new_face2_x < 0 and -2*H < new_face2_y < 0:
                    face2_x, face2_y = new_face2_x, new_face2_y

                mouse_x1, mouse_y1 = mouse_x2, mouse_y2

            # stop drag screen
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                drag = False
                break
            
        
        # Check pressed keys
        I += 1
        keys = pg.key.get_pressed()

        # Stop
        if (keys[pg.K_TAB] == 1 or run_but.is_pressed()) and I - dI > delay:
            start = not(start)
            dI = I

        # Speeding up
        elif keys[pg.K_RIGHT] == 1 and dt < 0.45 and I - dI > delay:
            dt *= 3
            dI = I

        # Slowing down
        elif keys[pg.K_LEFT] == 1 and dt > 0.017 and I - dI > delay:
            dt /= 3
            dI = I
        
        # Check pressed buttons with menus
        for button in (add_but, save_but):
            menu = button.menu
            if button.is_pressed() and not menu.is_enabled() and I - dI > delay:
                menu.enable()
                menu.draw(face3)
                menu.update(events)
                dI = I

            elif menu.is_enabled():
                menu.draw(face3)
                menu.update(events)
        
        # Clear bodies
        if clear_but.is_pressed() and I - dI > delay:
            bodies.empty()
            face2.fill(pg.SRCALPHA)
            dI = I
        
        update_bodies()

        face.blit(back, (0, 0))
        face.blit(face2, (face2_x, face2_y))
        face.blit(face3, (0, 0))
        pg.display.update()
        clock.tick(FPS)


def set_size(widget) -> None:
    ''' Costomise widgets '''
    name = str(widget)
    w, h = widget.get_rect()[2:]
    if 'Button' in name:
        dw, dh = (250 - w)//2, (70 - h)//2
    elif 'Selector' in name or 'TextInput' in name:
        dw, dh = (400 - w)//2, (70 - h)//2
    widget.set_padding((dh, dw))


# ------------------------------ Menus ------------------------------ #


# Create main_menu, add_menu and sub_menu
theme1 = pg_menu.Theme(
    title_font_color = FONT_COLOR,
    title_background_color = BACK_COLOR,
    background_color = (10, 15, 35),

    widget_background_color = BACK_COLOR,
    widget_border_width = 5,
    widget_border_color = BORDER_COLOR,
    widget_font_color = FONT_COLOR,
    widget_selection_effect = pg_menu.widgets.NoneSelection(),
    widget_margin = (0, 15))


main_menu = pg_menu.menu.Menu(
    'Menu', 600, 450, 
    mouse_motion_selection = True,
    theme = theme1)

sub_menu = pg_menu.menu.Menu(
    'Open frame', 600, 450,
    theme = theme1)

add_menu = pg_menu.menu.Menu(
    'New body', 650, 550,
    theme = theme1,
    enabled = False)

save_menu = pg_menu.menu.Menu(
    'Save frame', 600, 250,
    theme = theme1,
    enabled = False)


# Add buttons on main_menu
main_menu.add.button('New frame', run)
main_menu.add.button('Open frame', sub_menu)
main_menu.add.button('Exit', pg_menu.events.EXIT)

# Add buttons on sub_menu referenced to each frame
files = os.listdir('frames')
for file in files:
    frame_name = file[:-5]
    button = sub_menu.add.button(frame_name, lambda: run(0))
if files == []:
    sub_menu.add.label('No frames yet')

# Add widgets on add_menu
sel = add_menu.add.selector('Type: ', 
    [('Planet', 1), ('Star', 2)],
    style = 'classic')

inp1 = add_menu.add.text_input('Name:  ',
    input_underline = '_', input_underline_len = 20, maxchar = 10)
inp2 = add_menu.add.text_input('Mass:   ',
    input_underline = '_', input_underline_len = 30, maxchar = 10)
inp3 = add_menu.add.text_input('Position (x, y): ',
    input_underline = '_', input_underline_len = 12, maxchar = 10)
inp4 = add_menu.add.text_input('Velocity (Vx, Vy): ',
    input_underline = '_', input_underline_len = 9, maxchar = 10)
add_menu.add.button('Create', add_body)

# Add widgets on save_menu
inp5 = save_menu.add.text_input('Frame name: ',
    input_underline = '_', input_underline_len = 12, maxchar = 10)
save_menu.add.button('Save', save_frame)

# Castomize menus
for menu in (main_menu, sub_menu, add_menu, save_menu):
    w, h = menu.get_size()
    w, h = w//2, h//2
    decorator = menu.get_decorator()
    decorator.add_line((w, -h), (w, h), color = BACK_COLOR, width = 4)
    decorator.add_line((w, h), (-w, h), color = BACK_COLOR, width = 4)
    decorator.add_line((-w - 2, h), (-w - 2, -h), color = BACK_COLOR, width = 4)

    for widget in menu._widgets:
        set_size(widget)

# Adding buttons on face3
exit_but = Button('Exit', W - 120, 30)
add_but = Button('New body', 30, 30, add_menu)
save_but = Button('Save', W - 140, H - 270, save_menu)
run_but = Button('Run', W - 120, H - 180)
clear_but = Button('Clear', W - 145, H - 90)

main_menu.mainloop(face, bgfun = lambda: face.blit(back, (0, 0)))