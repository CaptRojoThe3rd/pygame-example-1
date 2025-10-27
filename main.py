
import pygame
from colorsys import hsv_to_rgb
from random import randint

# EASY-TO-EDIT CONSTANTS
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_BG_COLOR = (0x00, 0x00, 0x10)
FPS_LIMIT = 60

ENEMY_MIN_SIZE = 20
ENEMY_MAX_SIZE = 40
ENEMY_MIN_SPEED = 2
ENEMY_MAX_SPEED = 4
ENEMY_SPAWN_CHANCE = 10 # out of 1000

PLAYER_SIZE = 30
PLAYER_SPEED = 5
PLAYER_HEAL_SPEED = 10 # chance; out of 1000
PLAYER_COLOR = (0xff, 0xff, 0xff)

HEALTHBAR_BG_COLOR = (0x10, 0x10, 0x10)
HEALTHBAR_FG_COLOR = (0xff, 0x00, 0x00)

BULLET_SPEED = 10
BULLET_SIZE = 10
BULLET_COLOR = (0x80, 0x80, 0x80)


keys = {}
game_over: bool = False


class Entity():
	entities = [None] * 256

	def spawn(new: object) -> None:
		for i in range(255, -1, -1):
			if Entity.entities[i] != None:
				continue
			Entity.entities[i] = new
			return

	def updateAndRenderAll(window: pygame.Surface) -> None:
		for i, v in enumerate(Entity.entities):
			if v == None:
				continue
			ret = v.update()
			if not ret:
				Entity.entities[i] = None
				continue
			v.render(window)

	def __init__(self):
		self.x: int = 0
		self.y: int = 0
		self.xvel: int = 0
		self.yvel: int = 0

	def update(self) -> bool:
		self.x += self.xvel
		self.y += self.yvel
		return True

	def render(self, surf: pygame.Surface) -> None:
		pass


class Player(Entity):
	def __init__(self, map: list, id: int):
		super().__init__()
		self.x = 400
		self.y = 500
		self.health: int = 100
		self.just_fired: bool = False
		self.map: list = map
		for v in map:
			keys[v] = False
		self.id: int = id

	def update(self) -> bool:
		super().update()
		VECS = [(0, -PLAYER_SPEED), (0, PLAYER_SPEED), (-PLAYER_SPEED, 0), (PLAYER_SPEED, 0), (0, 0)]
		# Fire bullets
		if not keys[self.map[4]]:
			self.just_fired = False
		elif not self.just_fired:
			self.just_fired = True
			Entity.spawn(Bullet(self.x + (PLAYER_SIZE / 2), self.y - BULLET_SIZE))
		# Movement input
		self.xvel = 0
		self.yvel = 0
		for i, v in enumerate(self.map):
			if keys[v]:
				self.xvel += VECS[i][0]
				self.yvel += VECS[i][1]
		# Collision with enemies - also handle entities reaching bottom of screen
		for v in Entity.entities:
			if v == None:
				continue
			if not isinstance(v, Enemy):
				continue
			if ((v.x < self.x and self.x < (v.x + v.size)) and (v.y < self.y and self.y < (v.y + v.size))):
				self.health -= 1
				continue
			if ((self.x < v.x and v.x < (self.x + PLAYER_SIZE)) and (self.y < v.y and v.y < (self.y + PLAYER_SIZE))):
				self.health -= 1
				continue
			if (v.y > (WINDOW_HEIGHT - v.size)):
				self.health -= 2
		if randint(1, 1000) < PLAYER_HEAL_SPEED and self.health < 100:
			self.health += 1
		if self.health <= 0:
			game_over = True
			return False
		return True

	def render(self, surf: pygame.Surface) -> None:
		# Player is just a triangle
		pygame.draw.polygon(surf, PLAYER_COLOR, [(self.x + (PLAYER_SIZE / 2), self.y), (self.x, self.y + PLAYER_SIZE), 
				(self.x + PLAYER_SIZE, self.y + PLAYER_SIZE)])
		# Draw health bar
		pygame.draw.rect(surf, HEALTHBAR_BG_COLOR, pygame.Rect(10, 10 + (self.id * 50), 240, 40))
		pygame.draw.rect(surf, HEALTHBAR_FG_COLOR, pygame.Rect(20, 20 + (self.id * 50), 2.2 * self.health, 20))


class Enemy(Entity):
	def __init__(self):
		super().__init__()
		self.x = randint(0, WINDOW_WIDTH)
		self.yvel = randint(ENEMY_MIN_SPEED, ENEMY_MAX_SPEED)

		self.size: int = randint(ENEMY_MIN_SIZE, ENEMY_MAX_SIZE)
		hsv = hsv_to_rgb(randint(0, 360) / 360, 1, 1)
		self.color: tuple[int, int, int] = (int(hsv[0] * 255), int(hsv[1] * 255), int(hsv[2] * 255))

	def update(self) -> bool:
		super().update()
		# Bottom of screen
		if self.y >= WINDOW_HEIGHT:
			return False
		# Collision with bullets
		for i, v in enumerate(Entity.entities):
			if v == None:
				continue
			if not isinstance(v, Bullet):
				continue
			if ((v.x < self.x and self.x < (v.x + BULLET_SIZE)) and (v.y < self.y and self.y < (v.y + BULLET_SIZE))):
				Entity.entities[i] = None
				return False
			if ((self.x < v.x and v.x < (self.x + self.size)) and (self.y < v.y and v.y < (self.y + self.size))):
				Entity.entities[i] = None
				return False
		return True

	def render(self, surf: pygame.Surface) -> None:
		# Enemies are rectangles
		pygame.draw.rect(surf, self.color, pygame.Rect(self.x, self.y, self.size, self.size))


class Bullet(Entity):
	def __init__(self, x: int, y: int):
		super().__init__()
		self.x = x
		self.y = y
		self.yvel = -BULLET_SPEED

	def update(self) -> bool:
		super().update()
		return self.y > 0

	def render(self, surf: pygame.Surface) -> None:
		pygame.draw.rect(surf, BULLET_COLOR, pygame.Rect(self.x, self.y, BULLET_SIZE, BULLET_SIZE * 2))


def main() -> None:
	pygame.init()
	window: pygame.Surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
	clock: pygame.time.Clock = pygame.time.Clock()

	p1_map = [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_e]
	p2_map = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SLASH]

	Entity.spawn(Player(p1_map, 0))
	#Entity.spawn(Player(p2_map, 1))

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				# I wish Python had goto
				pygame.quit()
				return
			elif event.type == pygame.KEYDOWN:
				keys[event.key] = True
			elif event.type == pygame.KEYUP:
				keys[event.key] = False

		pygame.draw.rect(window, WINDOW_BG_COLOR, pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

		if randint(1, 1000) < ENEMY_SPAWN_CHANCE:
			Entity.spawn(Enemy())

		Entity.updateAndRenderAll(window)

		clock.tick(FPS_LIMIT)
		pygame.display.flip()
		

if __name__ == "__main__":
	main()
