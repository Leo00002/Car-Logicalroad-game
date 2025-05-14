import pygame
import math
from enum import Enum
from Component import Component  # 假设已存在Component类
class Car(pygame.sprite.Sprite):
    def __init__(self, path_or_surface, rotate_angle=0, scale=1.0, width_scale=1.0, height_scale=1.0):
        super().__init__()
        self.max_speed = 5
        self.acceleration = 0.2
        self.current_speed = 0
        self.direction = pygame.math.Vector2(1, 0)
        self._load_image(path_or_surface)
        self._process_image(rotate_angle, scale, width_scale, height_scale)
        self.rect = self.image.get_rect()

    def _load_image(self, path_or_surface):
        if isinstance(path_or_surface, str):
            try:
                self._original_image = pygame.image.load(path_or_surface).convert_alpha()
            except pygame.error:
                self._original_image = pygame.Surface((50, 30), pygame.SRCALPHA)
                self._original_image.fill((255, 0, 0, 128))
        else:
            self._original_image = path_or_surface.copy()

    def _process_image(self, rotate_angle, scale, width_scale, height_scale):
        self.scale = scale  # 保存缩放参数
        self.width_scale = width_scale
        self.height_scale = height_scale
        self.image = pygame.transform.rotozoom(self._original_image, rotate_angle, scale)
        if width_scale != 1.0 or height_scale != 1.0:
            new_width = int(self.image.get_width() * width_scale)
            new_height = int(self.image.get_height() * height_scale)
            self.image = pygame.transform.scale(self.image, (new_width, new_height))

    def rotate(self, angle):
        """根据给定角度旋转小车"""
        # 基于原始图像旋转并应用缩放
        self.image = pygame.transform.rotozoom(self._original_image, angle, self.scale)
        # 应用额外的宽高缩放
        if self.width_scale != 1.0 or self.height_scale != 1.0:
            new_width = int(self.image.get_width() * self.width_scale)
            new_height = int(self.image.get_height() * self.height_scale)
            self.image = pygame.transform.scale(self.image, (new_width, new_height))
        # 保持中心点不变
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)