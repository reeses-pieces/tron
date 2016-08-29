#!/usr/bin/env python3

import turtle
import random
import time
import os

# Welcome to Turtle TRON! The object of the game is to stay alive the longest by not crashing into the walls
# the opponent's trails, or the boundaries. Game resets when either player crashes.
# Options: Grid size

# Currently set to absolute key bindings.

class Game(object):
    """Creates screen, draws border, creates all sprites, maps keys, draws score, and
    runs game loop."""

    game_on = False

    def __init__(self, width=None, height=None, relative_controls=False):
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
                self.particles_explode(player)
                player.lives -= 1
                player.status = player.CRASHED

    def position_range_adder(self, player_positions):
        """If speed is > 1, the positions aren't recorded between the speed gap. Therefore,
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

    def create_player(self, number=2):
        """Two players are always created. P1 is blue.
        P2 is Yellow"""

        self.players = []
        colors = ['#40BBE3','#E3E329']
        
        for i in range(number):
            random_x = random.randint(-(self.width / 2) + 100, (self.width / 2) - 100 )
            random_y = random.randint(-(self.height / 2) + 100, (self.height / 2) - 100 )
            self.players.append(Player('P' + str(i + 1), random_x, random_y))
            self.players[i].color(colors[i])

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
        # Player collides into own trail (suicide) or into opponenet
        if player.pos() in player.positions[:-6] or player.pos() in other.positions:

        # for position in player.positions[-3:]: # 3 positions to cover speed gap (0 - 2)
        #     if position in player.positions[:-3] or position in other.positions:
                player.lives -= 1
                # Particle explosion
                self.particles_explode(player)
                player.status = player.CRASHED

    def set_relative_keyboard_bindings(self):
        """Maps relative controls to player movement."""
        # Set P1 keyboard bindings
        turtle.onkeypress(self.players[0].turn_left, 'a')
        turtle.onkeypress(self.players[0].turn_right, 'd')
        turtle.onkeypress(self.players[0].accelerate, 'w')
        turtle.onkeypress(self.players[0].decelerate, 's')

        # Set P2 keyboard bindings
        turtle.onkeypress(self.players[1].turn_left, 'Left')
        turtle.onkeypress(self.players[1].turn_right, 'Right')
        turtle.onkeypress(self.players[1].accelerate, 'Up')
        turtle.onkeypress(self.players[1].decelerate, 'Down')

    def set_abs_keyboard_bindings(self):
        """Maps absolute controls to player movement."""
        
        # Set P1 keyboard bindings
        if self.players[0].heading() == 0: # East
            self.abs_key_mapper(self.players[0], 'w', 's', 'd', 'a')
        elif self.players[0].heading() == 90: # North
            self.abs_key_mapper(self.players[0], 'a', 'd', 'w', 's')
        elif self.players[0].heading() == 180: # West
            self.abs_key_mapper(self.players[0], 's', 'w', 'a', 'd')
        elif self.players[0].heading() == 270: # South
            self.abs_key_mapper(self.players[0], 'd', 'a', 's', 'w')
        # Set P2 keyboard bindings
        if self.players[1].heading() == 0: # East
            self.abs_key_mapper(self.players[1], 'Up', 'Down', 'Right', 'Left')
        elif self.players[1].heading() == 90: # North
            self.abs_key_mapper(self.players[1], 'Left', 'Right', 'Up', 'Down')
        elif self.players[1].heading() == 180: # West
            self.abs_key_mapper(self.players[1], 'Down', 'Up', 'Left', 'Right')
        elif self.players[1].heading() == 270: # South
            self.abs_key_mapper(self.players[1], 'Right', 'Left', 'Down', 'Up')            

    def abs_key_mapper(self, player, left, right, accel, decel):
        turtle.onkeypress(player.turn_left, left)
        turtle.onkeypress(player.turn_right, right)
        turtle.onkeypress(player.accelerate, accel)
        turtle.onkeypress(player.decelerate, decel)


    def draw_score(self):
        """Using a turtle, this draws the score on the screen once, then clears once
        the score changes. Start position is upper left corner."""
        self.score_pen.clear()
        self.score_pen.setposition((self.width / -2) + 75, (self.height / 2) - 40)
        self.score_pen.pendown()
        self.score_pen.color('white')
        p1lives = 'P1: %s' % (self.players[0].lives * '*')
        p2lives = 'P2: %s' % (self.players[1].lives * '*')
        self.score_pen.write(p1lives, font=("Verdana", 18, "bold"))
        self.score_pen.penup()
        self.score_pen.hideturtle()
        self.score_pen.setposition((self.width / -2) + 205, (self.height / 2) - 40)
        self.score_pen.pendown()
        self.score_pen.write(p2lives, font=("Verdana", 18, "bold"))
        self.score_pen.penup()
        self.score_pen.hideturtle()

    def is_game_over(self):
        if self.players[0].lives == 0 or self.players[1].lives == 0:
            return True

    def display_winner(self, player, other):
        """Once game loop finishes, this runs to display the winner."""
        self.score_pen.setposition(0, 0)
        self.score_pen.pendown()
        if player.lives > 0:
            winner = player.name
        else:
            winner = other.name
        self.score_pen.write(winner + ' wins!', align='center', font=("Verdana", 36, "bold"))

    def reset(self):
        for player in self.players:
            player.crash()

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

        while self.game_on:
            # Updates screen only when loop is complete
            turtle.update()
            # Set controls based on menu setting
            if self.relative_controls:
                self.set_relative_keyboard_bindings()
            else:
                self.set_abs_keyboard_bindings()

            # Activate key mappings
            turtle.listen()

            # Set players into motion, boundary check,
            for player in self.players:
                player.forward(player.fd_speed)
                self.boundary_check(player)
                

            # Particle movement
            for particle in self.particles:
                particle.move()

            # Coercing coordinates and appending to list
            for player in self.players:
                # player.convert_coord_to_int()
                player.positions.append(player.pos())
            # Start evaluating positions for gaps
                if len(player.positions) > 2:
                    self.position_range_adder(player.positions)
                    

            # self.players[1].convert_coord_to_int()
            # self.players[1].positions.append(self.players[1].coord)
            # Start evaluating positions for gaps
            self.is_collision(self.players[1], self.players[0])
            self.is_collision(self.players[0], self.players[1])

            # If a player crashes
            for player in self.players:
                if player.status == player.CRASHED:
                    self.reset()
                    if os.name == 'posix':
                        os.system('afplay sounds/explosion.wav&')
                    self.draw_score()
        
            if self.is_game_over():
                self.game_on = False

        # Game ends
        self.display_winner(self.players[0], self.players[1])
        # time.sleep(3)
        self.screen.clear()
        if os.name == 'posix':
            os.system('killall afplay')


class Player(turtle.Turtle):

    CRASHED = 'crashed'
    READY = 'ready'

    def __init__(self, name, start_x, start_y):
        super(Player, self).__init__()
        self.name = name
        self.speed(0)
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
