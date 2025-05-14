import pygame
import sys
import BackGround
import Component
import Car
import copy
import math
import time
import PathGenerator

pygame.init()
clock = pygame.time.Clock()
pygame.mixer.init()

try:
    click_sound = pygame.mixer.Sound('Source/NXN.mp3')
except FileNotFoundError:
    print("警告：未找到点击音效文件")


class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.action = action
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if hasattr(click_sound, 'play'):
                    click_sound.play()
                if self.action:
                    self.action()


path_points = [

]
station = [(77, 60), (385, 358)]

is_playing = False
game_won = False
path_index = 0.0
coins = 1000
show_no_coins_message = False
no_coins_message_time = 0
start_time = 0
current_time = 0
timer_running = False
operation_history = []


def start_game():
    global is_playing, game_won, path_index, start_time, timer_running, path_points
    # 1. 收集所有用户拖拽摆放的组件
    placed = [cpt for cpt in all_CPT if not getattr(cpt, 'is_original', False)]

    offset_x = 50
    offset_y = 50

    newstation= [(x + offset_x, y + offset_y) for (x, y) in station]

    # 2. 如果一个都没摆，提示后返回
    if not placed:
        print("请先摆放至少一个组件！")
        return

    # 3. 从起点 station[0] 开始，到每个组件的入口→出口，再到终点 station[1]
    # … start_game 里 …
    pts = []
    pts.append(newstation[0])
    for cpt in placed:
        for pt in cpt.get_waypoints():
            pts.append((int(pt.x), int(pt.y)))
    pts.append(newstation[1])
    path_points = pts
  # 赋给全局列表

    # 4. 如果路径足够长，就开始动画
    if len(path_points) >= 2:
        is_playing   = True
        game_won     = False
        path_index   = 0.0
        start_time   = time.time()
        timer_running = True
        print("Generated path:", path_points)  # 调试用：看看坐标对不对
    else:
        print("路径生成失败，请检查组件摆放")



def reset_game():
    global path_index, is_playing, game_won, coins, timer_running, current_time
    path_index = 0.0
    is_playing = False
    game_won = False
    coins = 1000
    timer_running = False
    current_time = 0
    for cpt in all_CPT:
        if not cpt.is_original:
            cpt.kill()
    operation_history.clear()


def rotate_original_components():
    for cpt in original_components[:3]:
        cpt.rotate(45)


def undo_last_operation():
    global coins
    if operation_history:
        last_operation = operation_history.pop()
        if last_operation["type"] == "add":
            component = last_operation.get("component")
            if component is not None:
                if hasattr(component, 'price') and component.price > 0:
                    coins += component.price
                component.kill()
        elif last_operation["type"] == "move":
            component = last_operation.get("component")
            if component is not None and "prev_pos" in last_operation:
                component.rect.topleft = last_operation["prev_pos"]
        elif last_operation["type"] == "rotate":
            component = last_operation.get("component")
            if component is not None and "prev_angle" in last_operation:
                component._rotate_angle = last_operation["prev_angle"]
                component._apply_transform()


BACK = BackGround.BackGround('Source/background.png', 'Source/background2.png')
bg2_width, bg2_height = BACK.image2.get_size()


def load_scaled_component(image_path, target_height_ratio=0.1):
    try:
        image = pygame.image.load(image_path).convert_alpha()
        original_width, original_height = image.get_size()
        aspect_ratio = original_width / original_height
        new_height = int(bg2_height * target_height_ratio)
        new_width = int(new_height * aspect_ratio)
        return pygame.transform.scale(image, (new_width, new_height))
    except pygame.error:
        print(f"无法加载图片: {image_path}")
        return pygame.Surface((50, 50), pygame.SRCALPHA)


car_image = load_scaled_component('Source/Car.jpg', 0.20)
car = Car.Car(car_image, 0, 0.3, 1, 1)

start_button = Button("Start", 580, 200, 70, 50, (0, 255, 0), (0, 200, 0), start_game)
reset_button = Button("Reset", 580, 250, 70, 50, (255, 0, 0), (200, 0, 0), reset_game)
r_button = Button("R", 600, 450, 50, 50, (255, 0, 0), (200, 0, 0), rotate_original_components)
undo_button = Button("Undo", 580, 300, 70, 50, (100, 100, 100), (70, 70, 70), undo_last_operation)

original_components = [
    Component.Component(load_scaled_component('Source/CPT1.png', 0.15), 1,0, 0.7, price=100),
    Component.Component(load_scaled_component('Source/CPT2.jpg', 0.15), 2,0, 0.7, price=100),
    Component.Component(load_scaled_component('Source/CPT3.png', 0.15), 3,0, 0.8, price=100),
    Component.Component(load_scaled_component('Source/startp.png', 0.15), 0, 1, price=0),
    Component.Component(load_scaled_component('Source/endp.png', 0.15), 0, 1, price=0)
]

for cpt in original_components:
    cpt.is_original = True

initial_positions = [(679, 50), (679, 200), (699, 330), station[0], station[1]]
for cpt, pos in zip(original_components, initial_positions):
    cpt.rect.topleft = pos

all_CPT = pygame.sprite.Group()
all_CPT.add(original_components)

try:
    coin_image = load_scaled_component('Source/coin.png', 0.05)
    small_coin_image = pygame.transform.scale(coin_image, (20, 20))
except:
    coin_image = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(coin_image, (255, 215, 0), (15, 15), 15)
    small_coin_image = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(small_coin_image, (255, 215, 0), (10, 10), 10)

try:
    clock_image = load_scaled_component('Source/clock.png', 0.05)
except:
    clock_image = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(clock_image, (200, 200, 200), (15, 15), 15)
    pygame.draw.line(clock_image, (0, 0, 0), (15, 15), (15, 10), 2)
    pygame.draw.line(clock_image, (0, 0, 0), (15, 15), (20, 15), 2)

dragging = False
selected_component = None
offset = (0, 0)

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
price_font = pygame.font.Font(None, 20)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        start_button.handle_event(event)
        reset_button.handle_event(event)
        r_button.handle_event(event)
        undo_button.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for cpt in original_components:
                if cpt.rect.collidepoint(mouse_pos):
                    if coins >= cpt.price:
                        new_component = copy.deepcopy(cpt)
                        new_component.is_original = False
                        new_component.rect.center = mouse_pos
                        all_CPT.add(new_component)
                        selected_component = new_component
                        offset = (mouse_pos[0] - new_component.rect.centerx, mouse_pos[1] - new_component.rect.centery)
                        dragging = True
                        new_component.image.set_alpha(128)
                        coins -= cpt.price
                        operation_history.append({"type": "add", "component": new_component, "price": cpt.price})
                    else:
                        show_no_coins_message = True
                        no_coins_message_time = pygame.time.get_ticks()
                    break
        elif event.type == pygame.MOUSEBUTTONUP:
            if selected_component:
                selected_component.image.set_alpha(255)
                operation_history.append({
                    "type": "move",
                    "component": selected_component,
                    "prev_pos": (selected_component.rect.x - offset[0], selected_component.rect.y - offset[1])
                })
            dragging = False
            selected_component = None
        elif event.type == pygame.MOUSEMOTION and dragging:
            if selected_component:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                new_x = mouse_x - offset[0]
                new_y = mouse_y - offset[1]
                selected_component.rect.center = (new_x, new_y)
        elif event.type == pygame.KEYDOWN:
            if selected_component:
                prev_angle = selected_component.get_angle()
                if event.key == pygame.K_a:
                    selected_component.rotate(5)
                elif event.key == pygame.K_d:
                    selected_component.rotate(-5)
                elif event.key == pygame.K_q:
                    selected_component.rotate(90)
                elif event.key == pygame.K_e:
                    selected_component.rotate(-90)
                operation_history.append({"type": "rotate", "component": selected_component, "prev_angle": prev_angle})

    if show_no_coins_message and pygame.time.get_ticks() - no_coins_message_time > 2000:
        show_no_coins_message = False

    if is_playing and not game_won:
        path_index += 0.2
        idx = int(path_index)
        if idx < len(path_points) - 1:
            start_p = path_points[idx]
            end_p = path_points[idx + 1]
            dx = end_p[0] - start_p[0]
            dy = end_p[1] - start_p[1]
            if dx != 0 or dy != 0:
                angle = math.degrees(math.atan2(-dy, dx))
                car.rotate(angle - 90)
        else:
            game_won = True
            is_playing = False
            timer_running = False

    if timer_running:
        current_time = time.time() - start_time

    BACK.window.fill((0, 0, 0))
    BACK.window.blit(BACK.image1, (0, 0))
    BACK.window.blit(BACK.image2, (BACK.image1.get_width(), 0))
    BACK.window.blit(coin_image, (10, 10))
    coin_text = font.render(f": {coins}", True, (0, 0, 0))
    BACK.window.blit(coin_text, (50, 15))
    BACK.window.blit(clock_image, (BACK.image1.get_width() - 100, 10))
    minutes = int(current_time // 60)
    seconds = current_time % 60
    time_text = font.render(f": {minutes:02d}:{seconds:05.2f}", True, (255, 255, 255))
    BACK.window.blit(time_text, (BACK.image1.get_width() - 70, 15))
    all_CPT.draw(BACK.window)

    for i, cpt in enumerate(original_components[:3]):
        price_x = initial_positions[i][0] + 20
        price_y = initial_positions[i][1] + cpt.rect.height + 5
        BACK.window.blit(small_coin_image, (price_x, price_y))
        price_text = price_font.render(f"{cpt.price}", True, (0, 0, 0))
        BACK.window.blit(price_text, (price_x + small_coin_image.get_width() + 5, price_y))

    if path_index < len(path_points):
        idx = int(path_index)
        if idx < len(path_points) - 1:
            factor = path_index - idx
            x = path_points[idx][0] + (path_points[idx + 1][0] - path_points[idx][0]) * factor
            y = path_points[idx][1] + (path_points[idx + 1][1] - path_points[idx][1]) * factor
        else:
            x, y = path_points[idx]
            # 在游戏主循环的绘制部分添加路径绘制代码（大约在while循环的末尾，绘制小车之前）
            # 在以下位置添加代码：

            BACK.window.blit(time_text, (BACK.image1.get_width() - 70, 15))
            all_CPT.draw(BACK.window)

            for i, cpt in enumerate(original_components[:3]):
                price_x = initial_positions[i][0] + 20
        BACK.window.blit(car.image, (x, y))

    start_button.draw(BACK.window)
    reset_button.draw(BACK.window)
    r_button.draw(BACK.window)
    undo_button.draw(BACK.window)
    if game_won:
        victory_font = pygame.font.Font(None, 74)
        victory_text = victory_font.render("VICTORY!", True, (255, 215, 0))
        text_rect = victory_text.get_rect(center=(BACK.window.get_width() // 2, BACK.window.get_height() // 2))
        BACK.window.blit(victory_text, text_rect)
        final_time_font = pygame.font.Font(None, 48)
        final_time_text = final_time_font.render(f"Time: {minutes:02d}:{seconds:05.2f}", True, (255, 255, 255))
        final_time_rect = final_time_text.get_rect(
            center=(BACK.window.get_width() // 2, BACK.window.get_height() // 2 + 50))
        BACK.window.blit(final_time_text, final_time_rect)
    if show_no_coins_message:
        warning_font = pygame.font.Font(None, 32)
        warning_text = warning_font.render("Not enough coins!", True, (255, 0, 0))
        warning_rect = warning_text.get_rect(center=(BACK.window.get_width() // 2, 50))
        BACK.window.blit(warning_text, warning_rect)
    pygame.display.flip()
    clock.tick(60)