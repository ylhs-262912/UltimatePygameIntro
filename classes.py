import pygame
from random import randint, uniform
from constants import *
from abc import ABC, abstractmethod

pygame.init()

class player():
    POSSIBLE_ANIMATIONS = ["walk", "jump"]
    walkAnimation : list[pygame.image] = None
    jumpAnimation : list[pygame.image] = None
    __activeAnimation = None
    __frameCount = 0
    collider = None
    yVelocity = None

    def GetAnimation(self, animation):
        animation += "Animation"
        animation = getattr(self, animation, f":Nonexistent animation list {animation}")
        if type(animation) is str:
            raise RuntimeError(animation)
        return animation

    @property
    def activeAnimation(self) -> str:
        return self.__activeAnimation

    @activeAnimation.setter
    def activeAnimation(self, activeAnimation: str):
        if not activeAnimation in self.POSSIBLE_ANIMATIONS:
            raise RuntimeError("Not possible Animation")
        self.__activeAnimation = activeAnimation
        animation = self.GetAnimation(activeAnimation)
        if not 0 <= self.frameCount < len(animation):
            self.frameCount = 0

    @property
    def frameCount(self) -> int:
        return self.__frameCount

    @frameCount.setter
    def frameCount(self, frameCount : int):
        Animation = self.GetAnimation(self.activeAnimation)
        if frameCount < 0:
            self.frameCount = frameCount + len(Animation)
            return
        if frameCount >= len(Animation):
            self.frameCount = frameCount - len(Animation)
            return
        self.__frameCount = frameCount

    @property
    def img(self) -> pygame.image:
        Animation = self.GetAnimation(self.activeAnimation)
        return Animation[self.frameCount]

    @img.setter
    def img(self, img : pygame.image):
        Animation = self.GetAnimation(self.activeAnimation)
        if not img in Animation:
            raise RuntimeError("image not in active animation, please set that first")
        self.frameCount = Animation.index(img)

    @property
    def y(self) -> int:
        return self.collider.top

    @y.setter
    def y(self, y: int):
        self.collider.top = y



    def __init__(self):
        self.walkAnimation = [pygame.image.load("graphics/player/player_walk_1.png").convert_alpha(),
                              pygame.image.load("graphics/player/player_walk_2.png").convert_alpha()]
        self.jumpAnimation =  [pygame.image.load("graphics/player/jump.png").convert_alpha()]
        self.activeAnimation = "walk"
        self.frameCount = 0
        self.collider = self.img.get_rect(bottomleft = (PLAYER_STARTING_X, FLOOR_PLANE))
        self.yVelocity = 0

class enemy(ABC):
    animation : list[pygame.image] = None
    __frameCount : int = None
    collider: pygame.Rect = None

    @property
    def x(self) -> int:
        return self.collider.left

    @x.setter
    def x(self, x: int):
        self.collider.left = x

    @property
    def img(self) -> pygame.image:
        return self.animation[self.frameCount]

    @img.setter
    def img(self, img: pygame.image):
        if not img in self.animation:
            raise RuntimeError("image not in animation")
        self.frameCount = self.animation.index(img)

    @property
    def frameCount(self) -> int:
        return self.__frameCount

    @frameCount.setter
    def frameCount(self, frameCount : int):
        if frameCount < 0:
            self.frameCount = frameCount + len(self.animation)
            return
        if frameCount >= len(self.animation):
            self.frameCount = frameCount - len(self.animation)
            return
        self.__frameCount = frameCount

class snail(enemy):
    def __init__(self):
        self.animation = [pygame.image.load("graphics/snail/snail1.png").convert_alpha(),
                          pygame.image.load("graphics/snail/snail2.png").convert_alpha()]
        self.frameCount = 0
        self.collider = self.img.get_rect(bottom = FLOOR_PLANE)
        self.x = SCREEN_WIDTH + randint(100, 300)

class fly(enemy):
    def __init__(self):
        self.animation = [pygame.image.load("graphics/Fly/Fly1.png").convert_alpha(),
                          pygame.image.load("graphics/Fly/Fly2.png").convert_alpha()]
        self.frameCount = 0
        self.collider = self.img.get_rect(topleft = (SCREEN_WIDTH + randint(100, 300), 120))

class text():
    font = pygame.font.Font("font/Pixeltype.ttf", 50)
    img : pygame.Surface = None
    rect : pygame.Rect = None

    def __init__(self, text, color):
        self.img = self.font.render(text, False, color)
        self.rect = self.img.get_rect()

class Vector2:
    __data: tuple[int | float] = (0, 0)
    isInt: bool = False

    @property
    def data(self) -> tuple[int | float]:
        return self.__data

    @data.setter
    def data(self, data: tuple[int | float]):
        if len(data) != 2:
            raise RuntimeError(f"number of args for Vector2 is not 2 but {len(data)}")
        if self.isInt:
            data = (int(data[0] + .5), int(data[1] + .5))
        self.__data = data


    @property
    def x(self) -> int | float:
        return self.data[0]

    @x.setter
    def x(self, x: int | float):
        self.data = (x, self.data[1])

    @property
    def y(self) -> int | float:
        return self.data[1]

    @y.setter
    def y(self, y: int | float):
        self.data = (self.data[0], y)

    def __init__(self, x: int | float = 0, y: int | float = 0, isInt = False):
        self.x = x
        self.y = y
        self.isInt = isInt

    def __getitem__(self, index):
        return self.data[index]

class dust():
    img : pygame.image = None
    alpha: int = 255
    collider : pygame.Rect = None
    velocity : Vector2() = None
    time : int = 0
    despawn: int = 0


    def __init__(self, playerPosition):
        self.img = pygame.image.load("graphics/dust.png").convert_alpha()
        self.alpha = 255
        self.collider = self.img.get_rect()
        self.collider.center = playerPosition
        self.collider.centerx += randint(-25, -19)
        self.velocity = Vector2(uniform(-.8, -.6), uniform(-.8, -.6))
        self.time = 0
        self.despawn = randint(25, 36)
