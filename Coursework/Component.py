import pygame

import pygame

class Component(pygame.sprite.Sprite):
    def __init__(self, surface, type, rotate_angle=0, scale=1.0, price=100):
        super().__init__()
        self.type = type
        self._rotate_angle = rotate_angle
        self.scale = scale
        self.price = price
        self.is_original = False

        self.original_image = surface.convert_alpha()
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self._apply_transform()

    def _apply_transform(self):
        old_center = self.rect.center
        self.image = pygame.transform.rotozoom(
            self.original_image, self._rotate_angle, self.scale
        )
        self.rect = self.image.get_rect(center=old_center)

    def rotate(self, delta_angle):
        self._rotate_angle = (self._rotate_angle + delta_angle) % 360
        self._apply_transform()

    def get_angle(self):
        return self._rotate_angle

    def __deepcopy__(self, memo):
        # 完整传参：surface, type, rotate_angle, scale, price
        new_obj = Component(
            self.original_image,
            self.type,
            rotate_angle=self._rotate_angle,
            scale=self.scale,
            price=self.price
        )
        new_obj.rect = self.rect.copy()
        new_obj.is_original = self.is_original
        return new_obj

    def get_connection_points(self):
        center = pygame.math.Vector2(self.rect.center)
        return center, center

    def get_waypoints(self):
        center = pygame.math.Vector2(self.rect.center)
        return [center]
