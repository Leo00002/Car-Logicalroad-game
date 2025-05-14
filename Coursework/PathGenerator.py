import pygame, math

class PathGenerator:
    @staticmethod
    def line(start: pygame.math.Vector2,
             end:   pygame.math.Vector2,
             steps: int = 50):
        """直线路径：线性插值"""
        return [start.lerp(end, t/(steps-1)) for t in range(steps)]

    @staticmethod
    def arc(start: pygame.math.Vector2,
            end:   pygame.math.Vector2,
            height: float = 100,
            steps:  int   = 50):
        """
        弧形路径：通过抛物线形式提升高度 height，再回到 end 点。
        param height: 弧线中点向上的最大偏移量。
        """
        path = []
        for i in range(steps):
            t = i/(steps-1)
            # 基本线性点
            p = start.lerp(end, t)
            # 抛物线偏移：4h * t*(1-t)
            offset = height * 4 * t * (1 - t)
            # 垂直于 start->end 的单位法向量
            dir_vec = (end - start).normalize()
            normal = pygame.math.Vector2(-dir_vec.y, dir_vec.x)
            p += normal * offset
            path.append(p)
        return path

    @staticmethod
    def hyperbola(start: pygame.math.Vector2,
                  end:   pygame.math.Vector2,
                  a:     float = 1.0,
                  b:     float = 1.0,
                  steps: int   = 50):
        """
        双曲线路径：先将双曲线 y = b/x 片段映射到 0<=t<=1，再旋转平移到 start->end。
        a, b 控制曲线形状。这里 x 从 a 到 end_dist-a。
        """
        # 建立坐标系
        delta = end - start
        length = delta.length()
        ux    = delta.normalize()        # x 轴方向
        uy    = pygame.math.Vector2(-ux.y, ux.x)  # y 轴（法向量）
        # x 在 [a, length−a]
        xs = [a + (length - 2*a) * i/(steps-1) for i in range(steps)]
        path = []
        for x in xs:
            y = b / (x - a + 1e-5)  # 避免除零
            # 将 (x, y) 坐标映射回世界坐标
            p = start + ux * x + uy * y
            path.append(p)
        return path
