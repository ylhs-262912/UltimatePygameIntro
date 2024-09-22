from operator import contains
from sys import exit
import pygame
from random import randint
import classes
from constants import *

def DisplayScore():
    time = pygame.time.get_ticks() - startTime
    time = int(time / 1000.0)
    score = classes.text(f'Score: {time}', (64, 64, 64))
    score.rect.center = (SCREEN_WIDTH/2, 50)
    pygame.draw.rect(screen, pygame.Color("#c0e8ec"), score.rect)
    screen.blit(score.img, score.rect)
    return time

def ProcessEvents():
    for value, timer in enumerate(Timers):
        Timers[timer] = False
    for event in pygame.event.get():
        isQuit = event.type == pygame.QUIT
        isKeyEvent = event.type == pygame.KEYDOWN or event.type == pygame.KEYUP

        if isQuit:
            pygame.quit()
            exit()

        value = True
        if event.type == pygame.KEYUP:
            value = False
        if isKeyEvent and event.key in Input:
            Input[event.key] = value


        for timer in Timers.keys():
            if event.type == timer:
                Timers[timer] = True

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pixel Runner")
clock = pygame.time.Clock()
startTime = pygame.time.get_ticks()

font = pygame.font.Font("font/Pixeltype.ttf", 50)

sky = pygame.image.load("graphics/sky.png").convert()
skyX = 0
ground = pygame.image.load("graphics/ground.png").convert()
groundX = 0

player = classes.player()

dusts : list[classes.dust] = []

obstacles = []
obstacleColliders = []

Input = {pygame.K_SPACE: False}

Timers = {OBSTACLE_TIMER: False, ENEMY_ANIMATION_TIMER: False}

score = 0
highScore = 0


pygame.time.set_timer(OBSTACLE_TIMER, 900)
walkTimer = 0
pygame.time.set_timer(ENEMY_ANIMATION_TIMER, 300)

canJump = False

backgroundMusic = pygame.mixer.Sound("audio/music.wav")
backgroundMusic.set_volume(.2)
backgroundMusic.play(loops=-1)
jumpSound = pygame.mixer.Sound("audio/jump.mp3")
jumpSound.set_volume(.5)

class GameState():
    VALID_STATE = ["Menu", "Game"]
    __state = "Menu"

    def GetFunc(self, funcName):
        # if you don't know how getattr works, read the docs
        func = getattr(self, funcName, f":Nonexistent function {funcName}()")
        if type(func) is str:
            raise RuntimeError(func)
        return func

    def Transition(self, previousState, state):
        funcName = f"Transition{previousState}To{state}"
        func = self.GetFunc(funcName)
        func()

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        if not contains(self.VALID_STATE, state):
            raise RuntimeError(f"Invalid state of game: {state}")
        previousState = self.__state
        self.__state = state
        self.Transition(previousState, state)

    def DoLogic(self):
        funcName = f"Do{self.state}Logic"
        func = self.GetFunc(funcName)
        func()

    def Render(self):
        funcName = f"Render{self.state}"
        func = self.GetFunc(funcName)
        func()

    def TransitionGameToMenu(self):
        global highScore
        if score >= highScore:
            highScore = score

    def TransitionMenuToGame(self):
        global startTime, obstacles, obstacleColliders, skyX, groundX, dusts
        startTime = pygame.time.get_ticks()
        player.collider = player.img.get_rect(bottomleft=(PLAYER_STARTING_X, FLOOR_PLANE))
        obstacles = []
        obstacleColliders = []
        dusts = []
        player.yVelocity = 0
        skyX, groundX = 0, 0


    def DoGameLogic(self):
        global canJump
        canJump = player.collider.bottom >= FLOOR_PLANE
        if Input[pygame.K_SPACE] and canJump:
            player.yVelocity = -20
            jumpSound.play()
            dusts.append(classes.dust(player.collider.midbottom))

        player.yVelocity += GRAVITY
        player.y += player.yVelocity
        player.collider = player.img.get_rect(topleft=(150, player.y))
        if player.collider.bottom > FLOOR_PLANE:
            player.collider.bottom = FLOOR_PLANE
            player.yVelocity = 0

        index = 0
        while index < len(obstacles):
            obstacle = obstacles[index]
            obstacle.x -= SNAIL_SPEED
            if obstacle.x < -SNAIL_SCREEN_DISTANCE:
                obstacles.remove(obstacle)
                obstacleColliders.remove(obstacle.collider)
            index += 1
        if Timers[OBSTACLE_TIMER]:
            if randint(0, 2):
                obstacle = classes.snail()
            else:
                obstacle = classes.fly()
            obstacles.append(obstacle)
            obstacleColliders.append(obstacle.collider)

        for collider in obstacleColliders:
            if player.collider.colliderect(collider):
                self.state = "Menu"
                break



    def DoMenuLogic(self):
        global Input
        if Input[pygame.K_SPACE]:
            self.state = "Game"

    def RenderGame(self):
        global score, walkTimer, canJump, skyX, groundX, ground

        skyX -= 1
        if skyX <= - sky.get_width() / 2:
            skyX = 0
        groundX -= 3
        if groundX <= - ground.get_width() / 2:
            groundX = 0


        walkTimer += 1
        if walkTimer == 10:
            walkTimer = 0
            player.frameCount += 1

        if Timers[ENEMY_ANIMATION_TIMER]:
            for enemy in obstacles:
                enemy.frameCount += 1

        screen.blit(sky, (skyX, 0))
        screen.blit(ground, (groundX, FLOOR_PLANE))
        score = DisplayScore()

        for obstacle in obstacles:
            screen.blit(obstacle.img, obstacle.collider)

        if canJump:
            player.activeAnimation = "walk"
        else:
            player.activeAnimation = "jump"

        screen.blit(player.img, player.collider)

        index = 0
        while index < len(dusts):
            dust = dusts[index]
            screen.blit(dust.img, dust.collider)
            dust.alpha = dust.alpha - 8
            dust.img.set_alpha(dust.alpha)
            dust.time += 1
            if dust.time % 2:
                dust.collider.centerx += dust.velocity.x
                dust.collider.centery += dust.velocity.y
            if dust.time == dust.despawn:
                dusts.remove(dust)
                index -= 1
            index += 1


    def RenderMenu(self):
        display = pygame.Surface((SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        display.fill((94, 129, 162))

        title = classes.text("Pixel Runner", (111, 196, 169))
        title.rect.center = (SCREEN_WIDTH/4, 30)

        highScoreText = classes.text(f"High score: {highScore}", (111, 196, 169))
        highScoreText.rect.center = (SCREEN_WIDTH/4, 60)

        subtext = classes.text("Press space to run", (111, 196, 169))
        subtext.rect.center = (SCREEN_WIDTH/4, 170)

        playerImg = pygame.image.load("graphics/Player/player_stand.png")
        playerRect = playerImg.get_rect(center = (SCREEN_WIDTH/4, 110))

        display.blit(title.img, title.rect)
        display.blit(highScoreText.img, highScoreText.rect)
        display.blit(subtext.img, subtext.rect)
        display.blit(playerImg, playerRect)

        screen.blit(pygame.transform.scale(display, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))

Game = GameState()

while True:
    ProcessEvents()

    Game.DoLogic()

    screen.fill("black")
    Game.Render()
    pygame.display.update()
    clock.tick(60)