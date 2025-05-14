import pygame
import sys
from PIL import Image
import time
import math

pygame.init()

# Removed the global variable _target_state_after_loading

screen = pygame.display.set_mode((804, 512), pygame.RESIZABLE)
pygame.display.set_caption("GAME")

font = pygame.font.SysFont(None, 48)

# --- Game State Constants ---
LOGIN = "login"
MAIN_GAME = "main_game"
LOADING1 = "loading1"
LOADING2 = "loading2"
SCREEN_1 = "screen_1"
SCREEN_2 = "screen_2"
SCREEN_3 = "screen_3"
SCREEN_4 = "screen_4"

# --- Constants for UI Elements ---
BACK_ICON_SIZE_RATIO = 0.05 # Back icon height relative to screen height
BACK_ICON_MARGIN = 15 # Margin from top and left edges in pixels


# --- Load Background Images and GIFs ---
login_background_img_static = None
try:
    login_background_img_static = pygame.image.load("static/images/login_background.png").convert_alpha()
except pygame.error:
    login_background_img_static = None
    print("Warning: static/images/login_background.png not found or could not be loaded.")


# --- Load Main Game Chapter Images (map1 and map4 use .png, map2 and map3 use .jpg) ---
img_originals_main_game = {}
try:
    # map1 uses .png extension
    img_originals_main_game[1] = pygame.image.load("static/images/map1.png").convert_alpha()
except pygame.error:
    img_originals_main_game[1] = None
    print("Warning: static/images/map1.png not found or could not be loaded.")

try:
    # map2 uses .jpg extension
    img_originals_main_game[2] = pygame.image.load("static/images/map2.jpg").convert_alpha()
except pygame.error:
    img_originals_main_game[2] = None
    print("Warning: static/images/map2.jpg not found or could not be loaded.")

try:
    # map3 uses .jpg extension
    img_originals_main_game[3] = pygame.image.load("static/images/map3.jpg").convert_alpha()
except pygame.error:
    img_originals_main_game[3] = None
    print("Warning: static/images/map3.jpg not found or could not be loaded.")

try:
    # map4 uses .png extension
    img_originals_main_game[4] = pygame.image.load("static/images/map4.png").convert_alpha()
except pygame.error:
    img_originals_main_game[4] = None
    print("Warning: static/images/map4.png not found or could not be loaded.")


# --- Load Title Image ---
title_img_original = None
try:
    title_img_original = pygame.image.load("static/images/title.png").convert_alpha()
except pygame.error:
    title_img_original = None
    print("Warning: static/images/title.png not found or could not be loaded.")


def load_gif_frames(gif_path):
    frames = []
    try:
        img = Image.open(gif_path)
        if hasattr(img, 'seek'):
            try:
                i = 0
                while True:
                    img.seek(i)
                    # Ensure we copy the frame to avoid issues with PIL's lazy loading
                    frame_rgba = img.copy().convert("RGBA")
                    pygame_frame = pygame.image.frombuffer(frame_rgba.tobytes(), frame_rgba.size, "RGBA")
                    frames.append(pygame_frame)
                    i += 1
            except EOFError:
                pass
        else:
             # Handle non-animated images passed to this function (unlikely for GIFs)
             frame_rgba = img.convert("RGBA")
             pygame_frame = pygame.image.frombuffer(frame_rgba.tobytes(), frame_rgba.size, "RGBA")
             frames.append(pygame_frame)

    except FileNotFoundError:
        # print(f"Warning: GIF file not found at {gif_path}") # Printed in calling code
        return None
    except Exception as e:
        # print(f"Warning: Could not load or process GIF file {gif_path}: {e}") # Printed in calling code
        return None

    if not frames:
         # print(f"Warning: No frames loaded from {gif_path}") # Printed in calling code
         return None

    return frames

# --- Load GIF Animation Frames ---
login_background_gif_frames_original = load_gif_frames("static/images/login_background.gif")
# Fallback for login background
if login_background_gif_frames_original is None or not login_background_gif_frames_original:
    print("Warning: static/images/login_background.gif not loaded.")
    if login_background_img_static:
         login_background_fallback = login_background_img_static
    else:
         login_background_fallback = (0, 0, 0) # Default to black if neither static image nor GIF loaded
else:
    login_background_fallback = None # No fallback needed if GIF loaded

loading1_gif_frames_original = load_gif_frames("static/images/loading.gif")
# Fallback for loading1 text
if loading1_gif_frames_original is None or not loading1_gif_frames_original:
    print("Warning: static/images/loading.gif not loaded. Using fallback text.")
    loading1_text_surface = font.render("Loading...", True, (255, 255, 255))
else:
    loading1_text_surface = None

loading2_gif_frames_original = load_gif_frames("static/images/loading2.gif")
# Fallback for loading2 text
if loading2_gif_frames_original is None or not loading2_gif_frames_original:
    print("Warning: static/images/loading2.gif not loaded. Using fallback text.")
    loading2_text_surface = font.render("Loading Level...", True, (255, 255, 255))
else:
    loading2_text_surface = None

# --- Load Main Game Screen Background GIF ---
choose_background_gif_frames_original = load_gif_frames("static/images/choose.gif")
# --- Add print info ---
if choose_background_gif_frames_original:
    print(f"Successfully loaded {len(choose_background_gif_frames_original)} frames from static/images/choose.gif")
else:
    print("Failed to load static/images/choose.gif. MainGameScreen background will be solid color.")

# --- Load Left and Right Arrow Navigation Images (larr and rarr, set colorkey) ---
arrow_left_img_original = None
try:
    # Load larr.png and convert_alpha()
    arrow_left_img_original = pygame.image.load("static/images/larr.png").convert_alpha()
    # --- Set white as transparent color ---
    if arrow_left_img_original:
        # Set colorkey, (255, 255, 255) pure white will be considered transparent
        # Use RLEACCEL to improve drawing speed for transparent images
        arrow_left_img_original.set_colorkey((255, 255, 255), pygame.RLEACCEL)
except pygame.error:
    arrow_left_img_original = None
    print("Warning: static/images/larr.png not found or could not be loaded.")


arrow_right_img_original = None
try:
    # Load rarr.png and convert_alpha()
    arrow_right_img_original = pygame.image.load("static/images/rarr.png").convert_alpha()
    # --- Set white as transparent color ---
    if arrow_right_img_original:
        # Set colorkey, (255, 255, 255) pure white will be considered transparent
        # Use RLEACCEL to improve drawing speed for transparent images
        arrow_right_img_original.set_colorkey((255, 255, 255), pygame.RLEACCEL)
except pygame.error:
    arrow_right_img_original = None
    print("Warning: static/images/rarr.png not found or could not be loaded.")


class LoginScreen:
    # Add title_img_original to the constructor
    def __init__(self, screen, font, background_gif_frames, fallback_background, title_img_original):
        self.screen = screen
        self.font = font
        self.background_gif_frames = background_gif_frames
        self.is_background_gif_loaded = self.background_gif_frames is not None and len(self.background_gif_frames) > 0
        self.fallback_background = fallback_background

        self.background_frame_index = 0
        self.last_background_frame_time = time.time()
        self.background_frame_duration = 0.08

        self.prompt_text_surface = font.render("Press any key to continue", True, (255, 255, 255))
        self.text_visible = True
        self.last_text_toggle_time = time.time()
        self.text_blink_rate = 0.5

        # --- Title Image Properties ---
        self.title_img_original = title_img_original
        self.title_img_scaled = None # Current title image for drawing
        self.title_target_size_ratio = 0.7 # Target width as a ratio of screen width
        self.title_target_y_ratio = 0.25 # Target center Y coordinate as a ratio of screen height

        # Target size and position (calculated in _scale_assets)
        self.title_target_width = 0
        self.title_target_height = 0
        self.title_target_center_x = 0
        self.title_target_center_y = 0

        # Title animation properties
        self.title_current_scale = 0.01 # Current scale (from small to large, starts near 0)
        self.title_animation_duration = 1.5 # Animation duration (秒)
        self.title_animation_start_time = time.time() # Animation start time
        self.title_animation_finished = False # Is animation finished

        self._scale_assets() # Scale assets on initialization

    def _scale_assets(self):
        screen_width, screen_height = self.screen.get_size()

        # 缩放背景图
        if not self.is_background_gif_loaded and isinstance(self.fallback_background, pygame.Surface):
             try:
                  self.scaled_fallback_background = pygame.transform.scale(self.fallback_background, (screen_width, screen_height))
             except (ValueError, Exception):
                  self.scaled_fallback_background = None

        # --- Calculate Target Size and Position for Title Image, and reset animation ---
        if self.title_img_original:
            # Calculate target size
            aspect_ratio = self.title_img_original.get_width() / max(1, self.title_img_original.get_height())
            self.title_target_width = int(screen_width * self.title_target_size_ratio)
            self.title_target_height = int(self.title_target_width / aspect_ratio)

            # Ensure a minimum size, avoid scaling to 0 or negative
            min_title_size = 50
            if self.title_target_width < min_title_size or self.title_target_height < min_title_size:
                self.title_target_width = min_title_size
                if aspect_ratio > 0: # Ensure aspect_ratio is valid, avoid division by zero
                    self.title_target_height = max(min_title_size, int(min_title_size / aspect_ratio))
                else:
                    self.title_target_height = min_title_size


            # Calculate target center position
            self.title_target_center_x = screen_width // 2
            self.title_target_center_y = int(screen_height * self.title_target_y_ratio)

            # Reset animation state, make title reappear on window size change
            self.title_current_scale = 0.01 # Start from small
            self.title_animation_start_time = time.time() # Update animation start time
            self.title_animation_finished = False # Animation is not finished

            # Initial scale title image to the starting size of the animation
            current_width = int(self.title_target_width * self.title_current_scale)
            current_height = int(self.title_target_height * self.title_current_scale)
            if current_width > 0 and current_height > 0:
                 try:
                      # Use smoothscale for smoother animation scaling
                      self.title_img_scaled = pygame.transform.smoothscale(self.title_img_original, (current_width, current_height))
                 except (ValueError, Exception):
                      # Set to None if scaling fails
                      self.title_img_scaled = None
            else:
                 self.title_img_scaled = None # If calculated size <= 0, set to None
        else:
             self.title_img_scaled = None # Set to None if original title image didn't load


    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
             self._scale_assets() # Rescale resources when window size changes
             # If animating, window change might cause inaccurate animation position, consider forcing animation to finish or resetting.
             # self.is_animating = False # Simple handling: stop animation on window change
             # For title animation, we just reset it
             self.title_current_scale = 0.01
             self.title_animation_start_time = time.time()
             self.title_animation_finished = False


        if event.type == pygame.KEYDOWN:
            if event.key != pygame.K_ESCAPE:
                # Press any non-ESC key to switch to LOADING1
                return LOADING1
            else:
                 # Press ESC key to minimize window
                 pygame.display.iconify()
                 return None # Don't switch state

        return None # No state transition

    def update(self):
        current_time = time.time()

        # Update Background GIF Animation Frame (LoginScreen's own background animation)
        if self.is_background_gif_loaded:
            if current_time - self.last_background_frame_time > self.background_frame_duration:
                self.background_frame_index = (self.background_frame_index + 1) % len(self.background_gif_frames)
                self.last_background_frame_time = current_time

        # Update blink state of "Press any key" text
        if current_time - self.last_text_toggle_time > self.text_blink_rate:
            self.text_visible = not self.text_visible
            self.last_text_toggle_time = current_time

        # --- Update Title Image Pop-up Animation (LoginScreen's own title animation) ---
        # Note here we use self.title_animation_start_time, self.title_animation_duration, self.title_animation_finished
        if self.title_img_original and not self.title_animation_finished:
            elapsed_time = current_time - self.title_animation_start_time
            # Calculate animation progress (0.0 to 1.0)
            progress = min(elapsed_time / self.title_animation_duration, 1.0)

            # Calculate the current scale (linear interpolation from near 0 to 1.0)
            # Use 0.01 as a starting point to avoid scaling to size 0
            self.title_current_scale = 0.01 + progress * (1.0 - 0.01)

            # Calculate the current size for this animation frame
            current_width = int(self.title_target_width * self.title_current_scale)
            current_height = int(self.title_target_height * self.title_current_scale)
            if current_width > 0 and current_height > 0:
                 try:
                      # Use smoothscale for smoother animation scaling
                      self.title_img_scaled = pygame.transform.smoothscale(self.title_img_original, (current_width, current_height))
                 except (ValueError, Exception):
                      # Set to None if scaling fails
                      self.title_img_scaled = None
            else:
                 self.title_img_scaled = None # If calculated size <= 0, set to None


            if progress >= 1.0:
                self.title_animation_finished = True
                # Ensure at the end of animation, the image is scaled precisely to target size
                if self.title_img_original:
                     if self.title_target_width > 0 and self.title_target_height > 0:
                          try:
                               self.title_img_scaled = pygame.transform.smoothscale(self.title_img_original, (self.title_target_width, self.title_target_height))
                          except (ValueError, Exception):
                               self.title_img_scaled = None
                     else:
                          self.title_img_scaled = None
                else:
                     self.title_img_scaled = None


        return None # LoginScreen's update method does not return a new state unless specific logic requires switching


    def draw(self):
        screen_width, screen_height = self.screen.get_size()

        # 绘制背景
        if self.is_background_gif_loaded:
            current_frame = self.background_gif_frames[self.background_frame_index]
            try:
                # Scale GIF frame and draw to full screen
                scaled_frame = pygame.transform.smoothscale(current_frame, (screen_width, screen_height))
                self.screen.blit(scaled_frame, (0, 0))
            except (ValueError, Exception):
                 # Fill with black if scaling fails
                 self.screen.fill((0, 0, 0))
        else:
             # Draw fallback background (static image or solid color)
             if isinstance(self.fallback_background, tuple):
                  self.screen.fill(self.fallback_background)
             elif self.fallback_background and self.scaled_fallback_background:
                  self.screen.blit(self.scaled_fallback_background, (0, 0))
             else:
                  self.screen.fill((0, 0, 0)) # Fill with black if no background loaded

        # --- Draw Title Image ---
        if self.title_img_scaled:
            title_w, title_h = self.title_img_scaled.get_size()
            # Calculate drawing position to center it on the target center
            draw_x = self.title_target_center_x - title_w // 2
            draw_y = self.title_target_center_y - title_h // 2
            # Draw the scaled title image
            self.screen.blit(self.title_img_scaled, (draw_x, draw_y))

        # Draw "Press any key" text (if visible)
        if self.text_visible:
             # Position text near the bottom center of the screen
             text_rect = self.prompt_text_surface.get_rect(center=(screen_width // 2, screen_height * 0.9))
             self.screen.blit(self.prompt_text_surface, text_rect)


class LoadingScreen:
    # Added frame_duration_override
    # Removed target_size_ratio as GIF will fill screen
    def __init__(self, screen, font, gif_frames, fallback_text_surface, next_state, frame_duration_override=None, loop_count=1, fallback_duration=None): # Default fallback_duration to None
        self.screen = screen
        self.font = font
        self.gif_frames = gif_frames
        self.is_gif_loaded = self.gif_frames is not None and len(self.gif_frames) > 0
        self.fallback_text_surface = fallback_text_surface
        self.next_state = next_state # This is now set by Game.change_state or remains the one set in Game.__init__

        self.background_color = (0, 0, 0) # Loading screen background color

        self.frame_index = 0
        self.last_frame_time = time.time()
        # Use override frame duration if provided, otherwise use a default faster duration
        self.frame_duration = frame_duration_override if frame_duration_override is not None else 0.03 # Default faster speed

        # GIF loop control (if GIF is loaded)
        self.loop_count = 0
        # target_loops is None if we only use fallback_duration for transition
        self.target_loops = loop_count

        # Fallback text display duration control (if GIF fails to load or fixed duration is set)
        self.fallback_start_time = time.time()
        # fallback_duration is None if we only use GIF loop_count for transition
        self.fallback_duration = fallback_duration

        # No specific GIF position/size needed as it fills the screen

        # Initial Rect for centered fallback text (only needed if GIF fails to load)
        if self.fallback_text_surface:
             screen_width, screen_height = self.screen.get_size()
             self.fallback_text_rect = self.fallback_text_surface.get_rect(center=(screen_width // 2, screen_height // 2))


    def _scale_assets(self):
        # Only need to re-center fallback text if screen resizes and GIF isn't loaded
        if not self.is_gif_loaded and self.fallback_text_surface:
             screen_width, screen_height = self.screen.get_size()
             self.fallback_text_rect = self.fallback_text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
        # No scaling/positioning needed for GIF as it fills the screen


    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
             self._scale_assets() # Re-calculate positions and sizes on screen resize

        # Allow skipping loading screens by pressing ESC
        if event.type == pygame.KEYDOWN:
             if event.key == pygame.K_ESCAPE:
                  # If ESC is pressed, transition to the screen defined by next_state
                  # If next_state is None, it will effectively do nothing here unless state is set elsewhere
                  # We return the next_state property directly
                  return self.next_state

        return None

    def update(self):
        current_time = time.time()

        # Priority to fixed duration if set
        if self.fallback_duration is not None:
             if current_time - self.fallback_start_time >= self.fallback_duration:
                  return self.next_state # Transition to the next state

        # If no fixed duration, check GIF loop count if GIF is loaded and target_loops is set
        if self.is_gif_loaded:
            # Update GIF frame based on its frame duration
            if current_time - self.last_frame_time > self.frame_duration:
                self.frame_index += 1
                self.last_frame_time = current_time

                # GIF loop handling
                if self.frame_index >= len(self.gif_frames):
                    self.frame_index = 0 # Back to the first frame
                    self.loop_count += 1 # Increment loop count

            # Check if target loop count is reached (only if fixed duration was not set and target_loops is not None)
            if self.fallback_duration is None and self.target_loops is not None and self.loop_count >= self.target_loops:
                return self.next_state # Transition to the next state


        # If neither fixed duration nor GIF loops trigger transition, stay in this state
        return None

    def draw(self):
        screen_width, screen_height = self.screen.get_size()

        self.screen.fill(self.background_color) # Fill background

        if self.is_gif_loaded:
            # Draw current GIF frame, scaled to fill the entire screen
            current_frame = self.gif_frames[self.frame_index]
            try:
                scaled_frame = pygame.transform.smoothscale(current_frame, (screen_width, screen_height))
                self.screen.blit(scaled_frame, (0, 0))
            except (ValueError, Exception):
                 pass # Ignore drawing if scaling fails


        elif self.fallback_text_surface:
            # Draw fallback text (centered)
            if self.fallback_text_rect: # Check if rect was successfully calculated
                 self.screen.blit(self.fallback_text_surface, self.fallback_text_rect)


class MainGameScreen:
    # Added background_gif_frames, arrow_left_img_original, arrow_right_img_original, back_icon_original parameters
    def __init__(self, screen, font, img_originals, background_gif_frames, arrow_left_img_original, arrow_right_img_original, back_icon_original):
        self.screen = screen
        self.font = font

        # --- Background GIF properties ---
        self.background_gif_frames = background_gif_frames
        self.is_background_gif_loaded = self.background_gif_frames is not None and len(self.background_gif_frames) > 0
        self.background_frame_index = 0
        self.last_background_frame_time = time.time()
        self.background_frame_duration = 0.05 # GIF frame switching speed (seconds)
        self.fallback_background_color = (100, 200, 100) # Fallback background color if GIF is not loaded


        self.img_originals = img_originals # Original chapter images
        # img_scaled will store the *single* target size (width, height) for all maps
        # Ensure that even if some images fail to load, the corresponding keys exist in the dictionary with None values
        self.img_scaled = {key: None for key in range(1, 5)} # Initialize all possible chapter keys
        # The actual target size (tuple) will be calculated in _scale_assets and stored here for all valid maps


        # --- Chapter Switching Animation Properties ---
        self.current_chapter_index = 1 # Current chapter index being displayed (starts from 1)
        self.is_animating = False # Flag indicating if animation is in progress
        self.animation_start_time = 0 # Animation start time
        self.animation_duration = 0.5 # Animation duration (seconds)
        self.animation_direction = 0 # Animation direction: -1 (slide left to show next), 1 (slide right to show previous)

        self.outgoing_chapter_index = None # Index of the chapter sliding out
        self.incoming_chapter_index = None # Index of the chapter sliding in

        self.chapter_image_rect = None # Rect for the currently displayed chapter image (for click detection)
                                      # This Rect is updated during animation and when not animating
        # Target vertical position (center Y coordinate) for the chapter image (middle-upper)
        self.chapter_image_target_y = 0

        # Variables to hold current animated positions during slide (Left-top corner coordinates)
        self.current_x_out = None
        self.current_x_in = None


        # --- Left/Right Arrow Navigation Button Properties ---
        self.arrow_left_img_original = arrow_left_img_original
        self.arrow_right_img_original = arrow_right_img_original
        self.arrow_left_img_scaled = None
        self.arrow_right_img_scaled = None
        self.arrow_left_rect = None # Left arrow click area
        self.arrow_right_rect = None # Right arrow click area
        self.arrow_size_ratio = 0.08 # Arrow image size as a ratio of screen height
        self.arrow_margin_ratio = 0.02 # Arrow image distance from screen edge

        # --- Back Icon Properties ---
        self.back_icon_original = back_icon_original
        self.back_icon_scaled = None
        self.back_rect = None # Rect for the back icon click area


        self._scale_assets() # Scale assets on initialization

    def _scale_assets(self):
         screen_width, screen_height = self.screen.get_size()

         # --- Calculate Single Target Size for All Chapter Images ---
         # Target size as a ratio of screen dimensions (e.g., 50% width, 40% height)
         target_map_display_width_ratio = 0.5
         target_map_display_height_ratio = 0.4
         min_img_size = 100 # Minimum size

         target_width = int(screen_width * target_map_display_width_ratio)
         target_height = int(screen_height * target_map_display_height_ratio)

         # Ensure minimum size
         if target_width < min_img_size:
             target_width = min_img_size
         if target_height < min_img_size:
             target_height = min_img_size

         # Store this SAME target size for all existing map images
         single_target_size = (target_width, target_height)
         for key in range(1, 5):
              if self.img_originals.get(key) is not None: # Only store if the original image is loaded
                   self.img_scaled[key] = single_target_size
              else:
                   self.img_scaled[key] = None # Ensure it's None if original wasn't loaded

         # Calculate the vertical position (center Y coordinate) for the chapter image (middle-upper)
         # Position it at, say, 35% of the screen height
         self.chapter_image_target_y = int(screen_height * 0.35)

         # --- Scale and Position Left/Right Arrow Images ---
         arrow_target_height = int(screen_height * self.arrow_size_ratio)
         arrow_margin = int(screen_width * self.arrow_margin_ratio)

         if self.arrow_left_img_original:
              try:
                   arrow_aspect = self.arrow_left_img_original.get_width() / max(1, self.arrow_left_img_original.get_height())
                   arrow_target_width = int(arrow_target_height * arrow_aspect)
                   if arrow_target_width > 0 and arrow_target_height > 0:
                         # Scale arrow image
                         self.arrow_left_img_scaled = pygame.transform.scale(self.arrow_left_img_original, (arrow_target_width, arrow_target_height))
                         # Calculate left arrow position
                         arrow_left_x = arrow_margin
                         arrow_left_y = screen_height // 2 - arrow_target_height // 2
                         self.arrow_left_rect = self.arrow_left_img_scaled.get_rect(topleft=(arrow_left_x, arrow_left_y))
                   else:
                         self.arrow_left_img_scaled = None
                         self.arrow_left_rect = None
              except (ValueError, Exception):
                   self.arrow_left_img_scaled = None
                   self.arrow_left_rect = None
         else:
              self.arrow_left_img_scaled = None
              self.arrow_left_rect = None


         if self.arrow_right_img_original:
              try:
                   arrow_aspect = self.arrow_right_img_original.get_width() / max(1, self.arrow_right_img_original.get_height())
                   arrow_target_width = int(arrow_target_height * arrow_aspect)
                   if arrow_target_width > 0 and arrow_target_height > 0:
                         # Scale arrow image
                         self.arrow_right_img_scaled = pygame.transform.scale(self.arrow_right_img_original, (arrow_target_width, arrow_target_height))
                         # Calculate right arrow position (aligned to the right edge)
                         arrow_right_x = screen_width - arrow_target_width - arrow_margin
                         arrow_right_y = screen_height // 2 - arrow_target_height // 2
                         self.arrow_right_rect = self.arrow_right_img_scaled.get_rect(topleft=(arrow_right_x, arrow_right_y))
                   else:
                         self.arrow_right_img_scaled = None
                         self.arrow_right_rect = None
              except (ValueError, Exception):
                   self.arrow_right_img_scaled = None
                   self.arrow_right_rect = None
         else:
              self.arrow_right_img_scaled = None
              self.arrow_right_rect = None

         # --- Scale and Position Back Icon ---
         if self.back_icon_original:
              try:
                   icon_target_height = int(screen_height * BACK_ICON_SIZE_RATIO)
                   icon_aspect = self.back_icon_original.get_width() / max(1, self.back_icon_original.get_height())
                   icon_target_width = int(icon_target_height * icon_aspect)

                   if icon_target_width > 0 and icon_target_height > 0:
                        # Use scale as it's a small icon and quality difference is minimal, but scale is faster
                        self.back_icon_scaled = pygame.transform.scale(self.back_icon_original, (icon_target_width, icon_target_height))
                        # Position in top-left corner with margin
                        back_icon_x = BACK_ICON_MARGIN
                        back_icon_y = BACK_ICON_MARGIN
                        self.back_rect = self.back_icon_scaled.get_rect(topleft=(back_icon_x, back_icon_y))
                   else:
                       self.back_icon_scaled = None
                       self.back_rect = None
              except (ValueError, Exception):
                   self.back_icon_scaled = None
                   self.back_rect = None
         else:
              self.back_icon_scaled = None
              self.back_rect = None

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self._scale_assets()
            self.is_animating = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            # --- 检测左右箭头点击 ---
            if not self.is_animating:
                # 左箭头点击逻辑保持不变
                if self.current_chapter_index > 1 and self.arrow_left_rect and self.arrow_left_rect.collidepoint(
                        mouse_pos):
                    if self.img_originals.get(self.current_chapter_index - 1) is not None:
                        self.is_animating = True
                        self.animation_direction = 1
                        self.animation_start_time = time.time()
                        self.outgoing_chapter_index = self.current_chapter_index
                        self.incoming_chapter_index = self.current_chapter_index - 1
                    return None

                # 右箭头点击逻辑保持不变
                if self.current_chapter_index < 4 and self.arrow_right_rect and self.arrow_right_rect.collidepoint(
                        mouse_pos):
                    if self.img_originals.get(self.current_chapter_index + 1) is not None:
                        self.is_animating = True
                        self.animation_direction = -1
                        self.animation_start_time = time.time()
                        self.outgoing_chapter_index = self.current_chapter_index
                        self.incoming_chapter_index = self.current_chapter_index + 1
                    return None

            # --- 检测章节图片点击 ---
            if not self.is_animating and self.chapter_image_rect and self.chapter_image_rect.collidepoint(mouse_pos):
                # 确定目标状态
                target_state = None
                if self.current_chapter_index == 1:
                    target_state = SCREEN_1  # 第1章跳转到gameLevel1
                elif self.current_chapter_index == 2:
                    target_state = SCREEN_2
                elif self.current_chapter_index == 3:
                    target_state = SCREEN_3
                elif self.current_chapter_index == 4:
                    target_state = SCREEN_4

                if target_state is not None and self.img_originals.get(self.current_chapter_index):
                    # 返回元组，先进入LOADING2状态，再跳转到目标状态
                    return (LOADING2, target_state)
                else:
                    print(f"Warning: Cannot start Chapter {self.current_chapter_index}. Image not loaded.")
                    return None

            # --- 检测返回按钮点击 ---
            if self.back_rect and self.back_rect.collidepoint(mouse_pos):
                return LOGIN

        return None

    def update(self):
        current_time = time.time()

        # --- Update Background GIF Animation Frame ---
        if self.is_background_gif_loaded:
            if current_time - self.last_background_frame_time > self.background_frame_duration:
                # Switch to the next frame, loop back to the first frame if at the end (實現循環)
                self.background_frame_index = (self.background_frame_index + 1) % len(self.background_gif_frames)
                self.last_background_frame_time = current_time

        # --- Update Chapter Switching Animation ---
        # Animation handles the movement of the map image
        if self.is_animating:
            elapsed_time = current_time - self.animation_start_time
            # Calculate progress (0.0 to 1.0)
            progress = min(elapsed_time / self.animation_duration, 1.0)

            # Check if images needed for animation are still loaded (can fail async or on resize) and target size is calculated
            outgoing_img_original = self.img_originals.get(self.outgoing_chapter_index)
            incoming_img_original = self.img_originals.get(self.incoming_chapter_index)

            outgoing_target_size = self.img_scaled.get(self.outgoing_chapter_index)
            incoming_target_size = self.img_scaled.get(self.incoming_chapter_index)


            # Only calculate positions if both original images and their target sizes are available for animation
            if outgoing_img_original is not None and incoming_img_original is not None and outgoing_target_size and incoming_target_size and outgoing_target_size[0] > 0 and outgoing_target_size[1] > 0 and incoming_target_size[0] > 0 and incoming_target_size[1] > 0:

                screen_width = self.screen.get_size()[0]
                center_x = screen_width // 2

                outgoing_target_width, outgoing_target_height = outgoing_target_size
                incoming_target_width, incoming_target_height = incoming_target_size

                # Calculate starting and ending X positions based on animation direction
                if self.animation_direction == -1: # Slide Left (Incoming from Right)
                    start_x_out = center_x - outgoing_target_width // 2
                    end_x_out = 0 - outgoing_target_width # Off-screen left
                    start_x_in = screen_width # Off-screen right
                    end_x_in = center_x - incoming_target_width // 2 # Center

                elif self.animation_direction == 1: # Slide Right (Incoming from Left)
                    start_x_out = center_x - outgoing_target_width // 2
                    end_x_out = screen_width # Off-screen right
                    start_x_in = 0 - incoming_target_width # Off-screen left
                    end_x_in = center_x - incoming_target_width // 2 # Center

                # Linear interpolation for current X positions
                self.current_x_out = start_x_out + (end_x_out - start_x_out) * progress
                self.current_x_in = start_x_in + (end_x_in - start_x_in) * progress


                if progress >= 1.0:
                    # Animation finished
                    self.is_animating = False
                    # Update current chapter index to the incoming one
                    self.current_chapter_index = self.incoming_chapter_index
                    # Clear temporary animation variables
                    self.outgoing_chapter_index = None
                    self.incoming_chapter_index = None
                    self.current_x_out = None
                    self.current_x_in = None
                    self.animation_direction = 0 # Reset direction
                    # Animation finished, but we don't transition state here.
                    # State transition happens on click event.

            else:
                 # If any needed image or size is not available, stop animation immediately
                 self.is_animating = False
                 self.outgoing_chapter_index = None
                 self.incoming_chapter_index = None
                 self.current_x_out = None
                 self.current_x_in = None
                 self.animation_direction = 0
                 # print("Warning: Animation stopped due to missing image or size information.") # Keep silent during animation


        return None # MainGameScreen update doesn't change state directly


    def draw(self):
        screen_width, screen_height = self.screen.get_size()

        # --- Draw Background ---
        if self.is_background_gif_loaded:
            current_frame = self.background_gif_frames[self.background_frame_index]
            try:
                 # Scale GIF frame and draw to full screen
                 scaled_frame = pygame.transform.smoothscale(current_frame, (screen_width, screen_height))
                 self.screen.blit(scaled_frame, (0, 0))
            except (ValueError, Exception):
                 # Fill with fallback color if scaling fails
                 self.screen.fill(self.fallback_background_color)
        else:
             # Fill with fallback background color if GIF is not loaded
             self.screen.fill(self.fallback_background_color)


        # --- Draw Chapter Image(s) ---
        # Calculate the target center Y for the image(s) (middle-upper)
        target_center_y = self.chapter_image_target_y

        if self.is_animating:
            # Draw both outgoing and incoming images during animation
            outgoing_img_original = self.img_originals.get(self.outgoing_chapter_index)
            incoming_img_original = self.img_originals.get(self.incoming_chapter_index)

            outgoing_target_size = self.img_scaled.get(self.outgoing_chapter_index)
            incoming_target_size = self.img_scaled.get(self.incoming_chapter_index)

            if outgoing_img_original and outgoing_target_size and outgoing_target_size[0] > 0 and outgoing_target_size[1] > 0 and self.current_x_out is not None:
                 try:
                      outgoing_scaled = pygame.transform.scale(outgoing_img_original, outgoing_target_size) # Using scale for fixed size
                      outgoing_w, outgoing_h = outgoing_scaled.get_size()
                      # Calculate drawing Y position based on target center Y
                      draw_y_out = target_center_y - outgoing_h // 2
                      self.screen.blit(outgoing_scaled, (int(self.current_x_out), draw_y_out)) # Use int for blit position
                 except (ValueError, Exception):
                      pass # Ignore drawing if scaling fails


            if incoming_img_original and incoming_target_size and incoming_target_size[0] > 0 and incoming_target_size[1] > 0 and self.current_x_in is not None:
                 try:
                      incoming_scaled = pygame.transform.scale(incoming_img_original, incoming_target_size) # Using scale for fixed size
                      incoming_w, incoming_h = incoming_scaled.get_size()
                      # Calculate drawing Y position based on target center Y
                      draw_y_in = target_center_y - incoming_h // 2
                      self.screen.blit(incoming_scaled, (int(self.current_x_in), draw_y_in)) # Use int for blit position
                      # Update the chapter_image_rect for click detection (based on incoming image)
                      self.chapter_image_rect = incoming_scaled.get_rect(topleft=(int(self.current_x_in), draw_y_in))
                 except (ValueError, Exception):
                      self.chapter_image_rect = None
                      pass # Ignore drawing if scaling fails
                 # Note: The else block for chapter_image_rect was missing here in previous version


            else: # Fallback if images or sizes are missing during animation
                 self.chapter_image_rect = None # No valid rect


        else:
            # Draw only the current chapter image when not animating
            current_img_original = self.img_originals.get(self.current_chapter_index)
            # Get the single target size calculated in _scale_assets for the current map
            img_target_size = self.img_scaled.get(self.current_chapter_index)


            if current_img_original and img_target_size and img_target_size[0] > 0 and img_target_size[1] > 0:
                 try:
                      target_width, target_height = img_target_size
                      # Scale current image to the fixed target size (may cause distortion)
                      current_scaled = pygame.transform.scale(current_img_original, img_target_size)
                      # Calculate drawing position to center it horizontally and align vertically with target_center_y
                      draw_x = screen_width // 2 - target_width // 2
                      draw_y = target_center_y - target_height // 2
                      self.screen.blit(current_scaled, (draw_x, draw_y))
                      # Update the chapter_image_rect for click detection when not animating
                      self.chapter_image_rect = current_scaled.get_rect(topleft=(draw_x, draw_y))
                 except (ValueError, Exception):
                      self.chapter_image_rect = None # Set to None if scaling fails or image is missing
                      pass # Ignore drawing if scaling fails
            else:
                 self.chapter_image_rect = None # Set to None if original image or target size is missing


        # --- Draw Left Arrow (only if not in the first chapter and image loaded) ---
        if self.current_chapter_index > 1 and self.arrow_left_img_scaled and self.arrow_left_rect:
            self.screen.blit(self.arrow_left_img_scaled, self.arrow_left_rect)

        # --- Draw Right Arrow (only if not in the last chapter and image loaded) ---
        if self.current_chapter_index < 4 and self.arrow_right_img_scaled and self.arrow_right_rect: # Assuming 4 chapters
            self.screen.blit(self.arrow_right_img_scaled, self.arrow_right_rect)

        # --- Draw Back Icon ---
        if self.back_icon_scaled and self.back_rect:
             self.screen.blit(self.back_icon_scaled, self.back_rect)


class Screen1:
    # Added back_icon_original parameter
    def __init__(self, screen, font, back_icon_original):
        self.screen = screen
        self.font = font


        # --- Back Icon Properties ---
        self.back_icon_original = back_icon_original
        self.back_icon_scaled = None
        self.back_rect = None # Rect for the back icon click area

        self._scale_assets() # Scale assets on initialization


    def _scale_assets(self):
         screen_width, screen_height = self.screen.get_size()

         # Scale and Position Back Icon
         if self.back_icon_original:
              try:
                   icon_target_height = int(screen_height * BACK_ICON_SIZE_RATIO)
                   icon_aspect = self.back_icon_original.get_width() / max(1, self.back_icon_original.get_height())
                   icon_target_width = int(icon_target_height * icon_aspect)

                   if icon_target_width > 0 and icon_target_height > 0:
                        # Use scale as it's a small icon and quality difference is minimal, but scale is faster
                        self.back_icon_scaled = pygame.transform.scale(self.back_icon_original, (icon_target_width, icon_target_height))
                        # Position in top-left corner with margin
                        back_icon_x = BACK_ICON_MARGIN
                        back_icon_y = BACK_ICON_MARGIN
                        self.back_rect = self.back_icon_scaled.get_rect(topleft=(back_icon_x, back_icon_y))
                   else:
                       self.back_icon_scaled = None
                       self.back_rect = None
              except (ValueError, Exception):
                   self.back_icon_scaled = None
                   self.back_rect = None
         else:
              self.back_icon_scaled = None
              self.back_rect = None


    def handle_event(self, event):
         if event.type == pygame.VIDEORESIZE:
              self._scale_assets() # Rescale assets on window change

         if event.type == pygame.MOUSEBUTTONDOWN:
              # Detect Back Icon click
              if self.back_rect and self.back_rect.collidepoint(event.pos):
                   return MAIN_GAME # Go back to main game screen

         if event.type == pygame.KEYDOWN:
              if event.key == pygame.K_ESCAPE:
                   return MAIN_GAME # Press ESC to go back to main game screen

         return None

    def update(self):
        return None # Simple screens may not need updating

    def draw(self):
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill((50, 50, 150)) # Blue background

        text_rect = self.text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
        self.screen.blit(self.text_surface, text_rect)

        # Draw Back Icon
        if self.back_icon_scaled and self.back_rect:
             self.screen.blit(self.back_icon_scaled, self.back_rect)


class Screen2(Screen1): # Inherit from Screen1 for simplicity
     def __init__(self, screen, font, back_icon_original):
         super().__init__(screen, font, back_icon_original) # Pass the back icon
         self.text_surface = font.render("This is Screen 2", True, (255, 255, 255)) # Override text

class Screen3(Screen1): # Inherit from Screen1 for simplicity
     def __init__(self, screen, font, back_icon_original):
         super().__init__(screen, font, back_icon_original) # Pass the back icon
         self.text_surface = font.render("This is Screen 3", True, (255, 255, 255)) # Override text

class Screen4(Screen1): # Inherit from Screen1 for simplicity
     def __init__(self, screen, font, back_icon_original):
         super().__init__(screen, font, back_icon_original) # Pass the back icon
         self.text_surface = font.render("This is Screen 4", True, (255, 255, 255)) # Override text


# --- Game State Manager ---
class Game:
    def __init__(self):
        self.screen = screen
        self.font = font
        self.state = LOGIN # Initial state

        # Removed the global _target_state_after_loading

        # Pass required original images/data to screens
        self.screens = {
            LOGIN: LoginScreen(self.screen, self.font, login_background_gif_frames_original, login_background_fallback, title_img_original),
            # LOADING1 plays GIF for 1 loop with faster frame duration, fills screen, ignores fallback duration
            # Frame duration set to 0.02 for extra speed
            LOADING1: LoadingScreen(self.screen, self.font, loading1_gif_frames_original, loading1_text_surface, MAIN_GAME, frame_duration_override=0.02, loop_count=1, fallback_duration=None),
            # Pass arrow_left_img_original to MainGameScreen for left arrow, right arrow, and back icon
            # Kuang logic is NOT included in this version
            MAIN_GAME: MainGameScreen(self.screen, self.font, img_originals_main_game, choose_background_gif_frames_original, arrow_left_img_original, arrow_right_img_original, arrow_left_img_original),
            # LOADING2 plays GIF for 1 loop with faster frame duration, fills screen, ignores fallback duration
            # next_state is initially None here, will be set dynamically via tuple return from MainGameScreen
            LOADING2: LoadingScreen(self.screen, self.font, loading2_gif_frames_original, loading2_text_surface, None, frame_duration_override=0.03, loop_count=1, fallback_duration=None), # Frame duration 0.03
            # Pass arrow_left_img_original to Screen1 and its children for the back icon
            SCREEN_1: None,
            SCREEN_2: None,
            SCREEN_3: None,
            SCREEN_4: None,
        }
        self.current_screen = self.screens[self.state]
        self.last_update_time = time.time() # Initialize last update time for dt calculation


    def run(self):
        running = True
        while running:
            # Calculate delta time (time elapsed since last frame) - not strictly needed for current update logic but good practice
            # dt = time.time() - self.last_update_time # Uncomment if update logic uses dt
            # self.last_update_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    # Handle event in the current screen
                    next_state_info = self.current_screen.handle_event(event)
                    if next_state_info:
                         # Check if the returned info is a tuple for state transition (e.g., (LOADING2, SCREEN_X))
                         if isinstance(next_state_info, tuple) and len(next_state_info) == 2:
                             new_state, loading2_target_state = next_state_info
                             # Ensure the first element is a valid state name
                             if new_state in self.screens:
                                  # If transitioning via tuple, check if it's LOADING2 specifically
                                  if new_state == LOADING2:
                                       # If transitioning to LOADING2 via tuple, set LOADING2's next_state immediately
                                       # Ensure the target state for LOADING2 is also a valid state name
                                       if loading2_target_state in self.screens:
                                            self.screens[LOADING2].next_state = loading2_target_state
                                            self.change_state(new_state) # Change state to LOADING2
                                       else:
                                            print(f"Warning: Invalid target state for LOADING2: {loading2_target_state}. Not changing state.")
                                  else:
                                       # Handle other potential tuple returns if needed in the future (e.g., (SOME_STATE, data))
                                       # For now, treat other tuples as simple state changes? Or log a warning?
                                       # Let's log a warning and don't change state unless it's the LOADING2 tuple
                                        print(f"Warning: Received unhandled state tuple: {next_state_info}. Not changing state.")

                             else:
                                  print(f"Warning: Received tuple with invalid state name: {new_state}. Not changing state.")

                         else:
                              # If it's a simple state string, just change state
                              self.change_state(next_state_info)


            # Update the current screen
            next_state_info = self.current_screen.update() # Update doesn't typically need dt in this simple structure
            if next_state_info:
                 # Check if the returned info is a tuple for state transition (less common from update)
                 if isinstance(next_state_info, tuple) and len(next_state_info) == 2:
                      new_state, loading2_target_state = next_state_info
                      # Ensure the first element is a valid state name
                      if new_state in self.screens:
                           # If transitioning via tuple from update, check if it's LOADING2 specifically
                           if new_state == LOADING2:
                                # If transitioning to LOADING2 via tuple from update, set LOADING2's next_state immediately
                                # Ensure the target state for LOADING2 is also a valid state name
                                if loading2_target_state in self.screens:
                                     self.screens[LOADING2].next_state = loading2_target_state
                                     self.change_state(new_state) # Change state to LOADING2
                                else:
                                     print(f"Warning: Invalid target state for LOADING2 from update: {loading2_target_state}. Not changing state.")
                           else:
                                # Handle other potential tuple returns from update if needed
                                # Log a warning and don't change state unless it's the LOADING2 tuple
                                 print(f"Warning: Received unhandled state tuple from update: {next_state_info}. Not changing state.")
                      else:
                           print(f"Warning: Received tuple with invalid state name from update: {new_state}. Not changing state.")

                 else:
                      # If it's a simple state string, just change state
                      self.change_state(next_state_info)


            # Removed the old logic that used the global _target_state_after_loading here


            # Draw the current screen
            self.current_screen.draw()

            pygame.display.flip()

            # Add a small delay to limit frame rate, remove if you want max fps
            # pygame.time.Clock().tick(60) # Optional: cap frame rate to 60 FPS


        pygame.quit()
        sys.exit()

    def change_state(self, new_state):
        # This method expects simple state strings only.
        # Tuple handling (like (LOADING2, target_state)) should be done IN run()
        # BEFORE calling change_state with just the simple state name.

        if new_state in self.screens:
            self.state = new_state
            self.current_screen = self.screens[self.state]
            if isinstance(self.current_screen, LoadingScreen):
                 self.current_screen.fallback_start_time = time.time() # Reset timer for fallback duration
                 self.current_screen.loop_count = 0 # Reset GIF loop count
                 self.current_screen.frame_index = 0 # Reset GIF frame index
                 # Important: LOADING2's next_state is now set in run() when the tuple is received.
                 # We do NOT reset self.current_screen.next_state here for LoadingScreens.
                 # The next_state property holds the target state for the *next* transition FROM the loading screen.

        if new_state not in self.screens:
            print(f"Error: Invalid state requested: {new_state}")
            return

        # 动态初始化SCREEN_1（如果尚未初始化）
        if new_state == SCREEN_1 and self.screens[SCREEN_1] is None:
            try:
                import gameLevel1
                gameLevel1.running = True
                # 关卡完成后自动返回主界面
                self.state = MAIN_GAME
                self.current_screen = self.screens[self.state]
                return
            except (ImportError, AttributeError) as e:
                print(f"Error loading gameLevel1: {e}")
                return
        if new_state == SCREEN_2 and self.screens[SCREEN_2] is None:
            try:
                import gameLevel2
                gameLevel2.running = True
                # 关卡完成后自动返回主界面
                self.state = MAIN_GAME
                self.current_screen = self.screens[self.state]
                return
            except (ImportError, AttributeError) as e:
                print(f"Error loading gameLevel1: {e}")
                return
        if new_state == SCREEN_3 and self.screens[SCREEN_3] is None:
            try:
                import gameLevel3
                gameLevel3.running = True
                # 关卡完成后自动返回主界面
                self.state = MAIN_GAME
                self.current_screen = self.screens[self.state]
                return
            except (ImportError, AttributeError) as e:
                print(f"Error loading gameLevel1: {e}")
                return

        if new_state == SCREEN_4 and self.screens[SCREEN_4] is None:
            try:
                import gameLevel4
                gameLevel4.running = True
                # 关卡完成后自动返回主界面
                self.state = MAIN_GAME
                self.current_screen = self.screens[self.state]
                return
            except (ImportError, AttributeError) as e:
                print(f"Error loading gameLevel1: {e}")
                return

        # 检查目标屏幕是否有效
        if self.screens[new_state] is None:
            print(f"Error: Screen {new_state} is not initialized")
            return

        # 执行状态切换
        self.state = new_state
        self.current_screen = self.screens[self.state]

        # 安全地调用_scale_assets（如果存在）
        if hasattr(self.current_screen, '_scale_assets'):
            self.current_screen._scale_assets()

        # 重置加载屏幕状态
        if isinstance(self.current_screen, LoadingScreen):
            self.current_screen.fallback_start_time = time.time()
            self.current_screen.loop_count = 0
            self.current_screen.frame_index = 0



if __name__ == "__main__":
    game = Game()
    game.run()