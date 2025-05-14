# main.py
import pygame
import gameLevel1

if __name__ == "__main__":
    pygame.init()
    gameLevel1.running = True  # 确保可以控制退出逻辑

    while gameLevel1.running:
        gameLevel1.clock.tick(60)
