#!/usr/bin/env python3

import turtle
import random
import time
import os

# Welcome to Turtle TRON! The object of the game is to stay alive the longest by not crashing into the walls
# or the opponent's trails. Game resets when either player crashes.
# Options: Grid size

# Currently set to relative key bindings. I need the menu class to save a class attribute
# that stores the controls setting.

class Game(object):
    """Creates screen, draws border, creates all sprites, maps keys, draws score, and
    runs game loop."""

    game_on = False

    def __init__(self, width=None, height=None, relative_controls=True):
        self.width = width
        self.height = height
        self.relative_controls = relative_controls

    def screen_size(self):
        """Only used if script runs directly."""
        choices = ['small', 'medium', 'large']
        size = ''
        while size not in choices:
            size = input('Grid size: (Small, Medium, Large) ').lower().strip()
            if size == 'small':
                return (640, 480)
            elif size == 'medium':
                return (800, 600)
            elif size == 'large':
                return (1024, 768)
            else:
                print('{} is not a valid size.'.format(size))

    def create_screen(self):
        """If run directly, creates screen based on user choice from self.screen_size().
        Otherwise, screen is automatically created with arguments from main.py script."""
        if not self.width or not self.height:
            self.width, self.height = self.screen_size()
        self.screen = turtle.Screen()
        self.screen.bgcolor('black')
        self.screen.setup(self.width, self.height, startx=None, starty=None)
        self.screen.title('TRON')
        self.screen.tracer(0)

    def draw_border(self):
        """Border is drawn from the width and height, starting in upper
        right hand corner. Each side is 50 pixels from the edge of the screen.
        The border coordinates will be used for border detection as well."""
        self.x_boundary = (self.width / 2) - 50
        self.y_boundary = (self.height / 2) - 50
        self.pen.color('blue')
        self.pen.penup()
        self.pen.setposition(self.x_boundary, self.y_boundary)
        self.pen.pendown()
        self.pen.pensize(3)
        self.pen.speed(0)
        self.pen.setheading(180) # Start drawing west
        # Square is drawn
        for side in range(4):
            # Vertical
            if side % 2:
                self.pen.forward(self.height - 100)
                self.pen.left(90)
            # Horizontal
            else:
                self.pen.forward(self.width - 100)
                self.pen.left(90)
        self.pen.penup()
        self.pen.hideturtle()

    def boundary_check(self, player):
        """Checks if light cycle is out of bounds using border coord.
        Deviation of 3 on edge to cosmetically match impact."""
        if ((player.xcor() < (-self.x_boundary + 3)) or (player.xcor() > (self.x_boundary - 3)) or
            (player.ycor() < (-self.y_boundary + 3)) or (player.ycor() > (self.y_boundary - 3))):
                for particle in self.particles:
                    particle.change_color(player)
                    particle.explode(player.xcor(), player.ycor())
                player.lives -= 1
                player.status = player.CRASHED

    def position_range_adder(self, player_positions):
        """If speed is > 1, the positions aren't recorded in between the speed. Therefore,
        this function is needed to fill in the gaps and append the missing positions"""
        prev_x_pos, prev_y_pos = player_positions[-2] # tuple unpacking
        next_x_pos, next_y_pos = player_positions[-1]
        positions_range = []
        # X coord are changing and the difference between them is greater than 1
        if abs(prev_x_pos - next_x_pos) > 1:
            start = min(prev_x_pos, next_x_pos) + 1
            end = max(prev_x_pos, next_x_pos)
            for x_position in range(start, end):
                coord = (x_position, prev_y_pos)
                positions_range.append(coord)
        # Y coord are changing and the difference between them is greater than 1
        if abs(prev_y_pos - next_y_pos) > 1:
            start = min(prev_y_pos, next_y_pos) + 1
            end = max(prev_y_pos, next_y_pos)
            for y_position in range(start, end):
                coord = (prev_x_pos, y_position)
                positions_range.append(coord)
        # Unique coordinates to add
        if positions_range:
            for position in positions_range:
                if position not in player_positions:
                    player_positions.append(position)

    def create_player(self):
        """Two players are always created. P1 is blue.
        P2 is Yellow"""
        # Create player 1
        self.P1 = Player('P1', -100, 100)
        self.P1.speed(0)
        self.P1.color('#40BBE3')

        # Create player 2
        self.P2 = Player('P2', 100, -100)
        self.P2.speed(0)
        self.P2.color('#E3E329')

    def create_particles(self):
        """Creates particles list. All particles act in same manner."""
        self.particles = []
        # Number of particles
        for i in range(20):
            self.particles.append(Particle('square', 'white', 0, 0))

    def particles_explode(self, player):
        """Makes all particles explode at player crash position"""
        for particle in self.particles:
            particle.change_color(player)
            particle.explode(player.xcor(), player.ycor())

    def is_collision(self, player, other):
        """Collision check. Self and with other player."""
        # Player collides into own trail (suicide)
        for position in player.positions[-3:]: # 3 positions to cover speed gap (0 - 2)
            if position in player.positions[:-3]:
                player.lives -= 1
                # Particle explosion
                self.particles_explode(player)
                player.status = player.CRASHED

        # Player collides into other player.
        # Covers speed increase, thus 3 positions are checked
        for position in player.positions[-3:]:
            if position in other.positions:
                player.lives -= 1
                # Particle explosion
                self.particles_explode(player)
                player.status = player.CRASHED

    def set_relative_keyboard_bindings(self):
        """Maps relative controls to player movement."""
        turtle.listen()
        # Set P1 keyboard bindings
        turtle.onkeypress(self.P1.turn_left, 'a')
        turtle.onkeypress(self.P1.turn_right, 'd')
        turtle.onkeypress(self.P1.accelerate, 'w')
        turtle.onkeypress(self.P1.decelerate, 's')

        # Set P2 keyboard bindings
        turtle.onkeypress(self.P2.turn_left, 'Left')
        turtle.onkeypress(self.P2.turn_right, 'Right')
        turtle.onkeypress(self.P2.accelerate, 'Up')
        turtle.onkeypress(self.P2.decelerate, 'Down')

    def set_abs_keyboard_bindings(self):
        """Maps absolute controls to player movement."""
        turtle.listen()
        # Set P1 keyboard bindings
        if self.P1.heading() == 0: # East
            turtle.onkeypress(self.P1.turn_left, 'w')
            turtle.onkeypress(self.P1.turn_right, 's')
            turtle.onkeypress(self.P1.accelerate, 'd')
            turtle.onkeypress(self.P1.decelerate, 'a')
        elif self.P1.heading() == 90: # North
            turtle.onkeypress(self.P1.turn_left, 'a')
            turtle.onkeypress(self.P1.turn_right, 'd')
            turtle.onkeypress(self.P1.accelerate, 'w')
            turtle.onkeypress(self.P1.decelerate, 's')
        elif self.P1.heading() == 180: # West
            turtle.onkeypress(self.P1.turn_left, 's')
            turtle.onkeypress(self.P1.turn_right, 'w')
            turtle.onkeypress(self.P1.accelerate, 'a')
            turtle.onkeypress(self.P1.decelerate, 'd')
        elif self.P1.heading() == 270: # South
            turtle.onkeypress(self.P1.turn_left, 'd')
            turtle.onkeypress(self.P1.turn_right, 'a')
            turtle.onkeypress(self.P1.accelerate, 's')
            turtle.onkeypress(self.P1.decelerate, 'w')
        # Set P1 keyboard bindings
        if self.P2.heading() == 0: # East
            turtle.onkeypress(self.P2.turn_left, 'Up')
            turtle.onkeypress(self.P2.turn_right, 'Down')
            turtle.onkeypress(self.P2.accelerate, 'Right')
            turtle.onkeypress(self.P2.decelerate, 'Left')
        elif self.P2.heading() == 90: # North
            turtle.onkeypress(self.P2.turn_left, 'Left')
            turtle.onkeypress(self.P2.turn_right, 'Right')
            turtle.onkeypress(self.P2.accelerate, 'Up')
            turtle.onkeypress(self.P2.decelerate, 'Down')
        elif self.P2.heading() == 180: # West
            turtle.onkeypress(self.P2.turn_left, 'Down')
            turtle.onkeypress(self.P2.turn_right, 'Up')
            turtle.onkeypress(self.P2.accelerate, 'Left')
            turtle.onkeypress(self.P2.decelerate, 'Right')
        elif self.P2.heading() == 270: # South
            turtle.onkeypress(self.P2.turn_left, 'Right')
            turtle.onkeypress(self.P2.turn_right, 'Left')
            turtle.onkeypress(self.P2.accelerate, 'Down')
            turtle.onkeypress(self.P2.decelerate, 'Up')


    def draw_score(self):
        """Using a turtle, this draws the score on the screen once, then clears once
        the score changes. Start position is upper left corner."""
        self.score_pen.clear()
        self.score_pen.setposition((self.width / -2) + 75, (self.height / 2) - 40)
        self.score_pen.pendown()
        self.score_pen.color('white')
        p1lives = 'P1: %s' % (self.P1.lives * '*')
        p2lives = 'P2: %s' % (self.P2.lives * '*')
        self.score_pen.write(p1lives, font=("Verdana", 18, "bold"))
        self.score_pen.penup()
        self.score_pen.hideturtle()
        self.score_pen.setposition((self.width / -2) + 205, (self.height / 2) - 40)
        self.score_pen.pendown()
        self.score_pen.write(p2lives, font=("Verdana", 18, "bold"))
        self.score_pen.penup()
        self.score_pen.hideturtle()

    def display_winner(self, player, other):
        """Once game loop finishes, this runs to display the winner."""
        self.score_pen.setposition(0, 0)
        self.score_pen.pendown()
        if player.lives > 0:
            winner = player.name
        else:
            winner = other.name
        self.score_pen.write(winner + ' wins!', align='center', font=("Verdana", 36, "bold"))

    def start_game(self):
        """All players are set into motion, boundary checks, and collision checks
        run continuously until a player runs out of lives."""

        self.create_screen()
        self.pen = turtle.Turtle()
        self.draw_border()
        self.create_player()
        self.create_particles()
        self.score_pen = turtle.Turtle()
        self.draw_score()
        self.game_on = True
        # Start bgm
        if os.name == 'posix':
            os.system('afplay sounds/son_of_flynn.m4a&')
            os.system('say grid is live!')

        while self.P1.lives > 0 and self.P2.lives > 0:
            # Updates screen only when loop is complete
            turtle.update()
            # Set controls based on menu setting
            if self.relative_controls:
                self.set_relative_keyboard_bindings()
            else:
                self.set_abs_keyboard_bindings()

            # Set players into motion
            self.P1.forward(self.P1.fd_speed)
            self.P2.forward(self.P2.fd_speed)

            # Particle movement
            for particle in self.particles:
                particle.move()

            # Player boundary checks
            self.boundary_check(self.P1)
            self.boundary_check(self.P2)

            # Coercing coordinates and appending to list
            self.P1.convert_coord_to_int()
            self.P1.positions.append(self.P1.coord)
            # Start evaluating positions for gaps
            if len(self.P1.positions) > 2:
                self.position_range_adder(self.P1.positions)
                self.is_collision(self.P1, self.P2)

            self.P2.convert_coord_to_int()
            self.P2.positions.append(self.P2.coord)
            # Start evaluating positions for gaps
            if len(self.P2.positions) > 2:
                self.position_range_adder(self.P2.positions)
                self.is_collision(self.P2, self.P1)

            if self.P1.status == self.P1.CRASHED or self.P2.status == self.P2.CRASHED:
                self.P1.reset_players(self.P2)
                if os.name == 'posix':
                    os.system('afplay sounds/explosion.wav&')
                self.draw_score()
        # Game ends
        self.display_winner(self.P1, self.P2)
        self.game_on = False
        time.sleep(3)
        self.screen.clear()
        if os.name == 'posix':
            os.system('killall afplay')


class Player(turtle.Turtle):

    CRASHED = 'crashed'
    READY = 'ready'

    def __init__(self, name, start_x, start_y):
        super(Player, self).__init__()
        self.name = name
        self.fd_speed = 1
        self.pensize(2)
        self.start_x = start_x
        self.start_y = start_y
        self.setposition(start_x, start_y)
        self.positions = []
        self.coord = (self.start_x, self.start_y)
        self.lives = 5
        self.status = self.READY

    def turn_left(self):
        """90 Degree left turn."""
        self.left(90)

    def turn_right(self):
        """90 Degree right turn."""
        self.right(90)

    def accelerate(self):
        """Min. speed = 1, Max. speed = 2."""
        if self.fd_speed < 2:
            self.fd_speed += 1
            self.forward(self.fd_speed) # Needs to be run only if speed changes

    def decelerate(self):
        """Min. speed = 1, therefore player can never stop"""
        if self.fd_speed > 1:
            self.fd_speed -= 1
            self.forward(self.fd_speed) # Needs to be run only if speed changes

    def convert_coord_to_int(self):
        """Convert coordinates to integers for more accurate collision detection"""
        x, y = self.pos()
        x = int(x)
        y = int(y)
        self.coord = (x, y)

    def crash(self):
        """Removes light cycle from screen"""
        self.penup()
        self.clear()
        self.respawn()

    def respawn(self):
        """Respawns light cycle to default location, resets speed to 1, and
        resets the position list."""
        self.status = self.READY
        self.setposition(self.start_x, self.start_y)
        self.setheading(random.randrange(0, 360, 90))
        self.fd_speed = 1
        self.pendown()
        self.positions = []

    def reset_players(self, other):
        """Resets both players"""
        self.crash()
        other.crash()


class Particle(turtle.Turtle):
    """This class is only used to create particle effects when there is a crash."""
    def __init__(self, spriteshape, color, start_x, start_y):
        turtle.Turtle.__init__(self, shape = spriteshape)
        self.shapesize(stretch_wid=.1, stretch_len=.3, outline=None)
        self.speed(0) # Refers to animation speed
        self.penup()
        self.color(color)
        self.fd_speed = 10
        self.hideturtle()
        self.frame = 0

    def explode(self, start_x, start_y):
        self.frame = 1
        self.showturtle()
        self.setposition(start_x, start_y)
        self.setheading(random.randint(0, 360))

    def move(self):
        if self.frame > 0:
            self.forward(self.fd_speed)
            self.frame += 1
        if self.frame > 10:
            self.frame = 0
            self.hideturtle()
            self.setposition(0, 0)

    def change_color(self, player):
        pencolor, fillcolor = player.color()
        self.color(pencolor)

if __name__ == '__main__':
    gameObj = Game()
    gameObj.start_game()
