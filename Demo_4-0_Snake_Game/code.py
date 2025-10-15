# code.py — Snake with CAP1 (A5) AI toggle + accelerometer steering + mode NeoPixel
#
# Adds thin green border around play area, keeps score/high-score >10,
# plays 210.wav when food is eaten, 140.wav on Game Over,
# and flashes NeoPixel red 3× when the player loses.
#
import time
import board
import digitalio
import touchio
import displayio
import nvm
import struct
import microcontroller
import supervisor
supervisor.runtime.autoreload = False

# --- IMU (ICM-20948) ---
import adafruit_icm20x

# =========================
# AUDIO (from Gesture demo)
# =========================
try:
    from audiocore import WaveFile
    from audioio import AudioOut
    audio = AudioOut(board.DAC)

    _wav210_f = open("210.wav", "rb")
    _wav210 = WaveFile(_wav210_f)

    _wav140_f = open("140.wav", "rb")
    _wav140 = WaveFile(_wav140_f)

    def _audio_play(w):
        try:
            if audio.playing:
                audio.stop()
        except Exception:
            pass
        try:
            audio.play(w)
        except Exception as e:
            print("Audio play error:", e)

    def sfx_food(): _audio_play(_wav210)
    def sfx_gameover(): _audio_play(_wav140)

except Exception as e:
    print("Audio init failed:", e)
    def sfx_food(): pass
    def sfx_gameover(): pass

# =========================
# Mode NeoPixel (status LED + chained pixels)
# =========================
try:
    import neopixel
    PIX_COUNT = 5  # 0 = status/mode pixel, 1..4 = flash group
    _modepix = neopixel.NeoPixel(board.NEOPIXEL, PIX_COUNT, brightness=0.3, auto_write=True)
except Exception:
    _modepix = None

BLUE  = (0, 0, 255)
GREEN = (0, 255, 0)
RED   = (255, 0, 0)
OFF   = (0, 0, 0)

def _set_mode_pixel(demo_mode: bool):
    if not _modepix:
        return
    _modepix[0] = GREEN if demo_mode else BLUE


def flash_neopixel_red(times=3, on_s=0.15, off_s=0.10):
    """
    Flash the *next four* NeoPixels in the chain (indices 1..4) red.
    Leaves pixel 0 (status/mode) alone, then restores it after.
    Gracefully degrades if fewer than 5 pixels are present.
    """
    if not _modepix:
        return

    # Which indices to flash (skip 0 which is the mode LED)
    max_index = min(getattr(_modepix, "n", 1) - 1, 4)
    if max_index <= 0:
        return
    flash_idxs = range(1, max_index + 1)

    # Remember current colors so we can restore (in case you're using them elsewhere)
    saved = [tuple(_modepix[i]) for i in flash_idxs]
    saved0 = tuple(_modepix[0])

    try:
        for _ in range(times):
            for i in flash_idxs: _modepix[i] = RED
            time.sleep(on_s)
            for i in flash_idxs: _modepix[i] = OFF
            time.sleep(off_s)
    finally:
        # Restore the flashed pixels
        for i, c in zip(flash_idxs, saved):
            _modepix[i] = c
        # Restore the mode pixel color based on current DEMO_MODE
        _modepix[0] = saved0 if saved0 != OFF else (GREEN if DEMO_MODE else BLUE)


# =========================
# INPUTS
# =========================
cap_touch = touchio.TouchIn(board.A5)
last_captouch_state = False
DEMO_MODE = False

try:
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT
except Exception:
    led = None

def flash_led(n=3, on_s=0.05, off_s=0.05):
    if not led: return
    for _ in range(n):
        led.value = True;  time.sleep(on_s)
        led.value = False; time.sleep(off_s)

# =========================
# DISPLAY SETUP
# =========================
try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire
from adafruit_st7789 import ST7789

backlight = digitalio.DigitalInOut(microcontroller.pin.PA06)
backlight.direction = digitalio.Direction.OUTPUT
displayio.release_displays()

spi = board.LCD_SPI()
tft_cs = board.LCD_CS
tft_dc = board.D4
backlight.value = False  # active-low backlight

WIDTH = 240
HEIGHT = 135
display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = ST7789(display_bus, rotation=90, width=WIDTH, height=HEIGHT, rowstart=40, colstart=53)

# =========================
# HIGH SCORE STORAGE
# =========================
NVM_MAGIC = b"HSv1"
NVM_FMT = "<4sH"
NVM_SIZE = struct.calcsize(NVM_FMT)
high_score = 0

def _nvm_available():
    return getattr(microcontroller, "nvm", None) is not None

def load_high_score():
    global high_score
    if not _nvm_available() or len(microcontroller.nvm) < NVM_SIZE:
        high_score = 0
        return
    raw = bytes(microcontroller.nvm[0:NVM_SIZE])
    try:
        magic, hs = struct.unpack(NVM_FMT, raw)
        high_score = hs if magic == NVM_MAGIC else 0
    except Exception:
        high_score = 0

def save_high_score():
    if not _nvm_available() or len(microcontroller.nvm) < NVM_SIZE:
        return
    microcontroller.nvm[0:NVM_SIZE] = struct.pack(
        NVM_FMT, NVM_MAGIC, min(high_score, 65535)
    )

# =========================
# RENDER SURFACE
# =========================
GRID_W = 24
GRID_H = 18
BG_RGB, SNAKE_RGB, HEAD_RGB, FOOD_RGB = 0x101018, 0x33FF55, 0x00DDFF, 0xFF3355
SCALE = max(1, min(WIDTH // GRID_W, HEIGHT // GRID_H))
bitmap = displayio.Bitmap(GRID_W, GRID_H, 4)
palette = displayio.Palette(4)
palette[0], palette[1], palette[2], palette[3] = BG_RGB, SNAKE_RGB, FOOD_RGB, HEAD_RGB

tg = displayio.TileGrid(bitmap, pixel_shader=palette)
game_layer = displayio.Group(scale=SCALE,
    x=(WIDTH - GRID_W*SCALE)//2,
    y=(HEIGHT - GRID_H*SCALE)//2)
game_layer.append(tg)

root = displayio.Group()
display.root_group = root
root.append(game_layer)
ui = displayio.Group()
root.append(ui)

# Green border
try:
    from vectorio import Rectangle as VRectangle
    pal = displayio.Palette(1); pal[0] = 0x00FF00
    width_px, height_px = GRID_W*SCALE, GRID_H*SCALE
    x0, y0 = game_layer.x, game_layer.y
    border_group = displayio.Group()
    border_group.append(VRectangle(pixel_shader=pal, x=x0, y=y0-1, width=width_px, height=1))
    border_group.append(VRectangle(pixel_shader=pal, x=x0, y=y0+height_px, width=width_px, height=1))
    border_group.append(VRectangle(pixel_shader=pal, x=x0-1, y=y0, width=1, height=height_px))
    border_group.append(VRectangle(pixel_shader=pal, x=x0+width_px, y=y0, width=1, height=height_px))
    root.append(border_group)
except Exception:
    pass

# =========================
# IMU
# =========================
i2c = board.I2C()
icm = adafruit_icm20x.ICM20948(i2c, 0x69)
ax_f = ay_f = 0.0
LPF_ALPHA = 0.25

# =========================
# GAME STATE
# =========================
UP, DOWN, LEFT, RIGHT = (0,-1), (0,1), (-1,0), (1,0)
snake = [(GRID_W//2 + i, GRID_H//2) for i in range(1,-3,-1)]
direction = RIGHT
food = (GRID_W//3, GRID_H//3)
grow = 0

def place_food():
    global food
    start = ((food[0]+7)%GRID_W, (food[1]+5)%GRID_H)
    snake_set = set(snake)
    for dy in range(GRID_H):
        for dx in range(GRID_W):
            x = (start[0]+dx)%GRID_W
            y = (start[1]+dy)%GRID_H
            if (x,y) not in snake_set:
                food = (x,y); return

def _would_collide(pos, body):
    x,y = pos
    return (x<0) or (y<0) or (x>=GRID_W) or (y>=GRID_H) or (pos in body)

def ai_next_dir(head, body, target, cur_dir):
    body_set = set(body)
    rev = (-cur_dir[0], -cur_dir[1])
    for d in [(1,0),(-1,0),(0,1),(0,-1)]:
        if d==rev: continue
        nx, ny = head[0]+d[0], head[1]+d[1]
        if not _would_collide((nx,ny), body_set): return d
    return cur_dir

# =========================
# INPUTS
# =========================
TILT_THRESH = 2.2
def update_inputs():
    global DEMO_MODE, last_captouch_state, direction, ax_f, ay_f
    cap_now = cap_touch.value
    if cap_now and not last_captouch_state:
        DEMO_MODE = not DEMO_MODE
        _set_mode_pixel(DEMO_MODE)
        flash_led(3)
        print("DEMO_MODE:", DEMO_MODE)
    last_captouch_state = cap_now
    if DEMO_MODE: return
    ax, ay, az = icm.acceleration
    ax_f = (1-LPF_ALPHA)*ax_f + LPF_ALPHA*ax
    ay_f = (1-LPF_ALPHA)*ay_f + LPF_ALPHA*ay
    absx, absy = abs(ax_f), abs(ay_f)
    new_dir = None
    if absx >= absy and absx > TILT_THRESH:
        new_dir = RIGHT if ax_f > 0 else LEFT
    elif absy > TILT_THRESH:
        new_dir = UP if ay_f > 0 else DOWN
    if new_dir:
        rev = (-direction[0], -direction[1])
        if new_dir != rev:
            direction = new_dir

# =========================
# GAME OVER OVERLAY
# =========================
import terminalio
from adafruit_display_text import bitmap_label
score = 0
score_label = bitmap_label.Label(terminalio.FONT, text="0", color=0xFFFFFF,
    scale=2, anchor_point=(1.0,0.0), anchored_position=(WIDTH-2,2))
ui.append(score_label)
def update_score_label(): score_label.text = str(score)

def _flash_screen_red(duration=0.15):
    old_bg = palette[0]; palette[0] = 0xFF0000
    for y in range(GRID_H):
        for x in range(GRID_W): bitmap[x,y]=0
    time.sleep(duration)
    palette[0] = old_bg

def _show_game_over_stats(duration=3.0):
    overlay = displayio.Group()
    title = bitmap_label.Label(terminalio.FONT, text="Game Over", color=0xFFFFFF,
        scale=4, anchor_point=(0.5,0.5), anchored_position=(WIDTH//2, HEIGHT//2-14))
    stats = bitmap_label.Label(terminalio.FONT,
        text=f"Score: {score}   High: {high_score}",
        color=0xFFFFFF, scale=2,
        anchor_point=(0.5,0.0), anchored_position=(WIDTH//2, HEIGHT//2+8))
    overlay.append(title); overlay.append(stats); ui.append(overlay)
    time.sleep(duration); ui.remove(overlay)

def game_over_sequence():
    sfx_gameover()
    flash_neopixel_red()     # <-- new: flash NeoPixel red 3×
    _flash_screen_red(0.15)
    _show_game_over_stats(3.0)

# =========================
# GAME LOGIC
# =========================
def reset_game(reset_score=True):
    global snake, direction, grow, score
    snake = [(GRID_W//2+i, GRID_H//2) for i in range(1,-3,-1)]
    direction = RIGHT
    grow = 0
    if reset_score:
        score = 0
        update_score_label()

def step_game():
    global direction, grow, snake, food, score, high_score
    if DEMO_MODE:
        direction = ai_next_dir(snake[0], snake, food, direction)
    nx, ny = snake[0][0]+direction[0], snake[0][1]+direction[1]
    out_of_bounds = (nx<0) or (ny<0) or (nx>=GRID_W) or (ny>=GRID_H)
    hit_self = (nx,ny) in snake
    if out_of_bounds or hit_self:
        game_over_sequence()
        reset_game(reset_score=not DEMO_MODE)
        return
    snake.insert(0,(nx,ny))
    if (nx,ny)==food:
        if not DEMO_MODE:
            score += 1
            update_score_label()
            sfx_food()
            if score>high_score:
                high_score=score
                try: save_high_score()
                except Exception: pass
        grow += 2
        place_food()
    if grow>0: grow -= 1
    else: snake.pop()

def render():
    for y in range(GRID_H):
        for x in range(GRID_W): bitmap[x,y]=0
    bitmap[food[0],food[1]]=2
    for i,(x,y) in enumerate(snake): bitmap[x,y]=3 if i==0 else 1

# =========================
# MAIN LOOP
# =========================
load_high_score()
_set_mode_pixel(False)
TICK_S = 0.12
last_tick = 0
while True:
    update_inputs()
    now = time.monotonic()
    if now - last_tick >= TICK_S:
        last_tick = now
        step_game()
        render()
    time.sleep(0.005)
