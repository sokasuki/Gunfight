
import os, sys
import math
from enum import Enum
import pygame

#Constants
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600
BLOCK_SIZE = 40
CHARACTER_SIZE = BLOCK_SIZE
BULLET_SIZE = 5
RADAR_WIDTH = 5
RADAR_LENGTH = 3 * BLOCK_SIZE
HEARING_RANGE = 9 * BLOCK_SIZE

CHARACTER_SPEED = 10
BULLET_SPEED = 20

FPS = 60

#Colours
WHITE = (250, 250, 250)
BLACK = (0, 0, 0)
RED = (250, 0, 0)
GREEN = (0, 250, 0)
BLUE = (0, 0, 250)
SILVER = (192, 192, 192)

#Initialize Everything 
pygame.init()
pygame.display.set_caption('Gunfight')
# pygame.mouse.set_visible(0)
clock = pygame.time.Clock()

#Create The Backgound
gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))

#Object containers
allObjects = []
walls = []
enemies = []
bullets = []
allCharacters = []
radars = []

#Map
game_map = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
			[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 3, 1],
			[1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1],
			[1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 4, 0, 1, 1, 1], 
			[1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
			[1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1], 
			[1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
			[1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
			[1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
			[1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
			[1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
			[1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
			[1, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
			[1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
			[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

#Enumerator for directions
class Direction(Enum):
	LEFT = 1
	RIGHT = 2
	UP = 3
	DOWN = 4


class Radar(pygame.sprite.Sprite):
	#TODO: Change to a cone shaped sprite
	def __init__(self, start_x, start_y, radius, direction):
		self.x = start_x
		self.y = start_y
		self.radius = radius
		self.facing_direction = direction
		self.rect = pygame.Rect(self.x + self.radius, self.y - self.radius, RADAR_LENGTH, RADAR_WIDTH)
		self.blocked = self.blocked_by_wall()[0]
		radars.append(self)

	def destroy(self):
		radars.remove(self)
		del self

	def draw(self):
		if self.facing_direction == Direction.RIGHT:
			self.rect = pygame.Rect(self.x + self.radius/2, self.y - self.radius/2, RADAR_LENGTH, RADAR_WIDTH)
			if self.blocked_by_wall()[0]:
				self.blocked = True
				distance_to_wall = self.blocked_by_wall()[1].x - (self.x + self.radius/2)
				self.rect = pygame.Rect(self.x + self.radius/2, self.y - self.radius/2, distance_to_wall, RADAR_WIDTH)

		elif self.facing_direction == Direction.LEFT:
			self.rect = pygame.Rect(self.x - self.radius/2 - RADAR_LENGTH, self.y - self.radius/2, RADAR_LENGTH, RADAR_WIDTH)
			if self.blocked_by_wall()[0]:
				self.blocked = True
				distance_to_wall = self.x - self.radius/2 - self.blocked_by_wall()[1].x - BLOCK_SIZE
				self.rect = pygame.Rect(self.x - self.radius/2 - distance_to_wall, self.y - self.radius/2, distance_to_wall, RADAR_WIDTH)

		elif self.facing_direction == Direction.UP:
			self.rect = pygame.Rect(self.x - self.radius/2, self.y - self.radius/2 - RADAR_LENGTH, RADAR_WIDTH, RADAR_LENGTH)
			if self.blocked_by_wall()[0]:
				self.blocked = True
				distance_to_wall = self.y - self.radius/2 - self.blocked_by_wall()[1].y - BLOCK_SIZE
				self.rect = pygame.Rect(self.x - self.radius/2, self.y - self.radius/2 - distance_to_wall, RADAR_WIDTH, distance_to_wall)

		elif self.facing_direction == Direction.DOWN:
			self.rect = pygame.Rect(self.x - self.radius/2, self.y + self.radius/2, RADAR_WIDTH, RADAR_LENGTH)
			if self.blocked_by_wall()[0]:
				self.blocked = True
				distance_to_wall = self.blocked_by_wall()[1].y - self.y - self.radius/2
				self.rect = pygame.Rect(self.x - self.radius/2, self.y + self.radius/2, RADAR_WIDTH, distance_to_wall)

		pygame.draw.rect(gameDisplay, RED, self.rect, 1)

	def blocked_by_wall(self):
		for wall in walls:
			if self.rect.colliderect(wall):
				return (True, wall)
		self.blocked = False
		return (False, None)


class Bullet(pygame.sprite.Sprite):
	#TODO: Follow character class and remove self.x make into self.rect.x
	def __init__(self, start_x, start_y, direction):
		self.velocity = 0
		self.facing_direction = direction
		self.size = BULLET_SIZE
		self.colour = BLUE
		self.direction = direction
		self.rect = pygame.Rect(start_x, start_y, self.size, self.size)
		bullets.append(self)
		allObjects.append(self)

	def fire(self):
		self.velocity = BULLET_SPEED
		if self.direction == Direction.UP:
			self.rect.y -= self.velocity
		elif self.direction == Direction.DOWN:
			self.rect.y += self.velocity
		elif self.direction == Direction.RIGHT:
			self.rect.x += self.velocity
		elif self.direction == Direction.LEFT:
			self.rect.x -= self.velocity

	def draw(self):
		pygame.draw.rect(gameDisplay, self.colour, self.rect)

	def destroy(self):
		bullets.remove(self)
		allObjects.remove(self)
		del self

	def is_collided_with(self, other):
		return self.rect.colliderect(other.rect)


class Character(pygame.sprite.Sprite):
	def __init__(self, start_x, start_y, facing_direction):
		self.size = CHARACTER_SIZE
		self.velocity = 0
		self.facing_direction = facing_direction
		self.rect = pygame.Rect(start_x, start_y, self.size, self.size)
		self.radar = Radar(start_x, start_y, self.size/2, self.facing_direction)
		allObjects.append(self)
		allCharacters.append(self)

	def walk(self, direction):
		if direction == Direction.LEFT:
			self.move_single_axis(- CHARACTER_SPEED, 0)
		if direction == Direction.RIGHT:
			self.move_single_axis(CHARACTER_SPEED, 0)
		if direction == Direction.UP:
			self.move_single_axis(0, - CHARACTER_SPEED)
		if direction == Direction.DOWN:
			self.move_single_axis(0, CHARACTER_SPEED)

	def move_single_axis(self, dx, dy):
		# Move the rect
		self.rect.x += dx
		self.rect.y += dy

		#If you collide with a wall, move out based on velocity
		for wall in walls:
			if self.rect.colliderect(wall.rect):
				if dx > 0: # Moving right; Hit the left side of the wall
					self.rect.right = wall.rect.left
				if dx < 0: # Moving left; Hit the right side of the wall
					self.rect.left = wall.rect.right
				if dy > 0: # Moving down; Hit the top side of the wall
					self.rect.bottom = wall.rect.top
				if dy < 0: # Moving up; Hit the bottom side of the wall
					self.rect.top = wall.rect.bottom

	def orient(self, pos_x, pos_y):
		#TODO: Left/Right facing is really hard to achieve, make it easier
		if self.rect.x > pos_x:
			if self.rect.y == pos_y:
				self.facing_direction = Direction.LEFT
			if self.rect.y > pos_y:
				theta = math.degrees( math.atan( (self.rect.y - pos_y) / (self.rect.x - pos_x) ) )
				if theta > 45:
					self.facing_direction = Direction.UP
				else:
					self.facing_direction = Direction.LEFT

		if self.rect.x > pos_x:
			if self.rect.y == pos_y:
				self.facing_direction = Direction.LEFT
			if self.rect.y < pos_y:
				theta = math.degrees( math.atan( (self.rect.y - pos_y) / (self.rect.x - pos_x) ) )
				if theta > 45:
					self.facing_direction = Direction.LEFT
				else:
					self.facing_direction = Direction.DOWN

		if self.rect.x < pos_x:
			if self.rect.y == pos_y:
				self.facing_direction == Direction.RIGHT
			if self.rect.y < pos_y:
				theta = math.degrees( math.atan( (self.rect.y - pos_y) / (self.rect.x - pos_x) ) )
				if theta > 45:
					self.facing_direction = Direction.DOWN
				else:
					self.facing_direction = Direction.RIGHT

		if self.rect.x < pos_x:
			if self.rect.y == pos_y:
				self.facing_direction = Direction.RIGHT
			if self.rect.y > pos_y:
				theta = math.degrees( math.atan( (self.rect.y - pos_y) / (self.rect.x - pos_x) ) )
				if theta > 45:
					self.facing_direction = Direction.RIGHT
				else:
					self.facing_direction = Direction.UP		

	def shoot(self):
		#TODO: Countdown timer for gun
		if self.facing_direction == Direction.LEFT:
			bullet_params = (self.rect.x, self.rect.y + self.size/2, self.facing_direction)
		elif self.facing_direction == Direction.RIGHT:
			bullet_params = (self.rect.x + self.size, self.rect.y + self.size/2, self.facing_direction)
		elif self.facing_direction == Direction.UP:
			bullet_params = (self.rect.x + self.size/2 , self.rect.y, self.facing_direction)
		elif self.facing_direction == Direction.DOWN:
			bullet_params = (self.rect.x + self.size/2 , self.rect.y + self.size, self.facing_direction)

		bullet = Bullet(bullet_params[0], bullet_params[1], bullet_params[2])
		bullet.fire()

	def draw(self):
		#Remaking radar for new location
		self.radar.destroy()
		self.radar = Radar(self.rect.x, self.rect.y, self.size, self.facing_direction)
		self.radar.draw()

		#Draw character
		pygame.draw.rect(gameDisplay, self.colour, self.rect)


class Player(Character):
	def __init__(self, start_x, start_y, facing_direction):
		Character.__init__(self, start_x, start_y, facing_direction)
		self.colour = GREEN

	def check_if_hit(self):
		for enemy in enemies:
			if enemy.radar.rect.colliderect(self.rect):
				return True
		return False

	def die(self):
		pass


class Enemy(Character):
	def __init__(self, start_x, start_y, facing_direction):
		Character.__init__(self, start_x, start_y, facing_direction)
		self.colour = SILVER
		self.triggered = False
		enemies.append(self)

	def die(self):
		self.radar.destroy()
		enemies.remove(self)
		allObjects.remove(self)
		del self

	def listen(self, pos_x, pos_y):
		distance_x = math.fabs(self.rect.x - pos_x)
		distance_y = math.fabs(self.rect.y - pos_y)
		displacement = math.sqrt((distance_x**2) + (distance_y**2))
		if displacement < HEARING_RANGE:
			self.triggered = True
			self.target_x = pos_x
			self.target_y = pos_y

	def follow(self):
		#TODO: Stay triggered until the enemy reaches the target location
		if (self.target_x - 5) <= self.rect.x <= (self.target_x + 5) and (self.target_y - 5) <= self.rect.y <= (self.target_y + 5):
			self.triggered = False
		else:
			self.orient(self.target_x, self.target_y)
			if not self.radar.blocked:
				self.walk(self.facing_direction)
				return
			if self.rect.x > self.target_x:
				self.facing_direction = Direction.LEFT
				if not self.radar.blocked:
					self.walk(self.facing_direction)
					return
			if self.rect.x < self.target_x:
				self.facing_direction = Direction.RIGHT
				if not self.radar.blocked:
					self.walk(self.facing_direction)
					return
			if self.rect.y < self.target_y:
				self.facing_direction = Direction.DOWN
				if not self.radar.blocked:
					self.walk(self.facing_direction)
					return
			if self.rect.y > self.target_y:
				self.facing_direction = Direction.UP
				if not self.radar.blocked:
					self.walk(self.facing_direction)
					return
		

class Wall(pygame.sprite.Sprite):
	def __init__(self, start_x, start_y):
		self.x = start_x
		self.y = start_y
		self.size = BLOCK_SIZE
		self.colour = BLACK
		self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
		allObjects.append(self)
		walls.append(self)

	def draw(self):
		pygame.draw.rect(gameDisplay, self.colour, [self.x, self.y, self.size, self.size])

#Main Game 
def main():
	#Create the Backgound
	gameDisplay.fill(WHITE)

	#Create the Map
	for i, row in enumerate(game_map):
		for j, item in enumerate(row):
			if item == 1:
				Wall( j*BLOCK_SIZE, i*BLOCK_SIZE )
			if item == 2:
				player = Player( j*BLOCK_SIZE, i*BLOCK_SIZE, Direction.LEFT )
			if item == 3:
				Enemy( j*BLOCK_SIZE, i*BLOCK_SIZE, Direction.LEFT )
			if item == 4:
				Enemy( j*BLOCK_SIZE, i*BLOCK_SIZE, Direction.RIGHT )
			if item == 5:
				Enemy( j*BLOCK_SIZE, i*BLOCK_SIZE, Direction.UP )
			if item == 6:
				Enemy( j*BLOCK_SIZE, i*BLOCK_SIZE, Direction.DOWN )

	#Main Loop
	while True:
		clock.tick(FPS)

		#Controller
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				return
			if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
				return
			if e.type == pygame.MOUSEBUTTONDOWN:
				player.shoot()
				for enemy in enemies:
					enemy.listen( player.rect.x, player.rect.y )
		
		# Move the player if an arrow key is pressed
		key = pygame.key.get_pressed()
		if key[pygame.K_a]:
			player.walk(Direction.LEFT)
		if key[pygame.K_d]:
			player.walk(Direction.RIGHT)
		if key[pygame.K_w]:
			player.walk(Direction.UP)
		if key[pygame.K_s]:
			player.walk(Direction.DOWN)

		#Clear Screen
		gameDisplay.fill(WHITE)

		#Orient player direction
		mouse_pos = pygame.mouse.get_pos()
		player.orient( mouse_pos[0], mouse_pos[1] )

		#Fire bullets
		for bullet in bullets:
			bullet.fire()

		#Wall Collision Detection
		for wall in walls:
			for bullet in bullets:
				if bullet.is_collided_with(wall):
					bullet.destroy()

		#Check if any bullets hit a character
		for character in allCharacters:
			for bullet in bullets:
				if bullet.is_collided_with(character):
					character.die()
					bullet.destroy()

		if player.check_if_hit():
			print ("You've been hit!")

		#Enemy following
		for enemy in enemies:
			if enemy.triggered:
				enemy.follow()

		#Check if all enemies are dead
		if len(enemies) == 0:
			print ("You win!")

		#Draw every object
		for item in allObjects:	
			item.draw()

		pygame.display.update()

	#End Game
	pygame.quit()


if __name__ == '__main__':
	main()

quit()

# Object oriented advice from: http://ezide.com/games/writing-games.html
# Pygame tips from https: //www.pygame.org/docs/tut/ChimpLineByLine.html
# Pygame tutorial by: https://www.youtube.com/playlist?list=PL6gx4Cwl9DGAjkwJocj7vlc_mFU-4wXJq
# Collision tips from: http://www.pygame.org/project-Rect+Collision+Response-1061-.html
