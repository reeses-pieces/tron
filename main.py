#!/usr/bin/env python3

import turtle
import os
import sys
import game

class MainMenu(object):
    """Main menu creates a 800 x 600 window to allow you to view the controls,
    change the grid size, start the game, and quit the game.
    """

    game_on = False
    
    def __init__(self):
        self.current_screen = 'main'
        self.relative_controls = False
        self.keyboard_bindings()

    def create_screen(self):
        """Create medium sized main menu."""
        self.current_screen == 'main'
        self.width, self.height = (800, 600)
        self.screen = turtle.Screen()
        self.screen.bgcolor('black')
        self.screen.bgpic('images/main_menu.gif')
        self.screen.setup(self.width, self.height, startx=None, starty=None)
        self.screen.title('TURTLETRON')
        self.screen.tracer(0)

    def set_cursor_master(self):
        """Runs in start menu loop. Controlled by
        cursor_up and cursor_down functions.
        """
        if self.current_screen == 'main':
            self.set_cursor_main()
        elif self.current_screen == 'grid_size':
            self.set_cursor_grid_size()
        elif self.current_screen == 'controls':
            self.set_cursor_controls()

    def set_cursor_main(self):
        """Main: Start = 3, Controls = 2, Quit = 1"""
        if self.pen.cursor_pos == 1:
            self.pen.setposition(-48, -128)
        elif self.pen.cursor_pos == 2:
            self.pen.setposition(-80, -14)
        else: # Position 3
            self.pen.setposition(-50, 98)

    def set_cursor_controls(self):
        """Controls: Relative = 1, Absolute = 2."""
        if self.pen.cursor_pos == 1:
            self.pen.setposition(-285, -215)
        else:
            self.pen.setposition(145, -215)
        self.display_controls()


    def set_cursor_grid_size(self):
        """Grid Size: Small = 1, Medium = 2, Large = 3"""
        if self.pen.cursor_pos == 1:
            self.pen.setposition(-310, -15)
        elif self.pen.cursor_pos == 2:
            self.pen.setposition(-75, -15)
        else: # Position 3
            self.pen.setposition(195, -15)

    def cursor_up(self):
        """Increase cursor pos by 1. Controls screen only has two options."""
        if self.current_screen == 'controls' and self.pen.cursor_pos < 2:
            self.pen.cursor_pos += 1
        elif self.pen.cursor_pos < 3:
            self.pen.cursor_pos += 1

    def cursor_down(self):
        """Decrease cursor pos by 1."""
        if self.pen.cursor_pos > 1:
            self.pen.cursor_pos -= 1

    def keyboard_bindings(self):
        """Sets bindings depending on which screen is displayed. Either player
        can control cursor.
        """
        turtle.listen()
        if self.current_screen == 'main':
            turtle.onkeypress(self.cursor_up, 'Up')
            turtle.onkeypress(self.cursor_up, 'w')
            turtle.onkeypress(self.cursor_down, 'Down')
            turtle.onkeypress(self.cursor_down, 's')
        elif (self.current_screen == 'grid_size' or
              self.current_screen == 'controls'):
            turtle.onkeypress(self.cursor_up, 'Right')
            turtle.onkeypress(self.cursor_up, 'd')
            turtle.onkeypress(self.cursor_down, 'Left')
            turtle.onkeypress(self.cursor_down, 'a')
        # Apply special function to return or space
        turtle.onkeypress(self.press_enter_or_space_master, 'Return')
        turtle.onkeypress(self.press_enter_or_space_master, 'space')

    def press_enter_or_space_master(self):
        """Depending on the current screen,
        passes the action to its corresponding function.
        """
        if self.current_screen == 'main':
            self.press_enter_or_space_main()
        elif self.current_screen == 'grid_size':
            self.press_enter_or_space_grid_size()
        elif self.current_screen == 'controls':
            self.press_enter_or_space_controls()

    def press_enter_or_space_main(self):
        """Controls how enter or space function depending on the cursor position
        for the main screen.
        """
        if self.pen.cursor_pos == 3:
            self.display_grid_options()
        elif self.pen.cursor_pos == 2:
            self.display_controls()
            # Needed to show saved control setting
            if self.relative_controls:
                self.pen.cursor_pos = 1
            else:
                self.pen.cursor_pos = 2
        elif self.pen.cursor_pos == 1:
            if os.name == 'posix':
                os.system('killall afplay')
            turtle.bye()

    def press_enter_or_space_controls(self):
        """Controls how enter or space function depending on the cursor position
        for the controls screen.
        """
        if self.pen.cursor_pos == 1:
            self.relative_controls = True
        else:
            self.relative_controls = False
        self.pen.cursor_pos = 2 # Return to last main menu position
        self.display_main()

    def press_enter_or_space_grid_size(self):
        """Controls how enter or space function depending on the cursor position
        for the grid size screen.
        """
        if self.pen.cursor_pos == 1:
            width, height = (640, 480)
        elif self.pen.cursor_pos == 2:
            width, height = (800, 600)
        elif self.pen.cursor_pos == 3:
            width, height = (1024, 768)
        else:
            pass
        self.screen.clear()
        self.pen.clear()
        if os.name == 'posix':
            os.system('killall afplay')
        self.game_on = True
        # Start game
        self.start_game(width, height)
        # Game finishes and returns to menu
        self.current_screen = 'main'
        menu.start_menu()

    def display_controls(self):
        """Displays control screen. User can choose between relative or absolute
        control scheme.
        """
        self.current_screen = 'controls'
        if self.pen.cursor_pos == 1:
            self.screen.bgpic('images/controls_relative.gif')
        else:
            self.screen.bgpic('images/controls_absolute.gif')

    def display_main(self):
        """Displays the main menu."""
        self.current_screen = 'main'
        self.screen.bgpic('images/main_menu.gif')
        self.pen.showturtle()

    def display_grid_options(self):
        """Displays grid size options, after selecting to start."""
        self.pen.cursor_pos = 2
        self.current_screen = 'grid_size'
        self.screen.bgpic('images/grid_size.gif')
        if os.name == 'posix':
            os.system('say choose your grid size.&')

    def start_game(self, width, height):
        """Starts the game with grid size choice and control setting."""
        gameObj = game.Game(width, height, self.relative_controls)
        gameObj.start_game()

    def start_menu(self):
        """Main menu loop. Creates cursor, displays main menu, and plays bgm."""
        self.create_screen()
        self.pen = turtle.Turtle()
        self.pen.shapesize(stretch_wid=3, stretch_len=3, outline=None)
        self.pen.cursor_pos = 3
        self.pen.pencolor('#40BBE3')
        self.pen.penup()
        # Stop music when returning from game and restart main menu music
        if os.name == 'posix':
            os.system('killall afplay')
            os.system('afplay sounds/main_menu.m4a&')
        # Change cursor position based on keybindings
        while True:
            turtle.update()
            self.set_cursor_master()
            self.keyboard_bindings()

if __name__ == '__main__':
    if sys.version_info[0] < 3:
        raise SystemExit('Python 3 required!')
    menu = MainMenu()
    menu.start_menu()
