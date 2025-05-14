import pygame
class BackGround:
        def __init__(self, path1,path2):
            pygame.init()
            self.image1 = pygame.image.load(path1)
            self.image2 = pygame.image.load(path2)
            w1, h1 = self.image1.get_size()
            w2, h2 = self.image2.get_size()
            self.window = pygame.display.set_mode((w1+w2, h1))
            self.window.blit(self.image1, (0, 0))
            self.window.blit(self.image2, (w1, 0))
            pygame.display.flip()

        def remake(self):
            w1, h1 = self.image1.get_size()
            w2, h2 = self.image2.get_size()
            self.window = pygame.display.set_mode((w1 + w2, h1))
            self.window.blit(self.image1, (0, 0))
            self.window.blit(self.image2, (w1, 0))
            pygame.display.update()


