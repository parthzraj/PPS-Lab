
import pygame
import random
import math
import sys
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


SCREEN_W, SCREEN_H = 960, 640
TILE = 48
FPS  = 60
FONT_PATH = None          

BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
RED     = (220,  50,  50)
DARK_RED= (140,  20,  20)
GREEN   = ( 60, 200,  60)
DARK_GREEN=(20, 120,  20)
BLUE    = ( 60, 100, 220)
GOLD    = (255, 200,  40)
ORANGE  = (255, 140,  20)
PURPLE  = (160,  40, 200)
CYAN    = ( 40, 200, 220)
BROWN   = (120,  80,  40)
GRAY    = (120, 120, 120)
DGRAY   = ( 60,  60,  60)
LGRAY   = (180, 180, 180)
CREAM   = (240, 220, 180)

BG_COLOR     = ( 18,  12,  24)
WALL_COLOR   = ( 55,  45,  70)
WALL_LIT     = ( 80,  65, 100)
FLOOR_COLOR  = ( 38,  32,  48)
FLOOR_LIT    = ( 55,  48,  68)

WALL  = 0
FLOOR = 1
DOOR  = 2
CHEST = 3
STAIR = 4

ITEMS = {
    "Health Potion":  {"type": "consumable", "effect": "heal",   "value": 30,  "color": RED,    "symbol": "+"},
    "Mana Potion":    {"type": "consumable", "effect": "mana",   "value": 25,  "color": BLUE,   "symbol": "~"},
    "Iron Sword":     {"type": "weapon",     "effect": "attack", "value": 8,   "color": LGRAY,  "symbol": "/"},
    "Fire Staff":     {"type": "weapon",     "effect": "attack", "value": 14,  "color": ORANGE, "symbol": "|"},
    "Leather Armor":  {"type": "armor",      "effect": "defense","value": 5,   "color": BROWN,  "symbol": "]"},
    "Chain Mail":     {"type": "armor",      "effect": "defense","value": 10,  "color": GRAY,   "symbol": "#"},
    "Gold Coin":      {"type": "gold",       "effect": "gold",   "value": 20,  "color": GOLD,   "symbol": "$"},
    "Gem":            {"type": "gold",       "effect": "gold",   "value": 50,  "color": CYAN,   "symbol": "*"},
}


class Room:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.cx = x + w // 2
        self.cy = y + h // 2

    def intersects(self, other, padding=1):
        return (self.x - padding < other.x + other.w and
                self.x + self.w + padding > other.x and
                self.y - padding < other.y + other.h and
                self.y + self.h + padding > other.y)


def generate_map(cols, rows, num_rooms=12):
    grid = [[WALL] * cols for _ in range(rows)]
    rooms: List[Room] = []

    for _ in range(200):
        w = random.randint(5, 11)
        h = random.randint(4, 9)
        x = random.randint(1, cols - w - 1)
        y = random.randint(1, rows - h - 1)
        r = Room(x, y, w, h)
        if any(r.intersects(existing) for existing in rooms):
            continue
        # carve floor
        for ry in range(r.y, r.y + r.h):
            for rx in range(r.x, r.x + r.w):
                grid[ry][rx] = FLOOR
        # connect to previous room
        if rooms:
            prev = rooms[-1]
            # horizontal then vertical corridor
            sx, ex = sorted([r.cx, prev.cx])
            for cx in range(sx, ex + 1):
                grid[prev.cy][cx] = FLOOR
            sy, ey = sorted([r.cy, prev.cy])
            for cy in range(sy, ey + 1):
                grid[cy][r.cx] = FLOOR
        rooms.append(r)
        if len(rooms) >= num_rooms:
            break

    # place special tiles
    if len(rooms) >= 2:
        sr = rooms[0]
        er = rooms[-1]
        grid[er.cy][er.cx] = STAIR

        # chests in random rooms
        for room in random.sample(rooms[1:-1], min(4, len(rooms) - 2)):
            cx = random.randint(room.x + 1, room.x + room.w - 2)
            cy = random.randint(room.y + 1, room.y + room.h - 2)
            grid[cy][cx] = CHEST

    start = (rooms[0].cx, rooms[0].cy) if rooms else (2, 2)
    return grid, rooms, start


# ─────────────────────────── Entity base ──────────────────────────
class Entity:
    def __init__(self, x, y, color, symbol, name):
        self.x = float(x)
        self.y = float(y)
        self.color  = color
        self.symbol = symbol
        self.name   = name
        self.alive  = True

    @property
    def tile_x(self): return int(self.x)
    @property
    def tile_y(self): return int(self.y)


# ─────────────────────────── Player ───────────────────────────────
class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, CREAM, "@", "Hero")
        self.max_hp   = 100
        self.hp       = 100
        self.max_mana = 60
        self.mana     = 60
        self.attack   = 12
        self.defense  = 3
        self.speed    = 4.0          # tiles/sec
        self.level    = 1
        self.xp       = 0
        self.xp_next  = 50
        self.gold     = 0
        self.inventory: List[str] = []
        self.equipped_weapon: Optional[str] = None
        self.equipped_armor:  Optional[str] = None
        self.attack_cooldown = 0.0
        self.attack_rate     = 0.5   # seconds between attacks
        self.invincible      = 0.0
        self.invincible_time = 0.8

    def effective_attack(self):
        bonus = ITEMS[self.equipped_weapon]["value"] if self.equipped_weapon else 0
        return self.attack + bonus

    def effective_defense(self):
        bonus = ITEMS[self.equipped_armor]["value"] if self.equipped_armor else 0
        return self.defense + bonus

    def gain_xp(self, amount):
        self.xp += amount
        msgs = []
        while self.xp >= self.xp_next:
            self.xp     -= self.xp_next
            self.level  += 1
            self.xp_next = int(self.xp_next * 1.4)
            self.max_hp  += 15
            self.hp       = min(self.hp + 30, self.max_hp)
            self.max_mana += 8
            self.attack  += 2
            msgs.append(f"Level Up! Now level {self.level}!")
        return msgs

    def heal(self, amount):
        self.hp = min(self.hp + amount, self.max_hp)

    def use_item(self, item_name):
        data = ITEMS[item_name]
        msg = ""
        if data["type"] == "consumable":
            if data["effect"] == "heal":
                self.heal(data["value"])
                msg = f"Restored {data['value']} HP!"
            elif data["effect"] == "mana":
                self.mana = min(self.mana + data["value"], self.max_mana)
                msg = f"Restored {data['value']} Mana!"
            self.inventory.remove(item_name)
        elif data["type"] == "weapon":
            self.equipped_weapon = item_name
            msg = f"Equipped {item_name}!"
        elif data["type"] == "armor":
            self.equipped_armor  = item_name
            msg = f"Equipped {item_name}!"
        elif data["type"] == "gold":
            self.gold += data["value"]
            self.inventory.remove(item_name)
            msg = f"+{data['value']} gold!"
        return msg



ENEMY_TYPES = {
    "Goblin":    {"hp": 22,  "atk": 6,  "def": 1,  "spd": 2.2, "xp": 15,  "color": GREEN,   "sym": "g"},
    "Skeleton":  {"hp": 30,  "atk": 9,  "def": 2,  "spd": 1.8, "xp": 20,  "color": LGRAY,   "sym": "s"},
    "Orc":       {"hp": 55,  "atk": 14, "def": 4,  "spd": 1.5, "xp": 35,  "color": DARK_GREEN,"sym":"o"},
    "Vampire":   {"hp": 45,  "atk": 16, "def": 3,  "spd": 2.8, "xp": 45,  "color": PURPLE,  "sym": "v"},
    "Dragon":    {"hp": 120, "atk": 25, "def": 8,  "spd": 1.8, "xp": 120, "color": ORANGE,  "sym": "D"},
}


class Enemy(Entity):
    def __init__(self, x, y, etype):
        d = ENEMY_TYPES[etype]
        super().__init__(x, y, d["color"], d["sym"], etype)
        self.max_hp  = d["hp"]
        self.hp      = d["hp"]
        self.attack  = d["atk"]
        self.defense = d["def"]
        self.speed   = d["spd"]
        self.xp_drop = d["xp"]
        self.state   = "idle"       
        self.atk_cd  = 0.0
        self.atk_rate= 1.2
        self.aggro_r = 7.0           
        self.path_timer = 0.0

    def take_damage(self, amount):
        dmg = max(1, amount - self.defense)
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False
        return dmg



class Particle:
    def __init__(self, x, y, vx, vy, color, life):
        self.x, self.y   = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.life  = life
        self.max_life = life

    def update(self, dt):
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.vy += 80 * dt   
        self.life -= dt
        return self.life > 0

    def draw(self, surf, cam_x, cam_y):
        alpha = self.life / self.max_life
        r = max(1, int(4 * alpha))
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        c  = tuple(int(ch * alpha) for ch in self.color)
        pygame.draw.circle(surf, c, (sx, sy), r)



class FloatText:
    def __init__(self, text, x, y, color, size=18):
        self.text  = text
        self.x, self.y = x, y
        self.color = color
        self.life  = 1.2
        self.size  = size

    def update(self, dt):
        self.y    -= 40 * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surf, cam_x, cam_y, fonts):
        alpha = min(1.0, self.life / 0.5)
        c = tuple(int(ch * alpha) for ch in self.color)
        img = fonts[self.size].render(self.text, True, c)
        surf.blit(img, (self.x - cam_x - img.get_width()//2,
                        self.y - cam_y - img.get_height()//2))



class GroundItem:
    def __init__(self, x, y, item_name):
        self.x, self.y   = x, y        #
        self.item_name   = item_name
        self.bob_timer   = random.uniform(0, math.pi * 2)

    def update(self, dt):
        self.bob_timer += dt * 2

    def draw(self, surf, cam_x, cam_y, fonts):
        d   = ITEMS[self.item_name]
        bob = math.sin(self.bob_timer) * 4
        sx  = int(self.x * TILE + TILE//2 - cam_x)
        sy  = int(self.y * TILE + TILE//2 - cam_y + bob)
        pygame.draw.circle(surf, d["color"], (sx, sy), 10)
        pygame.draw.circle(surf, WHITE,      (sx, sy), 10, 2)
        txt = fonts[16].render(d["symbol"], True, BLACK)
        surf.blit(txt, (sx - txt.get_width()//2, sy - txt.get_height()//2))



class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Dungeon of Shadows")
        self.clock  = pygame.time.Clock()

        
        self.fonts  = {
            16: pygame.font.SysFont("monospace", 16, bold=True),
            18: pygame.font.SysFont("monospace", 18, bold=True),
            20: pygame.font.SysFont("monospace", 20, bold=True),
            24: pygame.font.SysFont("monospace", 24, bold=True),
            32: pygame.font.SysFont("monospace", 32, bold=True),
            48: pygame.font.SysFont("monospace", 48, bold=True),
        }

        self.state   = "title"   
        self.dungeon_level = 1
        self.messages: List[Tuple[str, float]] = []  

        self._init_level()

    
    def _init_level(self):
        cols, rows = 50, 38
        self.cols, self.rows = cols, rows
        self.grid, self.rooms, start = generate_map(cols, rows,
                                                     num_rooms=10 + self.dungeon_level)
        self.player = Player(*start)
        self.enemies:     List[Enemy]      = []
        self.ground_items:List[GroundItem] = []
        self.particles:   List[Particle]   = []
        self.float_texts: List[FloatText]  = []
        self.opened_chests = set()
        self.inv_selected  = 0

        self._spawn_enemies()
        self._spawn_ground_items()

        
        self._tile_surf = {}
        for kind, base, lit in [(WALL, WALL_COLOR, WALL_LIT),
                                  (FLOOR, FLOOR_COLOR, FLOOR_LIT)]:
            for is_lit, col in [(False, base), (True, lit)]:
                s = pygame.Surface((TILE, TILE))
                s.fill(col)
                if kind == WALL:
                    
                    pygame.draw.rect(s, tuple(min(255,c+20) for c in col), (0,0,TILE,4))
                    pygame.draw.rect(s, tuple(max(0,c-20)  for c in col), (0,TILE-4,TILE,4))
                else:
                    
                    pygame.draw.rect(s, tuple(max(0,c-12)  for c in col), (0,0,TILE,1))
                    pygame.draw.rect(s, tuple(max(0,c-12)  for c in col), (0,0,1,TILE))
                self._tile_surf[(kind, is_lit)] = s

    def _spawn_enemies(self):
        types = list(ENEMY_TYPES.keys())
        for room in self.rooms[1:]:
            count = random.randint(1, 2 + self.dungeon_level // 2)
            for _ in range(count):
                
                pool = types[:min(len(types), 2 + self.dungeon_level)]
                etype = random.choice(pool)
                ex = random.randint(room.x + 1, room.x + room.w - 2)
                ey = random.randint(room.y + 1, room.y + room.h - 2)
                self.enemies.append(Enemy(ex, ey, etype))

    def _spawn_ground_items(self):
        all_names = list(ITEMS.keys())
        for room in random.sample(self.rooms, min(5, len(self.rooms))):
            name = random.choice(all_names)
            ix   = random.randint(room.x + 1, room.x + room.w - 2)
            iy   = random.randint(room.y + 1, room.y + room.h - 2)
            if self.grid[iy][ix] == FLOOR:
                self.ground_items.append(GroundItem(ix, iy, name))

    
    def add_msg(self, text, color=CREAM):
        self.messages.insert(0, [text, 4.0, color])
        if len(self.messages) > 8:
            self.messages.pop()

    
    def spawn_hit_particles(self, wx, wy, color, n=8):
        for _ in range(n):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(40, 120)
            self.particles.append(Particle(
                wx, wy,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                color, random.uniform(0.3, 0.7)
            ))

    
    def camera(self):
        cx = self.player.x * TILE + TILE//2 - SCREEN_W//2
        cy = self.player.y * TILE + TILE//2 - SCREEN_H//2
        return cx, cy

    
    def is_lit(self, tx, ty, radius=7):
        dx = tx - self.player.tile_x
        dy = ty - self.player.tile_y
        return dx*dx + dy*dy <= radius*radius

    
    def walkable(self, tx, ty):
        if tx < 0 or ty < 0 or tx >= self.cols or ty >= self.rows:
            return False
        return self.grid[ty][tx] in (FLOOR, STAIR, CHEST)

   
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                self.handle_event(event)

            if   self.state == "playing":   self.update(dt)
            elif self.state == "title":     pass
            elif self.state == "inventory": pass

            self.draw()
            pygame.display.flip()

    
    def handle_event(self, event):
        if self.state == "title":
            if event.type == pygame.KEYDOWN:
                self.state = "playing"

        elif self.state == "playing":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "inventory"
                elif event.key == pygame.K_e:
                    self.interact()

        elif self.state == "inventory":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_i):
                    self.state = "playing"
                elif event.key == pygame.K_UP:
                    self.inv_selected = max(0, self.inv_selected - 1)
                elif event.key == pygame.K_DOWN:
                    inv = self.player.inventory
                    self.inv_selected = min(len(inv) - 1, self.inv_selected + 1)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.use_selected_item()

        elif self.state in ("game_over", "win"):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.__init__()
                    self.state = "playing"

    def interact(self):
        p = self.player
        
        for dx, dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]:
            tx, ty = p.tile_x + dx, p.tile_y + dy
            if self.grid[ty][tx] == CHEST and (tx,ty) not in self.opened_chests:
                self.opened_chests.add((tx,ty))
                name = random.choice(list(ITEMS.keys()))
                p.inventory.append(name)
                self.add_msg(f"Chest! Found {name}!", GOLD)
                self.spawn_hit_particles(tx*TILE+TILE//2, ty*TILE+TILE//2, GOLD)
                return
        
        for gi in list(self.ground_items):
            if gi.x == p.tile_x and gi.y == p.tile_y:
                p.inventory.append(gi.item_name)
                self.ground_items.remove(gi)
                self.add_msg(f"Picked up {gi.item_name}!", CYAN)
                return

    def use_selected_item(self):
        p   = self.player
        inv = p.inventory
        if not inv:
            return
        idx  = min(self.inv_selected, len(inv)-1)
        name = inv[idx]
        msg  = p.use_item(name)
        if msg:
            self.add_msg(msg, GOLD)
        self.inv_selected = max(0, min(self.inv_selected, len(p.inventory)-1))

   
    def update(self, dt):
        p = self.player
        if not p.alive:
            self.state = "game_over"
            return

        
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1

        if dx != 0 and dy != 0:
            dx *= 0.707; dy *= 0.707

        nx = p.x + dx * p.speed * dt
        ny = p.y + dy * p.speed * dt

        if self.walkable(int(nx), p.tile_y): p.x = nx
        if self.walkable(p.tile_x, int(ny)): p.y = ny

        
        if self.grid[p.tile_y][p.tile_x] == STAIR:
            self.dungeon_level += 1
            if self.dungeon_level > 5:
                self.state = "win"
                return
            self.add_msg(f"Descending to level {self.dungeon_level}...", GOLD)
            old_player = self.player
            self._init_level()
            
            self.player.hp       = old_player.hp
            self.player.max_hp   = old_player.max_hp
            self.player.mana     = old_player.mana
            self.player.max_mana = old_player.max_mana
            self.player.attack   = old_player.attack
            self.player.defense  = old_player.defense
            self.player.level    = old_player.level
            self.player.xp       = old_player.xp
            self.player.xp_next  = old_player.xp_next
            self.player.gold     = old_player.gold
            self.player.inventory           = old_player.inventory
            self.player.equipped_weapon     = old_player.equipped_weapon
            self.player.equipped_armor      = old_player.equipped_armor
            return

        
        p.attack_cooldown = max(0, p.attack_cooldown - dt)
        if keys[pygame.K_SPACE] and p.attack_cooldown == 0:
            self._player_attack()
            p.attack_cooldown = p.attack_rate

       
        p.invincible = max(0, p.invincible - dt)

        
        for e in self.enemies:
            if not e.alive: continue
            self._update_enemy(e, dt)

        self.enemies = [e for e in self.enemies if e.alive]

        
        for gi in self.ground_items:
            gi.update(dt)

        
        self.particles   = [p2 for p2 in self.particles   if p2.update(dt)]
        self.float_texts = [ft for ft in self.float_texts if ft.update(dt)]

        
        for m in self.messages:
            m[1] -= dt
        self.messages = [m for m in self.messages if m[1] > 0]

        
        p.mana = min(p.max_mana, p.mana + 3 * dt)

    def _player_attack(self):
        p   = self.player
        atk = p.effective_attack()
        hit = False
        for e in self.enemies:
            if not e.alive: continue
            dist = math.hypot(e.x - p.x, e.y - p.y)
            if dist < 1.8:
                dmg = e.take_damage(atk + random.randint(-2, 4))
                wx  = e.x * TILE + TILE//2
                wy  = e.y * TILE + TILE//2
                self.spawn_hit_particles(wx, wy, RED)
                self.float_texts.append(FloatText(f"-{dmg}", wx, wy, RED))
                hit = True
                if not e.alive:
                    msgs = p.gain_xp(e.xp_drop)
                    for msg in msgs:
                        self.add_msg(msg, GOLD)
                    self.add_msg(f"Defeated {e.name}! +{e.xp_drop} XP", GREEN)
                    
                    if random.random() < 0.4:
                        name = random.choice(list(ITEMS.keys()))
                        self.ground_items.append(GroundItem(e.tile_x, e.tile_y, name))
        if not hit:
            self.add_msg("Missed!", LGRAY)

    def _update_enemy(self, e: Enemy, dt):
        p    = self.player
        dist = math.hypot(e.x - p.x, e.y - p.y)

        
        if dist < e.aggro_r:
            e.state = "chase"
        elif e.state == "chase" and dist > e.aggro_r * 1.5:
            e.state = "idle"

        if e.state == "chase":
           
            if dist > 0.9:
                ddx = (p.x - e.x) / dist
                ddy = (p.y - e.y) / dist
                nx  = e.x + ddx * e.speed * dt
                ny  = e.y + ddy * e.speed * dt
                if self.walkable(int(nx), e.tile_y): e.x = nx
                if self.walkable(e.tile_x, int(ny)): e.y = ny

            
            e.atk_cd = max(0, e.atk_cd - dt)
            if dist < 1.3 and e.atk_cd == 0:
                if p.invincible == 0:
                    dmg = max(1, e.attack - p.effective_defense() + random.randint(-2,2))
                    p.hp -= dmg
                    p.invincible = p.invincible_time
                    if p.hp <= 0:
                        p.hp    = 0
                        p.alive = False
                    wx = p.x * TILE + TILE//2
                    wy = p.y * TILE + TILE//2
                    self.spawn_hit_particles(wx, wy, ORANGE, 6)
                    self.float_texts.append(FloatText(f"-{dmg}", wx, wy - 20, ORANGE))
                    self.add_msg(f"{e.name} hits you for {dmg}!", RED)
                e.atk_cd = e.atk_rate

    
    def draw(self):
        self.screen.fill(BG_COLOR)
        if   self.state == "title":     self.draw_title()
        elif self.state == "playing":   self.draw_game()
        elif self.state == "inventory": self.draw_game(); self.draw_inventory()
        elif self.state == "game_over": self.draw_game(); self.draw_game_over()
        elif self.state == "win":       self.draw_win()

    
    def draw_title(self):
        s = self.screen
        s.fill((10, 8, 18))
        
        t = pygame.time.get_ticks() / 1000
        for i in range(80):
            rx = (i * 137 + 23) % SCREEN_W
            ry = (i * 79  + 11) % SCREEN_H
            br = int(128 + 127 * math.sin(t + i))
            pygame.draw.circle(s, (br, br, br), (rx, ry), 1)

        title = self.fonts[48].render("DUNGEON OF SHADOWS", True, GOLD)
        sub   = self.fonts[20].render("A Pygame RPG Adventure", True, LGRAY)
        tip   = self.fonts[18].render("Press any key to begin your quest...", True, CREAM)
        ctrl  = self.fonts[16].render(
            "WASD/Arrows: Move   Space: Attack   E: Interact   ESC: Inventory", True, GRAY)

        cx = SCREEN_W // 2
        s.blit(title, (cx - title.get_width()//2, 160))
        s.blit(sub,   (cx - sub.get_width()//2,   230))

        
        if int(t * 2) % 2 == 0:
            s.blit(tip, (cx - tip.get_width()//2, 340))

        s.blit(ctrl,  (cx - ctrl.get_width()//2, SCREEN_H - 60))

        
        for i, (name, etype) in enumerate(ENEMY_TYPES.items()):
            col = etype["color"]
            lbl = self.fonts[16].render(f"{etype['sym']} {name}", True, col)
            s.blit(lbl, (60 + i * 170, SCREEN_H - 120))

    
    def draw_game(self):
        s        = self.screen
        cam_x, cam_y = self.camera()
        p        = self.player

        
        for ty in range(self.rows):
            for tx in range(self.cols):
                sx = tx * TILE - int(cam_x)
                sy = ty * TILE - int(cam_y)
                if sx + TILE < 0 or sy + TILE < 0 or sx > SCREEN_W or sy > SCREEN_H:
                    continue
                lit  = self.is_lit(tx, ty)
                kind = self.grid[ty][tx]
                base = WALL if kind == WALL else FLOOR

                tile_img = self._tile_surf.get((base, lit))
                if tile_img:
                    s.blit(tile_img, (sx, sy))
                else:
                    col = WALL_LIT if (base==WALL and lit) else \
                          WALL_COLOR if base==WALL else \
                          FLOOR_LIT if lit else FLOOR_COLOR
                    pygame.draw.rect(s, col, (sx, sy, TILE, TILE))

                
                if lit:
                    if kind == STAIR:
                        self._draw_tile_symbol(s, sx, sy, ">", GOLD)
                    elif kind == CHEST:
                        opened = (tx, ty) in self.opened_chests
                        col2   = DGRAY if opened else GOLD
                        self._draw_tile_symbol(s, sx, sy, "░" if opened else "▣", col2)

        
        for gi in self.ground_items:
            if self.is_lit(gi.x, gi.y):
                gi.draw(s, int(cam_x), int(cam_y), self.fonts)

        
        for e in self.enemies:
            if not self.is_lit(e.tile_x, e.tile_y): continue
            ex = int(e.x * TILE + TILE//2 - cam_x)
            ey = int(e.y * TILE + TILE//2 - cam_y)
            r  = 16
            pygame.draw.circle(s, e.color,       (ex, ey), r)
            pygame.draw.circle(s, BLACK,          (ex, ey), r, 2)
            sym = self.fonts[20].render(e.symbol.upper(), True, BLACK)
            s.blit(sym, (ex - sym.get_width()//2, ey - sym.get_height()//2))
            
            bar_w = 36
            ratio = e.hp / e.max_hp
            pygame.draw.rect(s, DARK_RED, (ex - bar_w//2, ey - r - 10, bar_w, 6))
            pygame.draw.rect(s, RED,      (ex - bar_w//2, ey - r - 10, int(bar_w*ratio), 6))

       
        px = int(p.x * TILE + TILE//2 - cam_x)
        py = int(p.y * TILE + TILE//2 - cam_y)
        r  = 18
        
        if p.invincible > 0 and int(p.invincible * 10) % 2 == 0:
            col_p = WHITE
        else:
            col_p = CREAM
        pygame.draw.circle(s, col_p, (px, py), r)
        pygame.draw.circle(s, GOLD,  (px, py), r, 3)
        sym = self.fonts[20].render("@", True, BLACK)
        s.blit(sym, (px - sym.get_width()//2, py - sym.get_height()//2))

        
        for part in self.particles:
            part.draw(s, int(cam_x), int(cam_y))

        
        for ft in self.float_texts:
            ft.draw(s, int(cam_x), int(cam_y), self.fonts)

        
        self.draw_hud()

    def _draw_tile_symbol(self, surf, sx, sy, sym, color):
        img = self.fonts[20].render(sym, True, color)
        surf.blit(img, (sx + TILE//2 - img.get_width()//2,
                        sy + TILE//2 - img.get_height()//2))

    
    def draw_hud(self):
        s  = self.screen
        p  = self.player
        pad= 10

        
        panel = pygame.Surface((260, 120), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 160))
        s.blit(panel, (pad, pad))

        
        self._draw_bar(s, pad+10, pad+10, 200, 16, p.hp, p.max_hp, RED, DARK_RED, "HP")
        
        self._draw_bar(s, pad+10, pad+34, 200, 16, p.mana, p.max_mana, BLUE, (20,20,100), "MP")
        
        self._draw_bar(s, pad+10, pad+58, 200, 12, p.xp, p.xp_next, PURPLE, (60,20,80), "XP")

        
        stats = (f"Lv{p.level}  ATK:{p.effective_attack()}  DEF:{p.effective_defense()}  "
                 f"Gold:{p.gold}")
        t = self.fonts[16].render(stats, True, LGRAY)
        s.blit(t, (pad+10, pad + 78))

        
        dl = self.fonts[16].render(f"Dungeon Lv {self.dungeon_level}/5", True, GOLD)
        s.blit(dl, (pad+10, pad + 98))

        
        if self.player.attack_cooldown > 0:
            ratio = self.player.attack_cooldown / self.player.attack_rate
            pygame.draw.rect(s, ORANGE, (SCREEN_W//2 - 30, SCREEN_H - 20, int(60*(1-ratio)), 8))
            pygame.draw.rect(s, DGRAY,  (SCREEN_W//2 - 30, SCREEN_H - 20, 60, 8), 2)

        
        tip = self.fonts[16].render("E:Interact  Space:Attack  ESC:Inventory", True, GRAY)
        s.blit(tip, (SCREEN_W - tip.get_width() - 10, SCREEN_H - 24))

        
        for i, m in enumerate(self.messages[:5]):
            alpha = min(255, int(255 * m[1] / 2))
            col   = m[2] if len(m) > 2 else CREAM
            col   = tuple(min(255, c) for c in col)
            txt   = self.fonts[16].render(m[0], True, col)
            s.blit(txt, (pad, SCREEN_H - 40 - i*20))

        
        self.draw_minimap()

    def _draw_bar(self, surf, x, y, w, h, val, maxv, fg, bg, label):
        ratio = max(0, val / maxv) if maxv > 0 else 0
        pygame.draw.rect(surf, bg, (x, y, w, h))
        pygame.draw.rect(surf, fg, (x, y, int(w * ratio), h))
        pygame.draw.rect(surf, WHITE, (x, y, w, h), 1)
        txt = self.fonts[16].render(f"{label} {int(val)}/{int(maxv)}", True, WHITE)
        surf.blit(txt, (x + 4, y + h//2 - txt.get_height()//2))

    def draw_minimap(self):
        s    = self.screen
        mw   = min(self.cols, 80)
        mh   = min(self.rows, 60)
        ts   = 4
        ox   = SCREEN_W - mw*ts - 10
        oy   = SCREEN_H - mh*ts - 40

        surf = pygame.Surface((mw*ts, mh*ts), pygame.SRCALPHA)
        surf.fill((0,0,0,180))
        for ty in range(mh):
            for tx in range(mw):
                if not self.is_lit(tx, ty): continue
                k   = self.grid[ty][tx]
                col = FLOOR_LIT if k in (FLOOR,STAIR,CHEST,DOOR) else WALL_LIT
                if k == STAIR: col = GOLD
                if k == CHEST: col = BROWN
                pygame.draw.rect(surf, col, (tx*ts, ty*ts, ts-1, ts-1))

        
        for e in self.enemies:
            if self.is_lit(e.tile_x, e.tile_y):
                pygame.draw.rect(surf, e.color,
                                 (e.tile_x*ts, e.tile_y*ts, ts, ts))
        
        pygame.draw.rect(surf, CREAM,
                         (self.player.tile_x*ts, self.player.tile_y*ts, ts+1, ts+1))

        s.blit(surf, (ox, oy))
        pygame.draw.rect(s, GRAY, (ox, oy, mw*ts, mh*ts), 1)

    
    def draw_inventory(self):
        s   = self.screen
        p   = self.player
        pw  = 400
        ph  = 480
        px2 = SCREEN_W//2 - pw//2
        py2 = SCREEN_H//2 - ph//2

        
        dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        dim.fill((0,0,0,160))
        s.blit(dim, (0,0))

        
        pygame.draw.rect(s, (30,22,45), (px2, py2, pw, ph))
        pygame.draw.rect(s, GOLD,       (px2, py2, pw, ph), 2)

        title = self.fonts[24].render("── INVENTORY ──", True, GOLD)
        s.blit(title, (px2 + pw//2 - title.get_width()//2, py2 + 12))

        
        eq_w  = self.fonts[18].render(f"Weapon: {p.equipped_weapon or 'None'}", True, LGRAY)
        eq_a  = self.fonts[18].render(f"Armor:  {p.equipped_armor  or 'None'}", True, LGRAY)
        s.blit(eq_w, (px2 + 20, py2 + 50))
        s.blit(eq_a, (px2 + 20, py2 + 72))

        pygame.draw.line(s, GRAY, (px2+10, py2+98), (px2+pw-10, py2+98), 1)

        
        inv = p.inventory
        if not inv:
            empty = self.fonts[18].render("(empty)", True, GRAY)
            s.blit(empty, (px2 + 20, py2 + 110))
        else:
            for i, name in enumerate(inv):
                y_pos = py2 + 108 + i * 28
                if i == self.inv_selected:
                    pygame.draw.rect(s, (80,60,120), (px2+10, y_pos-2, pw-20, 26))
                d   = ITEMS[name]
                col = d["color"]
                sym = self.fonts[18].render(f"{d['symbol']} {name}", True, col)
                typ = self.fonts[16].render(f"[{d['type']}  +{d['value']}]", True, GRAY)
                s.blit(sym, (px2 + 20, y_pos))
                s.blit(typ, (px2 + pw - typ.get_width() - 20, y_pos + 2))

        
        pygame.draw.line(s, GRAY, (px2+10, py2+ph-90), (px2+pw-10, py2+ph-90), 1)
        stats = [
            f"Level: {p.level}   XP: {p.xp}/{p.xp_next}",
            f"ATK: {p.effective_attack()}   DEF: {p.effective_defense()}   Gold: {p.gold}",
        ]
        for i, st in enumerate(stats):
            t = self.fonts[16].render(st, True, LGRAY)
            s.blit(t, (px2+20, py2+ph-84+i*22))

        hint = self.fonts[16].render("↑↓ Select  Enter: Use  ESC: Close", True, GRAY)
        s.blit(hint, (px2 + pw//2 - hint.get_width()//2, py2 + ph - 28))

    
    def draw_game_over(self):
        self._draw_overlay("GAME OVER", RED, "You have fallen in the dungeon.")

    def draw_win(self):
        self.screen.fill(BG_COLOR)
        self._draw_overlay("VICTORY!", GOLD,
                           f"You escaped the dungeon!  Gold: {self.player.gold}")

    def _draw_overlay(self, header, hcolor, sub):
        s   = self.screen
        dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        dim.fill((0,0,0,200))
        s.blit(dim, (0,0))
        h = self.fonts[48].render(header, True, hcolor)
        m = self.fonts[24].render(sub,    True, CREAM)
        r = self.fonts[20].render("Press R to restart", True, LGRAY)
        cx = SCREEN_W//2
        s.blit(h, (cx - h.get_width()//2, SCREEN_H//2 - 80))
        s.blit(m, (cx - m.get_width()//2, SCREEN_H//2))
        s.blit(r, (cx - r.get_width()//2, SCREEN_H//2 + 60))



if __name__ == "__main__":
    Game().run()