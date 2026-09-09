import os
import math
import random
import numpy as np
import pygame
import pymunk
from moviepy import ImageSequenceClip
from google import genai
import os
from dotenv import load_dotenv

def generate_caption(api_key):
    """Fetches a dynamic, motivational caption and hashtags from Gemini."""
    # Initialize the client with the new SDK structure
    client = genai.Client(api_key=api_key)
    
    prompt = (
        "Write a short, engaging Instagram Reel caption about perseverance, "
        "focus, and solving puzzles. Include a hook, a very brief motivational "
        "thought, and exactly 5 trending hashtags related to #satisfying, #maze, "
        "and #gaming. Output ONLY the caption text, without any conversational filler."
    )
    
    print("Generating fresh caption via Gemini...")
    # The new generate_content call requires the 'contents' parameter
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt
    )
    
    return response.text.strip()

import cloudinary
import cloudinary.uploader

def upload_to_cloudinary(file_path, cloud_name, api_key, api_secret):
    """Uploads the local MP4 to Cloudinary and returns the public URL."""
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )
    
    print(f"Uploading {file_path} to Cloudinary...")
    
    # resource_type="video" is strictly required for .mp4 files
    response = cloudinary.uploader.upload(
        file_path, 
        resource_type="video",
        folder="instagram_reels"
    )
    
    video_url = response.get("secure_url")
    print(f"Upload complete! Video URL: {video_url}")
    return video_url

import requests
import time

def post_to_instagram(video_url, caption, ig_user_id, access_token):
    """Creates a Reels container, waits for processing, and publishes."""
    base_url = "https://graph.facebook.com/v19.0"
    
    # --- Step 1: Create the Container ---
    print("Creating Instagram Reel container...")
    container_payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": access_token
    }
    
    # Post to the user's media endpoint
    container_response = requests.post(f"{base_url}/{ig_user_id}/media", data=container_payload).json()
    
    if "id" not in container_response:
        print("Error creating container:", container_response)
        return
        
    creation_id = container_response["id"]
    print(f"Container created (ID: {creation_id}). Polling Meta for processing status...")
    
    # --- Step 2: Poll for Processing Status ---
    status = "IN_PROGRESS"
    attempts = 0
    max_attempts = 12 # Will try for a maximum of 2 minutes (12 attempts * 10 seconds)
    
    while status != "FINISHED" and attempts < max_attempts:
        time.sleep(10) # Wait 10 seconds between checks
        
        # Query the specific container's status
        status_response = requests.get(
            f"{base_url}/{creation_id}",
            params={"fields": "status_code", "access_token": access_token}
        ).json()
        
        status = status_response.get("status_code", "ERROR")
        print(f"Processing status: {status} (Attempt {attempts + 1})")
        
        if status == "ERROR":
            print("Meta encountered an error processing the video:", status_response)
            return
            
        attempts += 1
        
    if status != "FINISHED":
        print("Video processing timed out. Cannot publish right now.")
        return

    # --- Step 3: Publish the Container ---
    print("Video ready! Publishing Reel...")
    publish_payload = {
        "creation_id": creation_id,
        "access_token": access_token
    }
    
    # Post to the user's media_publish endpoint
    publish_response = requests.post(f"{base_url}/{ig_user_id}/media_publish", data=publish_payload).json()
    
    if "id" in publish_response:
        print(f"Success! Reel published instantly. Post ID: {publish_response['id']}")
    else:
        print("Error publishing:", publish_response)

# --- Video Configuration ---
WIDTH, HEIGHT = 1080, 1920
FPS = 60
SIM_SECONDS = 20
TOTAL_FRAMES = FPS * SIM_SECONDS
DT = 1.0 / FPS

# Initialize Pygame in headless mode
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.font.init()
screen = pygame.Surface((WIDTH, HEIGHT))

# Fonts
title_font = pygame.font.SysFont("Arial", 44, bold=True)
subtitle_font = pygame.font.SysFont("Arial", 22, bold=True)
small_font = pygame.font.SysFont("Arial", 24, bold=True)
banner_font = pygame.font.SysFont("Arial", 52, bold=True)
powerup_font = pygame.font.SysFont("Arial", 28, bold=True)

CENTER = pymunk.Vec2d(WIDTH // 2, HEIGHT // 2 + 50)
RADII = [305, 245, 185, 125, 65]
BALL_RADIUS = 12

# --- Curated Aesthetic Color Palettes for Viral Reels ---
COLOR_PALETTES = [
    {
        "name": "Cyber Neon",
        "bg": (10, 14, 26),
        "walls": [(0, 220, 255), (0, 180, 240), (0, 150, 220), (0, 120, 200), (0, 95, 180)],
        "wall_accent": (0, 255, 220),
        "ball": (255, 225, 50),
        "ball_glow": (255, 200, 30, 70),
        "trail": (80, 200, 255),
        "gap": (255, 60, 130),
        "sparks": (255, 230, 100),
        "goal_bg": (15, 35, 55),
        "goal_ring": (0, 255, 180),
        "goal_core": (0, 255, 180),
        "text_primary": (245, 250, 255),
        "text_secondary": (120, 150, 190),
        "win_accent": (0, 255, 180),
        "pacman": (255, 235, 30),
    },
    {
        "name": "Sunset Synthwave",
        "bg": (22, 10, 32),
        "walls": [(255, 95, 105), (245, 75, 130), (225, 55, 160), (195, 45, 190), (160, 40, 210)],
        "wall_accent": (255, 140, 90),
        "ball": (255, 220, 60),
        "ball_glow": (255, 200, 50, 80),
        "trail": (240, 90, 150),
        "gap": (255, 210, 60),
        "sparks": (255, 240, 120),
        "goal_bg": (45, 15, 50),
        "goal_ring": (255, 110, 180),
        "goal_core": (255, 210, 70),
        "text_primary": (255, 245, 250),
        "text_secondary": (180, 130, 180),
        "win_accent": (255, 110, 180),
        "pacman": (255, 230, 40),
    },
    {
        "name": "Emerald & Gold",
        "bg": (8, 20, 18),
        "walls": [(46, 204, 113), (39, 174, 96), (30, 150, 85), (25, 130, 75), (20, 110, 65)],
        "wall_accent": (80, 240, 150),
        "ball": (255, 205, 40),
        "ball_glow": (255, 190, 30, 80),
        "trail": (46, 204, 113),
        "gap": (235, 87, 87),
        "sparks": (255, 225, 90),
        "goal_bg": (15, 45, 35),
        "goal_ring": (255, 205, 40),
        "goal_core": (46, 204, 113),
        "text_primary": (240, 255, 245),
        "text_secondary": (120, 175, 150),
        "win_accent": (255, 215, 50),
        "pacman": (255, 220, 40),
    },
    {
        "name": "Arctic Glacier",
        "bg": (10, 18, 30),
        "walls": [(120, 220, 255), (90, 195, 245), (65, 170, 230), (45, 145, 215), (30, 120, 195)],
        "wall_accent": (180, 240, 255),
        "ball": (255, 130, 45),
        "ball_glow": (255, 110, 30, 80),
        "trail": (100, 210, 255),
        "gap": (255, 80, 80),
        "sparks": (255, 180, 80),
        "goal_bg": (18, 35, 55),
        "goal_ring": (130, 230, 255),
        "goal_core": (255, 140, 50),
        "text_primary": (240, 250, 255),
        "text_secondary": (130, 165, 195),
        "win_accent": (100, 230, 255),
        "pacman": (255, 235, 40),
    },
    {
        "name": "Tokyo Violet",
        "bg": (16, 12, 30),
        "walls": [(175, 105, 255), (150, 85, 240), (130, 68, 220), (110, 52, 195), (90, 40, 170)],
        "wall_accent": (210, 150, 255),
        "ball": (0, 240, 220),
        "ball_glow": (0, 220, 200, 80),
        "trail": (175, 105, 255),
        "gap": (255, 85, 150),
        "sparks": (80, 255, 230),
        "goal_bg": (32, 20, 55),
        "goal_ring": (0, 240, 220),
        "goal_core": (190, 120, 255),
        "text_primary": (250, 245, 255),
        "text_secondary": (165, 145, 190),
        "win_accent": (0, 240, 220),
        "pacman": (255, 235, 40),
    },
    {
        "name": "Obsidian Gold",
        "bg": (14, 14, 16),
        "walls": [(225, 185, 90), (200, 160, 75), (175, 138, 60), (150, 116, 48), (125, 95, 38)],
        "wall_accent": (255, 215, 130),
        "ball": (245, 245, 250),
        "ball_glow": (255, 255, 255, 80),
        "trail": (220, 180, 90),
        "gap": (230, 80, 80),
        "sparks": (255, 235, 140),
        "goal_bg": (35, 30, 18),
        "goal_ring": (235, 195, 95),
        "goal_core": (255, 255, 255),
        "text_primary": (255, 250, 240),
        "text_secondary": (170, 160, 140),
        "win_accent": (255, 210, 80),
        "pacman": (255, 220, 40),
    },
]

def generate_procedural_palette():
    """Generates a harmonious custom color palette if custom randomness is desired."""
    base_hue = random.random()
    def hsv_to_rgb(h, s, v):
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
        return int(r * 255), int(g * 255), int(b * 255)

    bg = hsv_to_rgb(base_hue, 0.65, 0.08)
    wall_hue = (base_hue + 0.5) % 1.0
    walls = [hsv_to_rgb(wall_hue, 0.75, 0.95 - 0.12 * i) for i in range(5)]
    ball_hue = (wall_hue + 0.33) % 1.0
    ball = hsv_to_rgb(ball_hue, 0.85, 0.98)
    goal_hue = (wall_hue + 0.66) % 1.0
    return {
        "name": f"Harmonic #{int(base_hue*1000)}",
        "bg": bg,
        "walls": walls,
        "wall_accent": hsv_to_rgb(wall_hue, 0.45, 0.98),
        "ball": ball,
        "ball_glow": (*ball, 75),
        "trail": walls[0],
        "gap": hsv_to_rgb((wall_hue + 0.25) % 1.0, 0.8, 0.95),
        "sparks": (255, 240, 140),
        "goal_bg": hsv_to_rgb(goal_hue, 0.7, 0.18),
        "goal_ring": hsv_to_rgb(goal_hue, 0.8, 0.95),
        "goal_core": ball,
        "text_primary": (250, 250, 255),
        "text_secondary": (150, 160, 180),
        "win_accent": hsv_to_rgb(goal_hue, 0.8, 0.95),
        "pacman": (255, 235, 40),
    }

def pick_color_scheme():
    """Picks a new color palette on each run."""
    if random.random() < 0.85:
        palette = random.choice(COLOR_PALETTES)
    else:
        palette = generate_procedural_palette()
    return palette

# --- Physics & Maze Generator with Pac-Man Power-Up ---
def create_simulation(seed, palette):
    """
    Creates physics simulation featuring the Pac-Man gravity-reversing power-up.
    Returns: space, ball_body, rings, sparks, sim_state
    """
    rng = random.Random(seed)
    space = pymunk.Space()

    # Simulation State
    sim_state = {
        "powerup_pos": pymunk.Vec2d(CENTER.x + rng.uniform(-25, 25), CENTER.y + 270),
        "powerup_collected": False,
        "gravity_reversed": False,
        "collect_time": None,
        "collect_frame": None,
    }

    # Gravity controller: Downward until power-up is touched, then reversed inward vortex
    def dynamic_gravity(body, gravity, damping, dt):
        pymunk.Body.update_velocity(body, pymunk.Vec2d(0, 0), damping, dt)
        if not sim_state["gravity_reversed"]:
            # Normal downward gravity pulls ball into bottom channel toward Pac-Man
            body.velocity += pymunk.Vec2d(0, 1100) * dt
        else:
            # Reversed / Inward gravity vortex pulls ball into center
            down = pymunk.Vec2d(0, 850)
            delta = CENTER - body.position
            dist = delta.length
            inward = delta.normalized() * 1450 if dist > 14 else pymunk.Vec2d(0, 0)
            body.velocity += (down + inward) * dt

    # Dynamic Ball
    ball_body = pymunk.Body(1.0, pymunk.moment_for_circle(1.0, 0, BALL_RADIUS))
    ball_body.position = (CENTER.x, CENTER.y - 370)
    ball_body.velocity_func = dynamic_gravity
    ball_shape = pymunk.Circle(ball_body, BALL_RADIUS)
    ball_shape.elasticity = 0.35
    ball_shape.friction = 0.35
    ball_shape.collision_type = 2
    space.add(ball_body, ball_shape)

    # Collision spark collector
    sparks = []
    def on_collision(arbiter, space_ref, data):
        if arbiter.contact_point_set.points:
            pt = arbiter.contact_point_set.points[0].point_a
            count = rng.randint(3, 6)
            for _ in range(count):
                ang = rng.uniform(0, 2 * math.pi)
                spd = rng.uniform(50, 180)
                vx = math.cos(ang) * spd
                vy = math.sin(ang) * spd
                sparks.append([pt.x, pt.y, vx, vy, rng.uniform(0.25, 0.45), 1.0])
        return True

    # Pymunk 7.x collision handler
    space.on_collision(1, 2, begin=on_collision)

    # Target drop times for the 5 tiers (paced so completion occurs at ~14-17s)
    base_times = [1.0, 3.5, 6.5, 9.8, 13.0]
    jitter = [rng.uniform(-0.1, 0.1) for _ in base_times]
    target_times = [b + j for b, j in zip(base_times, jitter)]

    # Alternating rotation speeds (rad/s)
    base_speeds = [0.9, -1.1, 1.2, -1.3, 1.4]
    speed_mods = [rng.uniform(0.95, 1.05) for b in base_speeds]
    speeds = [b * m for b, m in zip(base_speeds, speed_mods)]

    rings = []
    for i, r in enumerate(RADII):
        body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        body.position = CENTER
        body.angular_velocity = speeds[i]
        space.add(body)

        t_drop = target_times[i]
        settle_angle = math.pi / 2 + (0.22 if speeds[i] > 0 else -0.22)

        if i == 0:
            gap_ang = -math.pi / 2
            body.angular_velocity = 0.0
            gap_w = 0.35
        else:
            gap_ang = (settle_angle - speeds[i] * t_drop) % (2 * math.pi)
            gap_w = 46.0 / r  # Linear gap width ~92px

        num_segs = 84
        shapes = []
        for s in range(num_segs):
            a1 = 2 * math.pi * s / num_segs
            a2 = 2 * math.pi * (s + 1) / num_segs
            mid = (a1 + a2) / 2
            diff = math.atan2(math.sin(mid - gap_ang), math.cos(mid - gap_ang))
            if abs(diff) < gap_w:
                continue
            p1 = (r * math.cos(a1), r * math.sin(a1))
            p2 = (r * math.cos(a2), r * math.sin(a2))
            seg = pymunk.Segment(body, p1, p2, 4)
            seg.elasticity = 0.35
            seg.friction = 0.35
            seg.collision_type = 1
            shapes.append(seg)

        # Decorative teeth on upper half (away from bottom rolling zone)
        teeth_count = rng.randint(2, 3)
        for t_idx in range(teeth_count):
            tooth_ang = (gap_ang + math.pi * 0.6 + (t_idx * 1.8 / teeth_count)) % (2 * math.pi)
            tooth_len = rng.uniform(10, 16)
            p_base = (r * math.cos(tooth_ang), r * math.sin(tooth_ang))
            p_tip = ((r - tooth_len) * math.cos(tooth_ang), (r - tooth_len) * math.sin(tooth_ang))
            seg_tooth = pymunk.Segment(body, p_base, p_tip, 3)
            seg_tooth.elasticity = 0.35
            seg_tooth.collision_type = 1
            shapes.append(seg_tooth)

        space.add(*shapes)
        rings.append({
            "body": body,
            "shapes": shapes,
            "radius": r,
            "speed": speeds[i],
            "gap_ang": gap_ang,
            "gap_w": gap_w,
            "color": palette["walls"][i],
        })

    # Center cradle cup
    goal_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    goal_body.position = CENTER
    space.add(goal_body)
    goal_shapes = []
    for s in range(24):
        a1 = math.pi * 0.15 + (math.pi * 0.7) * s / 24
        a2 = math.pi * 0.15 + (math.pi * 0.7) * (s + 1) / 24
        p1 = (24 * math.cos(a1), 24 * math.sin(a1))
        p2 = (24 * math.cos(a2), 24 * math.sin(a2))
        seg = pymunk.Segment(goal_body, p1, p2, 3)
        seg.elasticity = 0.15
        seg.friction = 0.6
        goal_shapes.append(seg)
    space.add(*goal_shapes)

    return space, ball_body, rings, sparks, sim_state

def validate_maze(seed, palette):
    """
    Simulates the physics in fast headless memory to ensure:
    1) Pac-Man power-up is touched within 2-5 seconds.
    2) Gravity reverses and the ball solves the maze to center within 13-17.5s.
    """
    space, ball_body, rings, _, sim_state = create_simulation(seed, palette)
    win_time = None

    for step in range(TOTAL_FRAMES):
        t = step / FPS
        if t >= 0.55 and rings[0]["body"].angular_velocity == 0.0:
            rings[0]["body"].angular_velocity = rings[0]["speed"]

        # Check power-up touch
        if not sim_state["powerup_collected"]:
            dist_to_p = (ball_body.position - sim_state["powerup_pos"]).length
            if dist_to_p < 35 and t > 0.8:
                sim_state["powerup_collected"] = True
                sim_state["gravity_reversed"] = True
                sim_state["collect_time"] = t

        space.step(DT)
        dist = (ball_body.position - CENTER).length
        if sim_state["powerup_collected"] and dist < 42 and t > 2.0:
            win_time = t
            break

    if sim_state["powerup_collected"] and win_time is not None and 13.0 <= win_time <= 17.5:
        return True, win_time, sim_state["collect_time"]
    return False, win_time, None

def find_validated_seed(palette):
    """
    Tests random seeds until a 100% verified solvable pattern with Pac-Man power-up is found.
    """
    for attempt in range(100):
        test_seed = random.randint(10000, 999999)
        valid, win_t, collect_t = validate_maze(test_seed, palette)
        if valid:
            print(f"Validated solvable maze pattern (Seed: {test_seed}) - Power-up at {collect_t:.2f}s, Center reached at {win_t:.2f}s!")
            return test_seed, win_t
    return 603, 17.06

# --- Drawing Helpers ---
def draw_gradient_background(surface, top_color, bottom_color):
    """Draws a subtle vertical gradient."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def draw_glowing_circle(surface, color, center, radius, glow_width=8, alpha=60):
    """Draws a circle with a soft outer glow."""
    glow_surf = pygame.Surface((radius * 2 + glow_width * 4, radius * 2 + glow_width * 4), pygame.SRCALPHA)
    glow_center = (radius + glow_width * 2, radius + glow_width * 2)
    for g in range(glow_width, 0, -2):
        g_alpha = int(alpha * (1 - g / glow_width))
        pygame.draw.circle(glow_surf, (*color[:3], g_alpha), glow_center, radius + g)
    pygame.draw.circle(glow_surf, color[:3], glow_center, radius)
    surface.blit(glow_surf, (center[0] - glow_center[0], center[1] - glow_center[1]))

def draw_pacman_sprite(surface, pos, size=15, frame_t=0.0, color=(255, 235, 35)):
    """Draws an animated retro Pac-Man power-up sprite with chomp animation and glow."""
    px, py = int(pos.x), int(pos.y)
    # Gentle bobbing animation
    bob_y = py + int(math.sin(frame_t * 8.0) * 4)

    # Chomp mouth angle (animates between 0.05 and 0.38 radians)
    chomp = abs(math.sin(frame_t * 12.0)) * 0.35 * math.pi
    base_dir = math.pi # Facing left toward incoming ball

    # Soft glowing aura
    draw_glowing_circle(surface, (*color, 70), (px, bob_y), size + 4, glow_width=8, alpha=75)

    # Pac-Man pie wedge body
    num_pts = 24
    points = [(px, bob_y)]
    start_a = base_dir + chomp
    end_a = base_dir + 2 * math.pi - chomp
    for i in range(num_pts + 1):
        a = start_a + (end_a - start_a) * i / num_pts
        points.append((px + int(size * math.cos(a)), bob_y + int(size * math.sin(a))))
    pygame.draw.polygon(surface, color, points)

    # Pac-Man eye
    eye_x = px + int(size * 0.35 * math.cos(base_dir + 0.9))
    eye_y = bob_y + int(size * 0.35 * math.sin(base_dir + 0.9))
    pygame.draw.circle(surface, (20, 20, 20), (eye_x, eye_y), max(2, int(size * 0.14)))

    # Floating mini energizer dots around Pac-Man
    for d_idx in range(3):
        dot_ang = frame_t * 4.0 + (d_idx * 2 * math.pi / 3)
        dot_r = size + 10
        dx = px + int(dot_r * math.cos(dot_ang))
        dy = bob_y + int(dot_r * math.sin(dot_ang))
        pygame.draw.circle(surface, (255, 255, 255), (dx, dy), 2)

# --- Main Generation Function ---
def generate_reel(output_path="final_reel_silent.mp4"):
    palette = pick_color_scheme()
    print(f"Theme Selected: {palette['name']}")

    print("Generating and verifying procedural maze pattern with Pac-Man power-up...")
    seed, expected_win_t = find_validated_seed(palette)

    space, ball_body, rings, sparks, sim_state = create_simulation(seed, palette)

    bg_top = palette["bg"]
    bg_bottom = (max(0, bg_top[0] - 8), max(0, bg_top[1] - 8), max(0, bg_top[2] - 8))
    bg_surface = pygame.Surface((WIDTH, HEIGHT))
    draw_gradient_background(bg_surface, bg_top, bg_bottom)

    # Decorative concentric guide rings
    for r in range(80, 420, 60):
        pygame.draw.circle(bg_surface, (255, 255, 255), (int(CENTER.x), int(CENTER.y)), r, 1)

    trail = []
    frames = []
    won = False
    win_frame = None
    confetti = []
    powerup_sparks = []
    powerup_flash_time = None

    print("Simulating physics and recording video frames...")
    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / FPS

        if t >= 0.55 and rings[0]["body"].angular_velocity == 0.0:
            rings[0]["body"].angular_velocity = rings[0]["speed"]

        # Check Pac-Man power-up collection
        if not sim_state["powerup_collected"]:
            dist_to_p = (ball_body.position - sim_state["powerup_pos"]).length
            if dist_to_p < 35 and t > 0.8:
                sim_state["powerup_collected"] = True
                sim_state["gravity_reversed"] = True
                sim_state["collect_time"] = t
                sim_state["collect_frame"] = frame_idx
                powerup_flash_time = t
                # Spawn power-up collection burst
                ppos = sim_state["powerup_pos"]
                for _ in range(35):
                    ang = random.uniform(0, 2 * math.pi)
                    spd = random.uniform(80, 260)
                    powerup_sparks.append([
                        ppos.x, ppos.y,
                        math.cos(ang) * spd,
                        math.sin(ang) * spd,
                        random.uniform(0.4, 0.8), # life
                        random.choice([palette["pacman"], (255, 255, 255), palette["win_accent"]])
                    ])

        space.step(DT)
        dist = (ball_body.position - CENTER).length

        # Trigger win when ball reaches goal
        if not won and sim_state["powerup_collected"] and dist < 42 and t > 2.0:
            won = True
            win_frame = frame_idx
            ball_body.velocity = (0, 0)
            ball_body.body_type = pymunk.Body.KINEMATIC
            for _ in range(80):
                c_ang = random.uniform(0, 2 * math.pi)
                c_spd = random.uniform(80, 380)
                confetti.append([
                    CENTER.x, CENTER.y,
                    math.cos(c_ang) * c_spd,
                    math.sin(c_ang) * c_spd,
                    random.uniform(0.6, 1.2),
                    random.choice([
                        palette["win_accent"],
                        palette["ball"],
                        palette["gap"],
                        palette["wall_accent"],
                        palette["pacman"],
                        (255, 255, 255)
                    ])
                ])

        if won:
            # Smoothly settle ball into dead center
            ball_body.position += (CENTER - ball_body.position) * 0.12

        trail.append((ball_body.position.x, ball_body.position.y))
        if len(trail) > 28:
            trail.pop(0)

        # Update sparks
        new_sparks = []
        for sx, sy, svx, svy, life, alpha in sparks:
            life -= DT
            if life > 0:
                sx += svx * DT
                sy += svy * DT
                svy += 400 * DT
                alpha = max(0.0, life / 0.4)
                new_sparks.append([sx, sy, svx, svy, life, alpha])
        sparks = new_sparks

        # Update power-up collection sparks
        new_pu_sparks = []
        for px, py, pvx, pvy, life, pcolor in powerup_sparks:
            life -= DT
            if life > 0:
                px += pvx * DT
                py += pvy * DT
                new_pu_sparks.append([px, py, pvx, pvy, life, pcolor])
        powerup_sparks = new_pu_sparks

        if won:
            new_confetti = []
            for cx, cy, cvx, cvy, csize, ccolor in confetti:
                cx += cvx * DT
                cy += cvy * DT
                cvy += 500 * DT
                cvx *= 0.98
                new_confetti.append([cx, cy, cvx, cvy, csize, ccolor])
            confetti = new_confetti

        # --- RENDERING ---
        screen.blit(bg_surface, (0, 0))

        # Title & Dynamic Subtitle
        caption_text = title_font.render("REACH THE CENTER", True, palette["text_primary"])
        caption_rect = caption_text.get_rect(center=(WIDTH // 2, 88))
        screen.blit(caption_text, caption_rect)

        if not sim_state["powerup_collected"]:
            sub_str = "FALL DOWN. GET THE POWER-UP!"
            sub_col = palette["pacman"]
        elif won:
            sub_str = "CENTER REACHED! CHALLENGE COMPLETE!"
            sub_col = palette["win_accent"]
        else:
            sub_str = "GRAVITY REVERSED! ASCENDING TO CENTER!"
            sub_col = palette["wall_accent"]

        subtitle_text = subtitle_font.render(sub_str, True, sub_col)
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, 132))
        screen.blit(subtitle_text, subtitle_rect)

        # Dynamic Level Badge
        current_level = 1
        for i, r in enumerate(RADII):
            if dist <= r:
                current_level = i + 1

        if won:
            status_text_str = "CENTER REACHED!"
            status_color = palette["win_accent"]
        elif sim_state["gravity_reversed"]:
            status_text_str = f"LEVEL {min(5, current_level)}/5 (REVERSED)"
            status_color = palette["wall_accent"]
        else:
            status_text_str = "FALLING DOWN"
            status_color = palette["text_primary"]

        pill_w, pill_h = 230 if sim_state["gravity_reversed"] and not won else 160, 36
        pill_rect = pygame.Rect(WIDTH // 2 - pill_w // 2, 164, pill_w, pill_h)
        pygame.draw.rect(screen, (palette["bg"][0] + 15, palette["bg"][1] + 15, palette["bg"][2] + 20), pill_rect, border_radius=18)
        pygame.draw.rect(screen, status_color, pill_rect, 2, border_radius=18)

        status_text = small_font.render(status_text_str, True, status_color)
        screen.blit(status_text, status_text.get_rect(center=(WIDTH // 2, 182)))

        # Center Goal
        pulse = math.sin(t * 5.0) * 4
        pygame.draw.circle(screen, palette["goal_bg"], (int(CENTER.x), int(CENTER.y)), int(36 + pulse))
        pygame.draw.circle(screen, palette["goal_ring"], (int(CENTER.x), int(CENTER.y)), int(28 + pulse * 0.5), 3)
        pygame.draw.circle(screen, palette["goal_core"], (int(CENTER.x), int(CENTER.y)), 9)

        # Rotating Maze Rings & Teeth
        for ring in rings:
            body = ring["body"]
            ring_color = ring["color"]
            for seg in ring["shapes"]:
                p1 = body.position + seg.a.rotated(body.angle)
                p2 = body.position + seg.b.rotated(body.angle)
                pygame.draw.line(screen, ring_color, (int(p1.x), int(p1.y)), (int(p2.x), int(p2.y)), int(seg.radius * 2))

            gap_pos = body.position + pymunk.Vec2d(ring["radius"], 0).rotated(body.angle + ring["gap_ang"])
            pygame.draw.circle(screen, palette["gap"], (int(gap_pos.x), int(gap_pos.y)), 6)

        # Pac-Man Power-Up Sprite (if not yet collected)
        if not sim_state["powerup_collected"]:
            draw_pacman_sprite(screen, sim_state["powerup_pos"], size=16, frame_t=t, color=palette["pacman"])
            # Little label below Pac-Man
            pu_label = subtitle_font.render("POWER UP", True, palette["pacman"])
            screen.blit(pu_label, pu_label.get_rect(center=(int(sim_state["powerup_pos"].x), int(sim_state["powerup_pos"].y) + 26)))

        # Power-Up Collection Flash & Starburst
        for px, py, _, _, life, pcolor in powerup_sparks:
            pr = max(2, int(6 * (life / 0.8)))
            pygame.draw.circle(screen, pcolor, (int(px), int(py)), pr)

        # "GRAVITY REVERSED!" announcement banner when collected
        if sim_state["powerup_collected"] and powerup_flash_time and (t - powerup_flash_time) < 2.2:
            flash_dt = t - powerup_flash_time
            # Expanding shockwave ripple
            ripple_r = int(flash_dt * 180)
            if ripple_r > 0:
                ripple_alpha = max(0, int(220 * (1 - flash_dt / 2.2)))
                rip_surf = pygame.Surface((ripple_r * 2, ripple_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(rip_surf, (*palette["pacman"], ripple_alpha), (ripple_r, ripple_r), ripple_r, 3)
                screen.blit(rip_surf, (int(sim_state["powerup_pos"].x - ripple_r), int(sim_state["powerup_pos"].y - ripple_r)))

            # Centered pop-up banner
            pop_text = powerup_font.render("⚡ GRAVITY REVERSED! ⚡", True, palette["pacman"])
            pop_rect = pop_text.get_rect(center=(WIDTH // 2, int(CENTER.y + 160)))
            pop_box = pygame.Rect(pop_rect.x - 16, pop_rect.y - 6, pop_rect.width + 32, pop_rect.height + 12)
            pygame.draw.rect(screen, (palette["bg"][0] + 30, palette["bg"][1] + 30, palette["bg"][2] + 45), pop_box, border_radius=10)
            pygame.draw.rect(screen, palette["pacman"], pop_box, 2, border_radius=10)
            screen.blit(pop_text, pop_rect)

        # Motion Trail
        for i, (tx, ty) in enumerate(trail):
            tr_ratio = i / len(trail)
            tr_radius = max(2, int(BALL_RADIUS * 0.8 * tr_ratio))
            tr_color = (*palette["trail"], int(140 * tr_ratio))
            trail_surf = pygame.Surface((tr_radius * 2, tr_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, tr_color, (tr_radius, tr_radius), tr_radius)
            screen.blit(trail_surf, (int(tx - tr_radius), int(ty - tr_radius)))

        # Sparks
        for sx, sy, _, _, _, s_alpha in sparks:
            sp_r = max(2, int(5 * s_alpha))
            sp_surf = pygame.Surface((sp_r * 4, sp_r * 4), pygame.SRCALPHA)
            pygame.draw.circle(sp_surf, (*palette["sparks"], int(255 * s_alpha)), (sp_r * 2, sp_r * 2), sp_r)
            screen.blit(sp_surf, (int(sx - sp_r * 2), int(sy - sp_r * 2)))

        # Ball with 3D Sphere Shading & Supercharged Aura
        bx, by = int(ball_body.position.x), int(ball_body.position.y)
        # If gravity is reversed, supercharge the ball glow!
        if sim_state["gravity_reversed"]:
            glow_col = palette["pacman"]
            draw_glowing_circle(screen, (*glow_col, 90), (bx, by), BALL_RADIUS + 7, glow_width=10, alpha=90)
        else:
            draw_glowing_circle(screen, palette["ball_glow"], (bx, by), BALL_RADIUS + 5, glow_width=8, alpha=70)

        pygame.draw.circle(screen, palette["ball"], (bx, by), BALL_RADIUS)
        hi_x = bx - int(BALL_RADIUS * 0.32)
        hi_y = by - int(BALL_RADIUS * 0.32)
        pygame.draw.circle(screen, (255, 255, 255), (hi_x, hi_y), int(BALL_RADIUS * 0.35))

        roll_ang = ball_body.angle
        dot_dist = BALL_RADIUS * 0.55
        dot_x = bx + int(dot_dist * math.cos(roll_ang))
        dot_y = by + int(dot_dist * math.sin(roll_ang))
        pygame.draw.circle(screen, (40, 40, 40), (dot_x, dot_y), 3)

        if won:
            for cx, cy, _, _, csize, ccolor in confetti:
                cp_r = int(4 * csize)
                if cp_r > 0 and 0 <= cx < WIDTH and 0 <= cy < HEIGHT:
                    pygame.draw.circle(screen, ccolor, (int(cx), int(cy)), cp_r)

            win_scale = min(1.0, (frame_idx - win_frame) / 20.0)
            win_text = banner_font.render("YOU MADE IT!", True, palette["win_accent"])
            win_rect = win_text.get_rect(center=(WIDTH // 2, 1140))
            glow_box = pygame.Rect(win_rect.x - 20, win_rect.y - 8, win_rect.width + 40, win_rect.height + 16)
            pygame.draw.rect(screen, (palette["bg"][0] + 25, palette["bg"][1] + 25, palette["bg"][2] + 35), glow_box, border_radius=12)
            pygame.draw.rect(screen, palette["win_accent"], glow_box, 3, border_radius=12)
            screen.blit(win_text, win_rect)
        else:
            time_left = max(0.0, SIM_SECONDS - t)
            time_text = small_font.render(f"{time_left:04.1f}s", True, palette["text_secondary"])
            screen.blit(time_text, time_text.get_rect(center=(WIDTH // 2, 1140)))

        raw_str = pygame.image.tostring(screen, "RGB")
        frame_array = np.frombuffer(raw_str, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
        frames.append(frame_array)

    print(f"Assembling video: {output_path}...")
    video = ImageSequenceClip(frames, fps=FPS)
    video.write_videofile(
        output_path,
        codec="libx264",
        fps=FPS
    )
    print(f"Video successfully generated: {output_path}")

if __name__ == "__main__":
    # Load the hidden keys from the .env file
    load_dotenv()

    # Fetch the credentials securely
    MY_GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUD_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUD_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

    IG_USER_ID = os.getenv("META_IG_USER_ID")
    META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")

    # 1. Generate Caption
    daily_caption = generate_caption(MY_GEMINI_KEY)
    print(f"\n--- Today's Caption ---\n{daily_caption}\n-----------------------\n")

    # 2. Render Video
    video_path = "final_reel_silent.mp4"
    generate_reel(video_path)

    # 3. Stage Video on Cloudinary
    public_video_url = upload_to_cloudinary(video_path, CLOUD_NAME, CLOUD_API_KEY, CLOUD_API_SECRET)

    # 4. Publish to Instagram
    if public_video_url:
        post_to_instagram(public_video_url, daily_caption, IG_USER_ID, META_ACCESS_TOKEN)