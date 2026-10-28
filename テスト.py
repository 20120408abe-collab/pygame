"""
どうぶつテトリス (Python + pygame)

実行方法:
    pip install pygame
    python tetris.py

画面の流れ:
    タイトル → スタート画面(ルール説明 → 3,2,1) → ゲーム(制限時間1分) → 結果・コンティニュー
    タイトル → チュートリアル(操作を1つずつ練習)

ゲーム中の操作:
    ← →      : 左右移動
    ↓        : ソフトドロップ
    ↑ / X    : 右回転
    Z        : 左回転
    Space    : ハードドロップ
    C        : ホールド
    P        : 一時停止
    Esc      : タイトルにもどる

日本語が文字化けする場合:
    日本語フォント(.ttf / .ttc / .otf)を「font.ttf」という名前で
    このファイルと同じフォルダに置いてください。
"""
import os
import random
import sys

import pygame

# ================= 設定 =================
CELL = 30                     # 1マスのピクセル数
COLS, ROWS = 10, 20           # 盤面サイズ
SIDE = 260                    # 右側パネルの幅
BOARD_W = COLS * CELL
WIDTH = BOARD_W + SIDE
HEIGHT = ROWS * CELL
FPS = 60

TIME_LIMIT_MS = 60 * 1000     # 制限時間 (1人1分)
CONTINUE_SEC = 10             # コンティニューの待ち時間 (秒)

BG = (18, 18, 28)
GRID = (40, 40, 55)
PANEL = (28, 28, 42)
TEXT = (235, 235, 235)
SUB = (150, 150, 175)
ACCENT = (255, 210, 90)
GOOD = (120, 230, 120)
WARN = (255, 90, 90)

# ミノごとの色 (動物に合わせた色)
COLORS = {
    "I": (90, 210, 240),    # うさぎ
    "O": (250, 220, 40),    # ひよこ
    "T": (170, 120, 230),   # ねこ
    "S": (90, 200, 80),     # かえる
    "Z": (250, 160, 190),   # ぶた
    "J": (170, 110, 60),    # くま
    "L": (240, 160, 70),    # いぬ
}
KINDS = list(COLORS.keys())

# ================= ドット絵 =================
# B=体の色  k=黒  w=白  p=ピンク  n=濃いピンク  o=オレンジ  m=薄い茶  .=背景
ANIMALS = {
    "T": [  # ねこ
        "..........",
        ".B......B.",
        ".BB....BB.",
        ".BBBBBBBB.",
        ".BkBBBBkB.",
        ".BBBBBBBB.",
        ".BBBppBBB.",
        ".BBkBBkBB.",
        "..BBBBBB..",
        "..........",
    ],
    "L": [  # いぬ
        "..........",
        ".kBBBBBBk.",
        "kkBBBBBBkk",
        "kkBkBBkBkk",
        "kkBBBBBBkk",
        ".kBBkkBBk.",
        "..BBkkBB..",
        "..BBppBB..",
        "...BBBB...",
        "..........",
    ],
    "I": [  # うさぎ
        "..B....B..",
        "..Bp..pB..",
        "..Bp..pB..",
        "..BB..BB..",
        ".BBBBBBBB.",
        ".BkBBBBkB.",
        ".BBBppBBB.",
        ".BBBkkBBB.",
        "..BBBBBB..",
        "..........",
    ],
    "J": [  # くま
        "..........",
        ".BBB..BBB.",
        ".BmBBBBmB.",
        "..BBBBBB..",
        ".BBkBBkBB.",
        ".BBBmmBBB.",
        ".BBmkkmBB.",
        ".BBBmmBBB.",
        "..BBBBBB..",
        "..........",
    ],
    "Z": [  # ぶた
        "..........",
        ".BB....BB.",
        ".BBBBBBBB.",
        ".BkBBBBkB.",
        ".BBBBBBBB.",
        ".BBnnnnBB.",
        ".BBnknkBB.",
        ".BBnnnnBB.",
        "..BBBBBB..",
        "..........",
    ],
    "S": [  # かえる
        "..........",
        ".www..www.",
        ".wkwBBwkw.",
        ".BBBBBBBB.",
        ".BBBBBBBB.",
        ".BkBBBBkB.",
        ".BBkkkkBB.",
        ".BBBBBBBB.",
        "..BBBBBB..",
        "..........",
    ],
    "O": [  # ひよこ
        "....B.....",
        "...BB.....",
        "..BBBBBB..",
        ".BBBBBBBB.",
        ".BkBBBBkB.",
        ".BBBooBBB.",
        ".BBBooBBB.",
        ".BBBBBBBB.",
        "..BBBBBB..",
        "..........",
    ],
}

# タイトル画面の大きな猫 (16x14)
BIG_CAT = [
    "..k..........k..",
    ".kBk........kBk.",
    ".kBBk......kBBk.",
    ".kBpBkkkkkkBpBk.",
    ".kBBBBBBBBBBBBk.",
    "kBBBBBBBBBBBBBBk",
    "kBBkkBBBBBBkkBBk",
    "kBBkwBBBBBBkwBBk",
    "kBBBBBBBBBBBBBBk",
    "kBpBBBBnnBBBBpBk",
    "kBBBBBkBBkBBBBBk",
    ".kBBBBBkkBBBBBk.",
    "..kkBBBBBBBBkk..",
    "....kkkkkkkk....",
]

PALETTE = {
    "k": (35, 30, 30),
    "w": (255, 255, 255),
    "p": (255, 150, 180),
    "n": (225, 95, 135),
    "o": (255, 130, 20),
    "m": (235, 205, 165),
}

# ================= ミノの形 =================
SHAPES = {
    "I": [(0, 1), (1, 1), (2, 1), (3, 1)],
    "O": [(1, 0), (2, 0), (1, 1), (2, 1)],
    "T": [(1, 0), (0, 1), (1, 1), (2, 1)],
    "S": [(1, 0), (2, 0), (0, 1), (1, 1)],
    "Z": [(0, 0), (1, 0), (1, 1), (2, 1)],
    "J": [(0, 0), (0, 1), (1, 1), (2, 1)],
    "L": [(2, 0), (0, 1), (1, 1), (2, 1)],
}
BOX = {"I": 4, "O": 4}  # それ以外は 3x3 の枠で回転
KICKS = [(0, 0), (-1, 0), (1, 0), (0, -1), (-2, 0), (2, 0)]  # 簡易ウォールキック
LINE_SCORES = [0, 100, 300, 500, 800]


# ================= 日本語フォント =================
FONT_FILES = [
    "font.ttf",  # 同じフォルダに置いたフォントを最優先
    "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/YuGothM.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]
FONT_NAMES = ["meiryo", "yugothic", "msgothic", "hiraginosans", "notosanscjkjp", "ipagothic"]


def find_jp_font():
    here = os.path.dirname(os.path.abspath(__file__))
    for path in FONT_FILES:
        full = path if path[0] in "/C" else os.path.join(here, path)
        if os.path.exists(full):
            return full
    for name in FONT_NAMES:
        path = pygame.font.match_font(name)
        if path:
            return path
    return None


def make_font(path, size):
    if path:
        return pygame.font.Font(path, size)
    return pygame.font.SysFont(None, size)


# ================= ミノ・ゲームロジック =================
class Piece:
    def __init__(self, kind):
        self.kind = kind
        self.cells = list(SHAPES[kind])
        self.x = COLS // 2 - 2
        self.y = 0

    def blocks(self, cells=None, x=None, y=None):
        cells = self.cells if cells is None else cells
        x = self.x if x is None else x
        y = self.y if y is None else y
        return [(x + cx, y + cy) for cx, cy in cells]

    def rotated(self, clockwise=True):
        if self.kind == "O":
            return list(self.cells)
        n = BOX.get(self.kind, 3)
        if clockwise:
            return [(n - 1 - cy, cx) for cx, cy in self.cells]
        return [(cy, n - 1 - cx) for cx, cy in self.cells]


class Bag:
    """7種を1セットずつシャッフルして出す"""

    def __init__(self):
        self.queue = []

    def _fill(self):
        if not self.queue:
            self.queue = KINDS[:]
            random.shuffle(self.queue)

    def next(self):
        self._fill()
        return self.queue.pop()

    def peek(self):
        self._fill()
        return self.queue[-1]


class Tetris:
    def __init__(self, time_limit=None, gravity_ms=None):
        self.time_limit = time_limit    # None なら時間無制限 (チュートリアル用)
        self.gravity_ms = gravity_ms    # None ならレベルに応じた速さ
        self.reset()

    def reset(self):
        self.board = [[None] * COLS for _ in range(ROWS)]
        self.bag = Bag()
        self.current = Piece(self.bag.next())
        self.hold = None
        self.can_hold = True
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.time_up = False
        self.paused = False
        self.fall_timer = 0
        self.time_left = self.time_limit
        # チュートリアルで「何をしたか」を数えるための記録
        self.stats = dict(left=0, right=0, cw=0, ccw=0, soft=0, hard=0, hold=0, locks=0)

    @property
    def finished(self):
        return self.game_over or self.time_up

    def clear_board(self):
        """スコアなどはそのままで盤面だけ空にする (チュートリアル用)"""
        self.board = [[None] * COLS for _ in range(ROWS)]
        self.current = Piece(self.bag.next())
        self.can_hold = True
        self.game_over = False
        self.fall_timer = 0

    # --- 判定 ---
    def valid(self, blocks):
        for x, y in blocks:
            if x < 0 or x >= COLS or y >= ROWS:
                return False
            if y >= 0 and self.board[y][x] is not None:
                return False
        return True

    def fall_interval(self):
        if self.gravity_ms is not None:
            return self.gravity_ms
        return max(60, 800 - (self.level - 1) * 70)

    # --- 操作 ---
    def move(self, dx, dy):
        p = self.current
        if self.valid(p.blocks(x=p.x + dx, y=p.y + dy)):
            p.x += dx
            p.y += dy
            return True
        return False

    def shift(self, dx):
        if self.move(dx, 0):
            self.stats["left" if dx < 0 else "right"] += 1

    def rotate(self, clockwise=True):
        p = self.current
        new_cells = p.rotated(clockwise)
        for kx, ky in KICKS:
            if self.valid(p.blocks(cells=new_cells, x=p.x + kx, y=p.y + ky)):
                p.cells = new_cells
                p.x += kx
                p.y += ky
                self.stats["cw" if clockwise else "ccw"] += 1
                return

    def soft_drop(self):
        self.stats["soft"] += 1
        if self.move(0, 1):
            self.score += 1
            self.fall_timer = 0
        else:
            self.lock()

    def hard_drop(self):
        self.stats["hard"] += 1
        dist = 0
        while self.move(0, 1):
            dist += 1
        self.score += dist * 2
        self.lock()

    def hold_piece(self):
        if not self.can_hold:
            return
        kind = self.current.kind
        self.current = Piece(self.bag.next() if self.hold is None else self.hold)
        self.hold = kind
        self.can_hold = False
        self.fall_timer = 0
        self.stats["hold"] += 1

    def ghost_y(self):
        p = self.current
        y = p.y
        while self.valid(p.blocks(y=y + 1)):
            y += 1
        return y

    # --- 固定・ライン消去 ---
    def lock(self):
        self.stats["locks"] += 1
        for x, y in self.current.blocks():
            if y < 0:
                self.game_over = True
                return
            self.board[y][x] = self.current.kind
        self.clear_lines()
        self.current = Piece(self.bag.next())
        self.can_hold = True
        self.fall_timer = 0
        if not self.valid(self.current.blocks()):
            self.game_over = True

    def clear_lines(self):
        remaining = [row for row in self.board if any(c is None for c in row)]
        cleared = ROWS - len(remaining)
        if cleared:
            self.board = [[None] * COLS for _ in range(cleared)] + remaining
            self.lines += cleared
            self.score += LINE_SCORES[cleared] * self.level
            self.level = self.lines // 10 + 1

    # --- 毎フレーム ---
    def update(self, dt):
        if self.finished or self.paused:
            return
        if self.time_left is not None:
            self.time_left -= dt
            if self.time_left <= 0:
                self.time_left = 0
                self.time_up = True
                return
        self.fall_timer += dt
        if self.fall_timer >= self.fall_interval():
            self.fall_timer = 0
            if not self.move(0, 1):
                self.lock()


def apply_game_key(game, key):
    """ゲーム中・チュートリアル中の共通キー操作"""
    if key == pygame.K_LEFT:
        game.shift(-1)
    elif key == pygame.K_RIGHT:
        game.shift(1)
    elif key == pygame.K_DOWN:
        game.soft_drop()
    elif key in (pygame.K_UP, pygame.K_x):
        game.rotate(clockwise=True)
    elif key == pygame.K_z:
        game.rotate(clockwise=False)
    elif key == pygame.K_SPACE:
        game.hard_drop()
    elif key == pygame.K_c:
        game.hold_piece()


# ================= 描画の部品 =================
_tile_cache = {}


def animal_tile(kind, size):
    """動物のドット絵ブロック (一度作ったら使い回す)"""
    key = (kind, size)
    if key not in _tile_cache:
        base = COLORS[kind]
        surf = pygame.Surface((size, size))
        surf.fill(tuple(int(c * 0.7) for c in base))
        draw_pixel_art(surf, ANIMALS[kind], {**PALETTE, "B": base}, 0, 0, size / 10)
        pygame.draw.rect(surf, tuple(int(c * 0.45) for c in base), surf.get_rect(), 1)
        _tile_cache[key] = surf
    return _tile_cache[key]


def draw_pixel_art(surf, art, palette, ox, oy, px):
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            x0, y0 = round(ox + c * px), round(oy + r * px)
            x1, y1 = round(ox + (c + 1) * px), round(oy + (r + 1) * px)
            surf.fill(palette[ch], (x0, y0, x1 - x0, y1 - y0))


def fmt_time(ms):
    s = max(0, (int(ms) + 999) // 1000)
    return f"{s // 60}:{s % 60:02d}"


def wrap_text(font, text, width):
    """日本語向け: 1文字ずつ詰めて折り返す"""
    lines = []
    for para in text.split("\n"):
        line = ""
        for ch in para:
            if line and font.size(line + ch)[0] > width:
                lines.append(line)
                line = ch
            else:
                line += ch
        lines.append(line)
    return lines


# ================= チュートリアルの内容 =================
TUTORIAL_STEPS = [
    {
        "title": "いどう",
        "text": "← → キーでブロックを左右に動かせるよ。\n\n左と右、両方に動かしてみよう！",
        "check": lambda d: d["left"] >= 1 and d["right"] >= 1,
    },
    {
        "title": "かいてん",
        "text": "↑ キー（または X）で右に回転、Z で左に回転するよ。\n\n両方ためしてみよう！",
        "check": lambda d: d["cw"] >= 1 and d["ccw"] >= 1,
    },
    {
        "title": "ソフトドロップ",
        "text": "↓ キーを押している間、ブロックが速く落ちるよ。\n\n↓ を5回押してみよう！",
        "check": lambda d: d["soft"] >= 5,
    },
    {
        "title": "ハードドロップ",
        "text": "SPACE キーで一気に下まで落とせるよ。\n\n点線の枠が「ここに落ちるよ」という目印。\nSPACE で落としてみよう！",
        "check": lambda d: d["hard"] >= 1,
    },
    {
        "title": "ホールド",
        "text": "C キーで今のブロックを右の HOLD にとっておけるよ。\nもう一度 C を押すと入れかえられるよ。\n\nC を押してみよう！",
        "check": lambda d: d["hold"] >= 1,
    },
    {
        "title": "ラインを消そう",
        "text": "横一列をすきまなくうめると、その列が消えて点数になるよ。\n\nうさぎブロックを、あいている所に SPACE で落とそう！",
        "check": lambda d: d["lines"] >= 1,
        "setup": "line",
    },
    {
        "title": "本番のルール",
        "text": "本番の制限時間は 1分！\n時間内にたくさんラインを消して高得点をめざそう。\n\n"
                "時間切れのあとはコンティニューで何度でも挑戦できるよ。\n"
                "P で一時停止、ESC でタイトルにもどれるよ。",
        "check": None,  # 最後のページ
    },
]


# ================= アプリ本体 (画面の切り替え) =================
class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("どうぶつテトリス")
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(170, 50)

        font_path = find_jp_font()
        self.f_small = make_font(font_path, 16)
        self.f = make_font(font_path, 20)
        self.f_mid = make_font(font_path, 28)
        self.f_big = make_font(font_path, 50)
        self.f_huge = make_font(font_path, 110)

        self.best = 0
        self.game = None
        self.rain = []          # タイトル画面で降ってくる動物
        self.rain_timer = 0
        self.go_title()

    # ---------- メインループ ----------
    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    getattr(self, "key_" + self.state)(event.key)
            getattr(self, "update_" + self.state)(dt)
            getattr(self, "draw_" + self.state)()
            pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()

    # ---------- 共通の描画 ----------
    def text(self, font, s, color, pos, center=False, shadow=False):
        if shadow:
            img = font.render(s, True, (0, 0, 0))
            r = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
            self.screen.blit(img, r.move(3, 3))
        img = font.render(s, True, color)
        r = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
        self.screen.blit(img, r)
        return r

    def dim(self, alpha=160, rect=None):
        rect = rect or pygame.Rect(0, 0, WIDTH, HEIGHT)
        overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, rect.topleft)

    def box(self, rect, border=ACCENT):
        pygame.draw.rect(self.screen, (30, 30, 48), rect, border_radius=12)
        pygame.draw.rect(self.screen, border, rect, 3, border_radius=12)

    def draw_board(self, game, show_piece=True):
        self.screen.fill(BG)
        for x in range(COLS + 1):
            pygame.draw.line(self.screen, GRID, (x * CELL, 0), (x * CELL, HEIGHT))
        for y in range(ROWS + 1):
            pygame.draw.line(self.screen, GRID, (0, y * CELL), (BOARD_W, y * CELL))
        for y, row in enumerate(game.board):
            for x, kind in enumerate(row):
                if kind:
                    self.screen.blit(animal_tile(kind, CELL), (x * CELL, y * CELL))
        if show_piece and not game.finished:
            p = game.current
            for x, y in p.blocks(y=game.ghost_y()):  # ゴースト
                if y >= 0:
                    rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL).inflate(-4, -4)
                    pygame.draw.rect(self.screen, COLORS[p.kind], rect, 2)
            for x, y in p.blocks():
                if y >= 0:
                    self.screen.blit(animal_tile(p.kind, CELL), (x * CELL, y * CELL))
        pygame.draw.rect(self.screen, PANEL, (BOARD_W, 0, SIDE, HEIGHT))

    def draw_mini(self, kind, ox, oy):
        if kind is None:
            return
        for cx, cy in SHAPES[kind]:
            self.screen.blit(animal_tile(kind, 20), (ox + cx * 20, oy + cy * 20))

    def draw_next_hold(self, y):
        px = BOARD_W + 20
        self.text(self.f, "NEXT", SUB, (px, y))
        self.draw_mini(self.game.bag.peek(), px, y + 28)
        self.text(self.f, "HOLD", SUB, (px + 120, y))
        self.draw_mini(self.game.hold, px + 120, y + 28)

    # ==================================================
    # タイトル画面
    # ==================================================
    MENU = ["ゲームスタート", "あそびかた（チュートリアル）", "おわる"]

    def go_title(self):
        self.state = "title"
        self.menu_index = 0

    def key_title(self, key):
        if key == pygame.K_UP:
            self.menu_index = (self.menu_index - 1) % len(self.MENU)
        elif key == pygame.K_DOWN:
            self.menu_index = (self.menu_index + 1) % len(self.MENU)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.menu_index == 0:
                self.go_ready()
            elif self.menu_index == 1:
                self.go_tutorial()
            else:
                self.quit()
        elif key == pygame.K_ESCAPE:
            self.quit()

    def update_title(self, dt):
        self.rain_timer += dt
        if self.rain_timer > 300:
            self.rain_timer = 0
            self.rain.append([random.randrange(0, WIDTH - CELL), -CELL,
                              random.choice(KINDS), random.uniform(40, 100)])
        for r in self.rain:
            r[1] += r[3] * dt / 1000
        self.rain = [r for r in self.rain if r[1] < HEIGHT]

    def draw_title(self):
        self.screen.fill(BG)
        for x, y, kind, _ in self.rain:
            self.screen.blit(animal_tile(kind, CELL), (x, int(y)))
        self.dim(150)

        cx = WIDTH // 2
        self.text(self.f_big, "どうぶつテトリス", ACCENT, (cx, 70), center=True, shadow=True)
        self.text(self.f, "ANIMAL TETRIS", SUB, (cx, 118), center=True)

        # 真ん中の大きな猫
        px = 9
        draw_pixel_art(self.screen, BIG_CAT, {**PALETTE, "B": (250, 190, 120)},
                       cx - 8 * px, 150, px)
        # 動物の顔を並べる
        for i, kind in enumerate(KINDS):
            self.screen.blit(animal_tile(kind, CELL), (cx - 7 * 36 // 2 + i * 36 + 3, 290))

        for i, label in enumerate(self.MENU):
            y = 375 + i * 50
            if i == self.menu_index:
                rect = pygame.Rect(0, 0, 380, 42)
                rect.center = (cx, y)
                pygame.draw.rect(self.screen, (60, 55, 30), rect, border_radius=10)
                pygame.draw.rect(self.screen, ACCENT, rect, 2, border_radius=10)
                self.text(self.f_mid, label, ACCENT, (cx, y), center=True)
            else:
                self.text(self.f_mid, label, SUB, (cx, y), center=True)

        if self.best:
            self.text(self.f, f"ハイスコア  {self.best}", TEXT, (cx, 535), center=True)
        self.text(self.f_small, "↑↓ でえらぶ ／ ENTER で決定", SUB, (cx, 570), center=True)

    # ==================================================
    # スタート画面 (ルール説明 → 3,2,1 カウントダウン)
    # ==================================================
    def go_ready(self, skip_info=False):
        self.state = "ready"
        self.game = Tetris(time_limit=TIME_LIMIT_MS)
        self.ready_phase = "count" if skip_info else "info"
        self.count_ms = 3000

    def key_ready(self, key):
        if key == pygame.K_ESCAPE:
            self.go_title()
        elif self.ready_phase == "info" and key in (pygame.K_SPACE, pygame.K_RETURN):
            self.ready_phase = "count"

    def update_ready(self, dt):
        if self.ready_phase == "count":
            self.count_ms -= dt
            if self.count_ms <= -700:  # 「スタート！」を少し見せてから開始
                self.state = "play"

    def draw_ready(self):
        self.draw_board(self.game, show_piece=False)
        self.draw_side_play()
        self.dim(170)
        cx, cy = WIDTH // 2, HEIGHT // 2
        if self.ready_phase == "info":
            self.box(pygame.Rect(cx - 220, cy - 190, 440, 380))
            self.text(self.f_big, "スタート", ACCENT, (cx, cy - 140), center=True)
            lines = [
                ("制限時間", "1分"),
                ("目標", "ラインを消そう"),
                ("1列", f"{LINE_SCORES[1]}点"),
                ("4列同時", f"{LINE_SCORES[4]}点！"),
            ]
            for i, (a, b) in enumerate(lines):
                y = cy - 70 + i * 42
                self.text(self.f_mid, a, SUB, (cx - 170, y - 16))
                self.text(self.f_mid, b, TEXT, (cx - 30, y - 16))
            self.text(self.f_mid, "SPACE でスタート", ACCENT, (cx, cy + 125), center=True)
            self.text(self.f_small, "ESC でタイトルにもどる", SUB, (cx, cy + 160), center=True)
        else:
            if self.count_ms > 0:
                n = str(int(self.count_ms // 1000) + 1)
                self.text(self.f_huge, n, ACCENT, (cx, cy), center=True, shadow=True)
            else:
                self.text(self.f_big, "スタート！", GOOD, (cx, cy), center=True, shadow=True)

    # ==================================================
    # ゲーム本番
    # ==================================================
    def key_play(self, key):
        g = self.game
        if key == pygame.K_ESCAPE:
            self.go_title()
        elif key == pygame.K_p:
            g.paused = not g.paused
        elif not g.paused:
            apply_game_key(g, key)

    def update_play(self, dt):
        self.game.update(dt)
        if self.game.finished:
            self.new_record = self.game.score > self.best
            self.best = max(self.best, self.game.score)
            self.go_result()

    def draw_side_play(self):
        g = self.game
        px = BOARD_W + 20
        # 残り時間 (10秒を切ると赤く点滅)
        t = g.time_left
        color = TEXT
        if t <= 10000 and (t // 250) % 2 == 0:
            color = WARN
        self.text(self.f, "のこり時間", SUB, (px, 12))
        self.text(self.f_big, fmt_time(t), color, (px, 34))
        bar = pygame.Rect(px, 98, SIDE - 40, 10)
        pygame.draw.rect(self.screen, GRID, bar, border_radius=5)
        fill = bar.copy()
        fill.width = int(bar.width * t / TIME_LIMIT_MS)
        pygame.draw.rect(self.screen, WARN if t <= 10000 else GOOD, fill, border_radius=5)

        self.draw_next_hold(125)

        rows = [("スコア", g.score), ("ライン", g.lines), ("レベル", g.level), ("ハイスコア", self.best)]
        for i, (label, val) in enumerate(rows):
            y = 235 + i * 34
            self.text(self.f, label, SUB, (px, y))
            self.text(self.f_mid, str(val), TEXT, (px + 105, y - 6))

        helps = ["← → ：いどう", "↓ ：ソフトドロップ", "↑ / X ・ Z ：かいてん",
                 "SPACE ：ハードドロップ", "C ：ホールド", "P ：一時停止", "ESC ：タイトルへ"]
        for i, s in enumerate(helps):
            self.text(self.f_small, s, SUB, (px, 400 + i * 26))

    def draw_play(self):
        self.draw_board(self.game)
        self.draw_side_play()
        if self.game.paused:
            self.dim(160, pygame.Rect(0, 0, BOARD_W, HEIGHT))
            self.text(self.f_big, "一時停止", TEXT, (BOARD_W // 2, HEIGHT // 2 - 20), center=True)
            self.text(self.f, "P でさいかい", SUB, (BOARD_W // 2, HEIGHT // 2 + 30), center=True)

    # ==================================================
    # 結果・コンティニュー
    # ==================================================
    def go_result(self):
        self.state = "result"
        self.result_ms = 0          # 結果画面に入ってからの時間
        self.continue_ms = CONTINUE_SEC * 1000

    def key_result(self, key):
        if self.result_ms < 800:    # 連打で一瞬で飛ばさないように少し待つ
            return
        if key in (pygame.K_SPACE, pygame.K_RETURN):
            self.go_ready(skip_info=True)
        elif key == pygame.K_ESCAPE:
            self.go_title()

    def update_result(self, dt):
        self.result_ms += dt
        self.continue_ms -= dt
        if self.continue_ms <= 0:
            self.go_title()

    def draw_result(self):
        g = self.game
        self.draw_board(g, show_piece=False)
        self.draw_side_play()
        self.dim(180)
        cx, cy = WIDTH // 2, HEIGHT // 2
        self.box(pygame.Rect(cx - 210, cy - 230, 420, 460))

        title = "タイムアップ！" if g.time_up else "ゲームオーバー"
        self.text(self.f_big, title, ACCENT, (cx, cy - 185), center=True)
        self.text(self.f_mid, f"スコア  {g.score}", TEXT, (cx, cy - 115), center=True)
        self.text(self.f, f"消したライン  {g.lines}", TEXT, (cx, cy - 78), center=True)
        if self.new_record and g.score > 0:
            self.text(self.f_mid, "★ ハイスコア更新！ ★", GOOD, (cx, cy - 38), center=True)
        else:
            self.text(self.f, f"ハイスコア  {self.best}", SUB, (cx, cy - 38), center=True)

        self.text(self.f_mid, "コンティニュー？", TEXT, (cx, cy + 15), center=True)
        sec = int(self.continue_ms // 1000) + 1
        self.text(self.f_huge, str(min(sec, CONTINUE_SEC)), ACCENT, (cx, cy + 95), center=True)
        self.text(self.f, "SPACE ：もう一度挑戦（1分）", GOOD, (cx, cy + 165), center=True)
        self.text(self.f, "ESC ：タイトルにもどる", SUB, (cx, cy + 197), center=True)

    # ==================================================
    # チュートリアル
    # ==================================================
    def go_tutorial(self):
        self.state = "tutorial"
        self.game = Tetris(time_limit=None, gravity_ms=1200)  # ゆっくり落ちる
        self.step = 0
        self.step_done_ms = 0       # 「できた！」表示の残り時間
        self.start_step()

    def snapshot(self):
        return dict(self.game.stats, lines=self.game.lines)

    def start_step(self):
        self.step_base = self.snapshot()
        if TUTORIAL_STEPS[self.step].get("setup") == "line":
            self.setup_line_practice()

    def setup_line_practice(self):
        """一番下の列に4マスのすきまを作り、うさぎ(I)ブロックを出す"""
        g = self.game
        g.clear_board()
        g.board[ROWS - 1] = [None if 3 <= x <= 6 else random.choice(KINDS) for x in range(COLS)]
        g.current = Piece("I")
        self.line_locks = g.stats["locks"]

    def key_tutorial(self, key):
        last = self.step == len(TUTORIAL_STEPS) - 1
        if key == pygame.K_ESCAPE:
            self.go_title()
        elif last and key in (pygame.K_SPACE, pygame.K_RETURN):
            self.go_ready()
        elif key == pygame.K_RETURN:          # とばす
            self.next_step()
        elif not last:
            apply_game_key(self.game, key)

    def next_step(self):
        self.step = min(self.step + 1, len(TUTORIAL_STEPS) - 1)
        self.step_done_ms = 0
        self.start_step()

    def update_tutorial(self, dt):
        g = self.game
        step = TUTORIAL_STEPS[self.step]
        if step["check"] is None:
            return
        g.update(dt)
        if g.game_over:               # チュートリアルでは積み上がったら盤面をリセット
            g.clear_board()

        if self.step_done_ms > 0:
            self.step_done_ms -= dt
            if self.step_done_ms <= 0:
                self.next_step()
            return

        now = self.snapshot()
        delta = {k: now[k] - self.step_base[k] for k in now}
        if step["check"](delta):
            self.step_done_ms = 1000
        elif step.get("setup") == "line" and g.stats["locks"] > self.line_locks:
            self.setup_line_practice()  # 消せなかったらやり直し

    def draw_tutorial(self):
        g = self.game
        step = TUTORIAL_STEPS[self.step]
        last = step["check"] is None
        self.draw_board(g, show_piece=not last)
        px = BOARD_W + 20

        self.text(self.f, f"チュートリアル  {self.step + 1} / {len(TUTORIAL_STEPS)}", SUB, (px, 12))
        # 進み具合のバー
        for i in range(len(TUTORIAL_STEPS)):
            color = ACCENT if i <= self.step else GRID
            pygame.draw.rect(self.screen, color, (px + i * 31, 42, 26, 6), border_radius=3)

        if not last:
            self.draw_next_hold(62)

        top = 62 if last else 160
        self.text(self.f_mid, step["title"], ACCENT, (px, top))
        for i, line in enumerate(wrap_text(self.f, step["text"], SIDE - 40)):
            self.text(self.f, line, TEXT, (px, top + 45 + i * 28))

        if last:
            self.text(self.f, "SPACE ：ゲームスタート", GOOD, (px, HEIGHT - 80))
            self.text(self.f, "ESC ：タイトルへ", SUB, (px, HEIGHT - 50))
            # 盤面側にはまとめの絵
            self.dim(120, pygame.Rect(0, 0, BOARD_W, HEIGHT))
            draw_pixel_art(self.screen, BIG_CAT, {**PALETTE, "B": (250, 190, 120)},
                           BOARD_W // 2 - 8 * 10, 170, 10)
            self.text(self.f_big, "がんばって！", ACCENT, (BOARD_W // 2, 360), center=True, shadow=True)
        else:
            self.text(self.f_small, "ENTER ：この説明をとばす", SUB, (px, HEIGHT - 52))
            self.text(self.f_small, "ESC ：タイトルへ", SUB, (px, HEIGHT - 28))

        if self.step_done_ms > 0:
            self.text(self.f_big, "できた！", GOOD, (BOARD_W // 2, HEIGHT // 2), center=True, shadow=True)


if __name__ == "__main__":
    App().run()