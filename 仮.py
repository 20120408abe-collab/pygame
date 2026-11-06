"""
Animal Block Remove (Python + pygame)

実行方法:
    pip install pygame
    python tetris.py

画面の流れ:
    タイトル → スタート画面(ルール説明 → 3,2,1) → ゲーム(制限時間2分) → 結果・コンティニュー
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

レベル (ゲームスタートのあとにえらぶ):
    レベル1 かんたん   : いつものルール
    レベル2 ふつう     : ばくだんが落ちてくる (動かしているブロックにあたると減点)
    レベル3 むずかしい : ばくだんがレベル2よりたくさん落ちてくる
    ばくだんは積み終わったブロックや床に落ちても何も起きません。
    ハイスコアはレベルごとに記録されます。
    爆弾の数や減点は DIFFICULTY と BOMB_PENALTY で変えられます。

とくしゅアイテム (ゲーム中に上から落ちてくるキャラクター):
    いま動かしているブロックでキャッチすると効果が出ます。
    積み終わったブロックや床に落ちたら、効果なしで消えます。
        グレー : スコア +500
        赤     : のこり時間 +5秒
        黄色   : のこり時間 +10秒
        青     : のこり時間 +20秒
        虹色   : ボーナスタイム 1分 (その間のこり時間がへらない)
    キャラクターの絵・効果音・BGM はすべてこのプログラムの中で作っているので、
    著作権の心配はありません。

画像を使う場合 (なくても動きます):
    このファイルと同じ場所に「assets」フォルダを作り、次の名前で画像を入れてください。
    見つからない画像は、今までどおりドット絵で表示されます。

        assets/rabbit.png     うさぎ (I)
        assets/chick.png      ひよこ (O)
        assets/cat.png        ねこ   (T)
        assets/frog.png       かえる (S)
        assets/pig.png        ぶた   (Z)
        assets/bear.png       くま   (J)
        assets/dog.png        いぬ   (L)
        assets/title_bg.png   タイトル画面の背景
        assets/title_cat.png  タイトル画面・チュートリアル最後の大きな絵

    ブロックは 30×30 ピクセルに縮小されるので、
    背景が透明で輪郭のはっきりした PNG がおすすめです。
    フリー素材は各サイトの利用規約(クレジット表記・商用利用など)を確認してください。

日本語が文字化けする場合:
    日本語フォント(.ttf / .ttc / .otf)を「font.ttf」という名前で
    このファイルと同じフォルダに置いてください。
"""
import math
import os
import random
import sys
from array import array

import pygame

# ================= 設定 =================
CELL = 30                     # 1マスのピクセル数
COLS, ROWS = 10, 20           # 盤面サイズ
SIDE = 260                    # 右側パネルの幅
BOARD_W = COLS * CELL
WIDTH = BOARD_W + SIDE
HEIGHT = ROWS * CELL
FPS = 60

TIME_LIMIT_MS = 120 * 1000    # 制限時間 (1人2分)

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

# ================= 画像ファイル =================
ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
IMAGE_FILES = {
    "I": "rabbit.png",
    "O": "chick.png",
    "T": "cat.png",
    "S": "frog.png",
    "Z": "pig.png",
    "J": "bear.png",
    "L": "dog.png",
}
TITLE_BG_FILE = "title_bg.png"
TITLE_CAT_FILE = "title_cat.png"

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
    "s": (255, 240, 150),   # アイテムキャラの頭の星
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
CROSS_SCORE = 1000      # 同じ動物が十字 (＋の形) にそろったときの点数

# ================= とくしゅアイテム (落ちてくるキャラクター) =================
ITEM_SCORE = 500                    # グレー: スコアボーナスの点数
BONUS_MS = 60 * 1000                # 虹色: ボーナスタイム (のこり時間がへらない) の長さ
ITEM_FIRST_MS = 8000                # ゲーム開始から最初のアイテムまで
ITEM_INTERVAL_MS = (10000, 18000)   # つぎのアイテムまでの間隔 (この間でランダム)
ITEM_SPEED = 70                     # 落ちる速さ (ピクセル/秒)
ITEM_PX = 3                         # キャラのドット1つの大きさ

# weight は出やすさ (大きいほどよく出る)
ITEM_TYPES = {
    "gray":    {"color": (165, 165, 175), "weight": 35, "label": f"+{ITEM_SCORE}",
                "title": f"スコア +{ITEM_SCORE}", "sub": "点数がふえる"},
    "red":     {"color": (235, 70, 70), "weight": 25, "sec": 5, "label": "+5秒",
                "title": "時間 +5秒", "sub": "のこり時間がふえる"},
    "yellow":  {"color": (245, 210, 40), "weight": 18, "sec": 10, "label": "+10秒",
                "title": "時間 +10秒", "sub": "のこり時間がふえる"},
    "blue":    {"color": (70, 130, 245), "weight": 12, "sec": 20, "label": "+20秒",
                "title": "時間 +20秒", "sub": "のこり時間がふえる"},
    "rainbow": {"color": None, "weight": 10, "label": "ボーナス",          # None = 虹色
                "title": "ボーナスタイム", "sub": "1分間 時間がへらない！"},
}

# このゲームのオリジナルキャラクター (頭に星のついたまんまるな子)
# アイテムとして落ちてくるほか、盤面の後ろにシルエットで大きく表示する
ITEM_ART = [
    ".....ss.....",
    "....ssss....",
    ".....BB.....",
    "...BBBBBB...",
    "..BBBBBBBB..",
    ".BBwkBBwkBB.",
    ".BBkkBBkkBB.",
    ".BBBBBBBBBB.",
    ".BpBBkkBBpB.",
    "..BBBBBBBB..",
    "..BB....BB..",
    "............",
]

# ================= 難易度 (レベル1〜3) =================
BOMB_PENALTY = 300      # 爆弾が動かしているブロックにあたったときに減る点数

# bomb_first: ゲーム開始から最初の爆弾まで (ミリ秒)
# bomb_interval: つぎの爆弾までの間隔 (この間でランダム)
# bomb_max: 同時に落ちてくる爆弾の数の上限 (0 なら爆弾なし)
DIFFICULTY = {
    1: {"name": "かんたん", "color": (120, 230, 120), "desc": "いつものルール",
        "bomb_max": 0},
    2: {"name": "ふつう", "color": (255, 210, 90), "desc": "ばくだんが落ちてくる！",
        "bomb_max": 1, "bomb_first": 6000, "bomb_interval": (3000, 6000)},
    3: {"name": "むずかしい", "color": (255, 90, 90), "desc": "ばくだんがたくさん！",
        "bomb_max": 3, "bomb_first": 3000, "bomb_interval": (1500, 3500)},
}

# 爆弾のドット絵 (どこにでもある丸い爆弾の形。f=導火線  s=火花)
BOMB_ART = [
    ".........s..",
    "........fs..",
    ".......f....",
    ".....gg.....",
    "...kkkkkk...",
    "..kkkkkkkk..",
    ".kkwwkkkkkk.",
    ".kwwkkkkkkk.",
    ".kkkkkkkkkk.",
    ".kkkkkkkkkk.",
    "..kkkkkkkk..",
    "...kkkkkk...",
]


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
        # ブロック1つ1つの番号 (同じ十字で何度も点が入らないように使う)
        self.ids = [[None] * COLS for _ in range(ROWS)]
        self.next_id = 0
        self.scored_crosses = set()     # もう点数を入れた十字
        self.crosses = 0                # 十字をそろえた回数
        self.events = []                # 画面に知らせること (十字がそろった など)
        self.bag = Bag()
        self.current = Piece(self.bag.next())
        self.hold = None
        self.can_hold = True
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.topped_out = False         # 一番上まで積み上がった (くずれるエフェクトの合図)
        self.bonus_ms = 0               # ボーナスタイムののこり (0 ならボーナスなし)
        self.time_up = False
        self.paused = False
        self.fall_timer = 0
        self.time_left = self.time_limit
        # 動かしているブロックが下に動いて通ったマス。
        # ハードドロップで一気に落としても、とちゅうのアイテムや爆弾にあたるようにするため
        self.trail = []
        # チュートリアルで「何をしたか」を数えるための記録
        self.stats = dict(left=0, right=0, cw=0, ccw=0, soft=0, hard=0, hold=0, locks=0)

    @property
    def finished(self):
        return self.game_over or self.time_up

    def clear_board(self):
        """スコア・ライン・時間はそのままで盤面だけ空にする"""
        self.board = [[None] * COLS for _ in range(ROWS)]
        self.ids = [[None] * COLS for _ in range(ROWS)]
        self.current = Piece(self.bag.next())
        self.can_hold = True
        self.game_over = False
        self.topped_out = False
        self.fall_timer = 0
        self.trail = []

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
            if dy > 0:
                self.trail.extend(p.blocks())
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
        if self.move(0, 1):         # ソフトドロップでは点数は増えない
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
        # 出てきたブロックが積んであるブロックと重なったら、積み上がったのと同じあつかい
        # (前はそのまま重なって、ブロックが上書きされることがあった)
        if not self.valid(self.current.blocks()):
            self.topped_out = True

    def ghost_y(self):
        p = self.current
        y = p.y
        while self.valid(p.blocks(y=y + 1)):
            y += 1
        return y

    # --- 固定・ライン消去 ---
    def lock(self):
        self.stats["locks"] += 1
        # 一番上まで積み上がってもゲームオーバーにはせず、topped_out で知らせる
        for x, y in self.current.blocks():
            if y < 0:
                self.topped_out = True
                return
            self.board[y][x] = self.current.kind
            self.ids[y][x] = self.new_id()
        self.clear_lines()
        self.check_crosses()
        self.current = Piece(self.bag.next())
        self.can_hold = True
        self.fall_timer = 0
        if not self.valid(self.current.blocks()):
            self.topped_out = True

    def new_id(self):
        self.next_id += 1
        return self.next_id

    def clear_lines(self):
        keep = [y for y, row in enumerate(self.board) if any(c is None for c in row)]
        cleared = ROWS - len(keep)
        if cleared:
            empty = lambda: [[None] * COLS for _ in range(cleared)]
            self.board = empty() + [self.board[y] for y in keep]
            self.ids = empty() + [self.ids[y] for y in keep]
            self.lines += cleared
            self.score += LINE_SCORES[cleared] * self.level
            self.level = self.lines // 10 + 1

    def check_crosses(self):
        """同じ動物が ＋ の形 (まん中と上下左右の5つ) にそろっていたら点数を入れる。
        ブロックは消えずに残るが、同じ5つのブロックの十字で点が入るのは1回だけ"""
        for y in range(1, ROWS - 1):
            for x in range(1, COLS - 1):
                kind = self.board[y][x]
                if kind is None:
                    continue
                cells = [(x, y), (x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]
                if any(self.board[cy][cx] != kind for cx, cy in cells):
                    continue
                key = frozenset(self.ids[cy][cx] for cx, cy in cells)
                if key in self.scored_crosses:
                    continue
                self.scored_crosses.add(key)
                self.crosses += 1
                self.score += CROSS_SCORE
                self.events.append({"type": "cross", "cells": cells, "kind": kind})

    # --- 毎フレーム ---
    def update(self, dt):
        if self.finished or self.paused or self.topped_out:
            return
        if self.time_left is not None:
            if self.bonus_ms > 0:           # ボーナスタイム中はのこり時間がへらない
                self.bonus_ms = max(0, self.bonus_ms - dt)
            else:
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
    if game.topped_out:
        return
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


# ================= 落ちてくるアイテム =================
class Items:
    """上から落ちてくるもの (とくしゅアイテムや爆弾) の管理"""

    def __init__(self, first_ms=ITEM_FIRST_MS, interval=ITEM_INTERVAL_MS, choices=None,
                 weights=None, max_falling=1):
        self.falling = []
        self.timer = first_ms
        self.interval = interval
        # choices: チュートリアル用。このリストの中から同じ確率で出す (空なら出さない)
        self.choices = choices
        # weights: {しゅるい: 出やすさ}。指定がなければとくしゅアイテム
        self.weights = weights or {k: v["weight"] for k, v in ITEM_TYPES.items()}
        self.max_falling = max_falling      # 同時に落ちてくる数の上限

    def pick(self):
        if self.choices is not None:
            return random.choice(self.choices) if self.choices else None
        kinds = list(self.weights)
        return random.choices(kinds, [self.weights[k] for k in kinds])[0]

    def update(self, dt, game, others=()):
        """落ちてくるものを動かし、起きたこと (出てきた・あたった) のリストを返す。
        others: ほかの Items (同じ列に重ならないようにするため)"""
        events = []
        if len(self.falling) < self.max_falling:
            self.timer -= dt
            kind = self.pick() if self.timer <= 0 else None
            if kind:
                self.timer = random.randint(*self.interval)
                # いま動かしているブロックの真上には出さない (出たとたんにあたらないように)。
                # ほかに落ちているものと同じ列にも出さない
                busy = {x for x, y in game.current.blocks()}
                for group in (self, *others):
                    busy |= {it["col"] for it in group.falling}
                cols = [c for c in range(COLS) if c not in busy] or list(range(COLS))
                self.falling.append({"kind": kind, "col": random.choice(cols),
                                     "y": float(-CELL)})
                events.append({"type": "appear", "kind": kind})
        for it in list(self.falling):
            it["y"] += ITEM_SPEED * dt / 1000
            touched = self.touch(it, game)
            if touched:
                self.falling.remove(it)
                events.append({"type": touched, "kind": it["kind"],
                               "x": it["col"] * CELL + CELL / 2, "y": it["y"] + CELL / 2})
        return events

    @staticmethod
    def touch(it, game):
        """動かしているブロックにあたったら "hit" (効果あり)。
        積み終わったブロックや床に落ちたら "land" (効果なしで消える)。まだなら None"""
        col, top = it["col"], it["y"]
        rect = pygame.Rect(col * CELL, int(top), CELL, CELL)
        # 落ちているブロック (プレイヤーが動かしているブロック) だけが効果あり。
        # trail は、ハードドロップなどでこの一瞬に通りすぎたマス
        for x, y in set(game.current.blocks()) | set(game.trail):
            if pygame.Rect(x * CELL, y * CELL, CELL, CELL).colliderect(rect):
                return "hit"
        # 積み終わったブロック・床: 効果なし
        bottom = top + CELL
        if bottom >= HEIGHT:
            return "land"
        row = int(bottom // CELL)
        if row >= 0 and game.board[row][col] is not None:
            return "land"
        return None


# ================= 効果音・BGM =================
NOTE_INDEX = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
              "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def note_freq(name):
    """"C5" のような音の名前を周波数にする (None は休み)"""
    if not name:
        return 0
    midi = 12 * (int(name[-1]) + 1) + NOTE_INDEX[name[:-1]]
    return 440 * 2 ** ((midi - 69) / 12)


class SoundBox:
    """効果音と BGM をプログラムで作って鳴らす。
    録音した音やほかの曲は使わず、波の形から作っているので著作権の心配はない。
    音が出せないパソコンでは何もしない (ゲームはそのまま遊べる)"""

    def __init__(self):
        self.ok = False
        self.sounds = {}
        self.bgm = None
        self.bgm_channel = None
        try:
            init = pygame.mixer.get_init()
            if not init:
                return
            self.rate, _, self.channels = init
            self._build()
            self.ok = True
        except Exception as e:
            print(f"音を出せません: {e}")

    def _wave(self, notes, shape, vol):
        """[(音の名前, ミリ秒), ...] から波形 (数のリスト) を作る"""
        r = self.rate
        out = []
        for name, ms in notes:
            n = int(r * ms / 1000)
            f = note_freq(name)
            if not f:
                out.extend([0.0] * n)
                continue
            attack = max(1, int(r * 0.004))
            release = max(1, int(n * 0.3))
            for i in range(n):
                ph = (f * i / r) % 1.0
                if shape == "square":           # ピコピコした音
                    v = 1.0 if ph < 0.25 else -0.6
                else:                           # 三角波: やわらかい音
                    v = 4 * abs(ph - 0.5) - 1
                env = min(1.0, i / attack, (n - i) / release)
                out.append(v * env * vol)
        return out

    def _noise(self, ms, vol):
        """ザーッという音 (ランダムな波) をだんだん小さくする。爆発の音に使う"""
        n = int(self.rate * ms / 1000)
        out, last = [], 0.0
        for i in range(n):
            last = last * 0.75 + random.uniform(-1, 1) * 0.25    # 高い音をけずって低く太い音に
            out.append(last * vol * (1 - i / n) ** 2 * 2.5)
        return out

    def _make(self, *voices):
        """いくつかの波形を重ねて pygame の Sound にする"""
        n = max(len(v) for v in voices)
        data = array("h")
        for i in range(n):
            s = sum(v[i] for v in voices if i < len(v))
            val = int(max(-1.0, min(1.0, s)) * 32000)
            data.extend([val] * self.channels)
        return pygame.mixer.Sound(buffer=data.tobytes())

    def _build(self):
        sq, tri = "square", "triangle"
        w = self._wave
        self.sounds["appear"] = self._make(w([("E6", 50), ("B6", 90)], sq, 0.10))
        self.sounds["score"] = self._make(
            w([("C6", 60), ("E6", 60), ("G6", 60), ("C7", 180)], sq, 0.22))
        self.sounds["time"] = self._make(
            w([("G5", 50), ("C6", 50), ("E6", 50), ("G6", 50), ("C7", 50), ("E7", 200)], tri, 0.5))
        self.sounds["rainbow"] = self._make(
            w([("C5", 80), ("E5", 80), ("G5", 80), ("C6", 80), ("E6", 80), ("G6", 80), ("C7", 420)],
              sq, 0.18),
            w([("C4", 480), ("C5", 420)], tri, 0.35))
        self.sounds["bonus_end"] = self._make(w([("G5", 100), ("E5", 100), ("C5", 280)], sq, 0.18))
        # 爆弾: 出てきたときの「ブッブー」という注意の音と、ドカーンという爆発の音
        self.sounds["bomb_appear"] = self._make(w([("A3", 90), (None, 40), ("A3", 90)], sq, 0.16))
        self.sounds["bomb"] = self._make(self._noise(650, 0.9), w([("C3", 120), ("G2", 260)], tri, 0.5))

        # ボーナスタイムの BGM (このゲームのために作ったオリジナルのメロディ。くり返し鳴らす)
        eighth = 150
        melody = ("C5 E5 G5 E5 A5 G5 E5 G5  F5 A5 C6 A5 G5 E5 D5 E5  "
                  "C5 E5 G5 C6 B5 G5 A5 B5  C6 G5 E5 G5 C6 - C6 -")
        bass = "C3 C3 G2 G2  F2 F2 G2 G2  C3 C3 E3 E3  F2 G2 C3 C3"
        lead = [(None if n == "-" else n, eighth) for n in melody.split()]
        low = [(n, eighth * 2) for n in bass.split()]
        self.bgm = self._make(w(lead, sq, 0.12), w(low, tri, 0.25))

    def play(self, name):
        if self.ok:
            self.sounds[name].play()

    def start_bgm(self):
        if self.ok and self.bgm_channel is None:
            self.bgm_channel = self.bgm.play(loops=-1)

    def stop_bgm(self):
        if self.ok:
            self.bgm.stop()
        self.bgm_channel = None

    def pause_bgm(self, paused):
        if self.ok and self.bgm_channel is not None:
            if paused:
                self.bgm_channel.pause()
            else:
                self.bgm_channel.unpause()


# ================= 画像の読み込み =================
_image_cache = {}
_scaled_cache = {}


def load_image(name):
    """assets フォルダの画像を読み込む。見つからなければ None (一度読んだら使い回す)"""
    if name not in _image_cache:
        path = os.path.join(ASSET_DIR, name)
        img = None
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
            except pygame.error as e:
                print(f"画像を読み込めませんでした: {path} ({e})")
        _image_cache[name] = img
    return _image_cache[name]


def scaled_image(name, size):
    """画像を指定サイズに縮小したもの (なければ None)"""
    key = (name, size)
    if key not in _scaled_cache:
        img = load_image(name)
        _scaled_cache[key] = pygame.transform.smoothscale(img, size) if img else None
    return _scaled_cache[key]


def fit_image(name, max_w, max_h):
    """縦横比を保ったまま枠に収まるように縮小 (なければ None)"""
    img = load_image(name)
    if img is None:
        return None
    w, h = img.get_size()
    scale = min(max_w / w, max_h / h)
    return scaled_image(name, (max(1, int(w * scale)), max(1, int(h * scale))))


# ================= 描画の部品 =================
_tile_cache = {}


def animal_tile(kind, size):
    """動物のブロック。画像があれば画像、なければドット絵 (一度作ったら使い回す)"""
    key = (kind, size)
    if key not in _tile_cache:
        base = COLORS[kind]
        surf = pygame.Surface((size, size))
        surf.fill(tuple(int(c * 0.7) for c in base))
        img = scaled_image(IMAGE_FILES[kind], (size, size))
        if img:
            surf.blit(img, (0, 0))
        else:
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


def draw_big_cat(surf, cx, top, px):
    """大きな猫を描く。title_cat.png があればそれを、なければドット絵を使う"""
    w, h = 16 * px, 14 * px
    img = fit_image(TITLE_CAT_FILE, w, h)
    if img:
        surf.blit(img, img.get_rect(midtop=(cx, top)))
    else:
        draw_pixel_art(surf, BIG_CAT, {**PALETTE, "B": (250, 190, 120)}, cx - 8 * px, top, px)


def rainbow_color(t_ms, offset=0, sat=85, val=100):
    """時間とともに色が変わる虹色"""
    c = pygame.Color(0, 0, 0)
    c.hsva = ((t_ms * 0.3 + offset) % 360, sat, val, 100)
    return (c.r, c.g, c.b)


def draw_item(surf, kind, cx, top, px, t_ms=0):
    """アイテムのキャラクターを描く (cx は横のまん中、top は上の端)"""
    left = cx - len(ITEM_ART[0]) * px / 2
    if kind == "rainbow":       # 1段ずつ色を変えて虹色にする
        for r, row in enumerate(ITEM_ART):
            pal = {**PALETTE, "B": rainbow_color(t_ms, r * 30)}
            draw_pixel_art(surf, [row], pal, left, top + r * px, px)
    else:
        draw_pixel_art(surf, ITEM_ART, {**PALETTE, "B": ITEM_TYPES[kind]["color"]}, left, top, px)


def draw_bomb(surf, cx, top, px, t_ms=0):
    """爆弾を描く。火花がチカチカして、まわりが赤く光る"""
    w = len(BOMB_ART[0]) * px
    # 後ろの赤い光 (ドキドキするように大きさと濃さが変わる)
    pulse = (math.sin(t_ms / 120) + 1) / 2
    r = int(w * (0.42 + 0.08 * pulse))
    glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 60, 40, int(60 + 70 * pulse)), (r, r), r)
    surf.blit(glow, (int(cx - r), int(top + w * 0.62 - r)))
    spark = (255, 230, 80) if (t_ms // 80) % 2 == 0 else (255, 120, 30)
    pal = {"k": (55, 55, 70), "w": (190, 190, 210), "g": (130, 130, 140),
           "f": (180, 130, 70), "s": spark}
    draw_pixel_art(surf, BOMB_ART, pal, cx - w / 2, top, px)


def fmt_time(ms):
    s = max(0, (int(ms) + 999) // 1000)
    return f"{s // 60}:{s % 60:02d}"


def fmt_limit(ms):
    """制限時間を「1分」「1分30秒」のような文字にする"""
    s = ms // 1000
    m, s = divmod(s, 60)
    if m and s:
        return f"{m}分{s}秒"
    return f"{m}分" if m else f"{s}秒"


def wrap_text(font, text, width):
    """日本語向け: 1文字ずつ詰めて折り返す (、。！ などは行の先頭に来ないようにする)"""
    no_head = "、。，．！？）」』ー〜…・"
    lines = []
    for para in text.split("\n"):
        line = ""
        for ch in para:
            if line and font.size(line + ch)[0] > width and ch not in no_head:
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
        "retry": True,      # 置いてもできなかったら盤面を作り直す
    },
    {
        "title": "十字そろい",
        "text": f"同じ動物が ＋ の形（まん中と上下左右）にそろうと {CROSS_SCORE}点！\n"
                "ブロックは消えずに残るよ。\n\n"
                "ねこブロックを SPACE で落として、十字を作ろう！",
        "check": lambda d: d["crosses"] >= 1,
        "setup": "cross",
        "retry": True,
    },
    {
        "title": "とくしゅアイテム",
        "text": "動かしているブロックで、落ちてくるキャラを5しゅるい全部キャッチしよう！\n"
                "積んだブロックや床ではダメ。",
        "check": lambda d: d["items_got"] >= len(ITEM_TYPES),
        "setup": "items",
    },
    {
        "title": "ゲームオーバーなし",
        "text": "一番上まで積み上がっても、ゲームオーバーにならないよ！\n"
                "ブロックが全部くずれて、点数はそのまま続けられるよ。\n\n"
                "SPACE でどんどん落として、一番上まで積んでみよう！",
        "check": lambda d: d["collapses"] >= 1,
        "setup": "stack",
    },
    {
        "title": "本番のルール",
        "text": f"本番の制限時間は {fmt_limit(TIME_LIMIT_MS)}！\n"
                "たくさんラインを消して高得点をめざそう。\n"
                "積み上がってもゲームオーバーにならないよ。\n\n"
                "レベルは3つ。レベル2・3では ばくだんが落ちてくるよ。\n"
                f"動かしているブロックにあたると -{BOMB_PENALTY}点！",
        "check": None,  # 最後のページ
    },
]


# ================= アプリ本体 (画面の切り替え) =================
class App:
    def __init__(self):
        # 日本語入力 (IME) の変換ウィンドウが出ないようにする (pygame.init より前に)
        os.environ.setdefault("SDL_IME_SHOW_UI", "0")
        pygame.mixer.pre_init(22050, -16, 1, 512)   # 効果音用 (pygame.init より前に)
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Animal Block Remove")
        self.stop_ime()
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(170, 50)

        font_path = find_jp_font()
        self.f_small = make_font(font_path, 16)
        self.f = make_font(font_path, 20)
        self.f_mid = make_font(font_path, 28)
        self.f_big = make_font(font_path, 40)
        self.f_huge = make_font(font_path, 110)

        self.best = {lv: 0 for lv in DIFFICULTY}    # ハイスコアはレベルごと
        self.difficulty = 1     # えらんでいるレベル (1〜3)
        self.level_index = 0    # レベルえらび画面のカーソル
        self.bombs = None       # 落ちてくる爆弾 (レベル2・3のときだけ)
        self.bomb_hits = 0      # 爆弾にあたった回数
        self.booms = []         # 爆発のエフェクト
        self.game = None
        self.rain = []          # タイトル画面で降ってくる動物
        self.rain_timer = 0
        self.collapse = None    # くずれるエフェクト中のブロック (None なら再生していない)
        self.collapse_ms = 0
        self.effects = []       # 十字がそろったときの光と「+1000」
        self.sound = SoundBox()
        self.items = None       # 落ちてくるアイテム (本番のときだけ)
        self.popups = []        # 「+500点」などの浮かび上がる文字
        self.sparks = []        # キラキラ・はじける粒
        self.sparkle_timer = 0
        self.bgm_delay = 0      # ファンファーレのあと BGM を始めるまでの時間
        self.collapses = 0      # くずれた回数 (チュートリアルの確認用)
        self.go_title()

    # ---------- メインループ ----------
    def run(self):
        while True:
            # ウィンドウをドラッグしている間などは画面が止まり、そのあと dt が何秒分にもなる。
            # そのままだと時間が一気にへったり、爆弾やアイテムがワープしたりするので上限をつける
            dt = min(self.clock.tick(FPS), 100)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == getattr(pygame, "WINDOWFOCUSGAINED", -1):
                    self.stop_ime()     # ウィンドウにもどったときも、もう一度止める
                if event.type == pygame.KEYDOWN:
                    getattr(self, "key_" + self.state)(event.key)
            getattr(self, "update_" + self.state)(dt)
            getattr(self, "draw_" + self.state)()
            pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()

    @staticmethod
    def stop_ime():
        """文字入力モードを止める。
        これをしないと、日本語入力がオンのときにキーを押すと
        「p」「ぱ」などの変換ウィンドウが画面に出てしまう"""
        try:
            pygame.key.stop_text_input()
        except pygame.error:
            pass

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

    def text_with_enter(self, font, before, after, color, center):
        """「before ↩ after」を中央そろえで描く。
        ↩ は環境によってフォントに無いことがあるので、線で描いている"""
        a = font.render(before, True, color)
        b = font.render(after, True, color)
        h = font.get_height()
        iw, ih = int(h * 0.75), int(h * 0.55)   # ↩ マークの大きさ
        gap = 4
        total = a.get_width() + gap + iw + b.get_width()
        x = center[0] - total // 2
        top = center[1] - h // 2
        self.screen.blit(a, (x, top))
        x += a.get_width() + gap
        cy = center[1] + 1
        right, left = x + iw - 1, x + 1
        pygame.draw.line(self.screen, color, (right, cy - ih // 2), (right, cy), 2)   # たて線
        pygame.draw.line(self.screen, color, (right, cy), (left, cy), 2)              # よこ線
        head = max(3, ih // 2)
        pygame.draw.polygon(self.screen, color,                                       # 矢じり
                            [(left - 1, cy), (left + head, cy - head), (left + head, cy + head)])
        self.screen.blit(b, (x + iw, top))

    def draw_silhouette(self, game):
        """盤面の後ろに、オリジナルキャラクターのシルエットを大きく描く (ゆっくり上下にゆれる)"""
        t = pygame.time.get_ticks()
        if game.bonus_ms > 0:
            color = rainbow_color(t, 0, 60, 32)     # ボーナス中はうっすら虹色
        else:
            color = (32, 32, 50)
        px = 18
        w, h = len(ITEM_ART[0]) * px, len(ITEM_ART) * px
        left = (BOARD_W - w) / 2
        top = (HEIGHT - h) / 2 + math.sin(t / 600) * 6
        draw_pixel_art(self.screen, ITEM_ART, {ch: color for ch in "Bkwpnoms"}, left, top, px)

    def draw_board(self, game, show_piece=True):
        self.screen.fill(BG)
        self.draw_silhouette(game)
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

    # ---------- 積み上がったときの「くずれる」エフェクト ----------
    COLLAPSE_MAX_MS = 2200      # エフェクトの最長時間

    def start_collapse(self):
        """盤面のブロックをバラバラに飛ばすエフェクトを始め、盤面を空にする (点数はそのまま)"""
        g = self.game
        parts = []
        for y, row in enumerate(g.board):
            for x, kind in enumerate(row):
                if kind:
                    parts.append({
                        "kind": kind,
                        "x": float(x * CELL), "y": float(y * CELL),
                        "vx": random.uniform(-170, 170),       # 横方向の速さ
                        "vy": random.uniform(-420, -120),      # 上にはねる速さ
                        "angle": 0.0,
                        "spin": random.uniform(-540, 540),     # 回転の速さ (度/秒)
                        "delay": y * 22 + random.uniform(0, 120),  # 上の段から順にくずれる
                    })
        g.clear_board()
        self.collapse = parts
        self.collapse_ms = 0
        self.collapses += 1
        self.effects = []
        for group in (self.items, self.bombs):
            if group:
                group.falling.clear()       # 落ちていたアイテムや爆弾も消える

    def update_collapse(self, dt):
        """エフェクト再生中なら進めて True を返す (その間ゲームは止まる)"""
        if self.collapse is None:
            return False
        self.collapse_ms += dt
        s = dt / 1000
        for p in self.collapse:
            if self.collapse_ms < p["delay"]:
                continue
            p["vy"] += 1500 * s             # 重力
            p["x"] += p["vx"] * s
            p["y"] += p["vy"] * s
            p["angle"] += p["spin"] * s
        all_gone = all(p["y"] > HEIGHT for p in self.collapse)
        if (self.collapse_ms > 500 and all_gone) or self.collapse_ms > self.COLLAPSE_MAX_MS:
            self.collapse = None
        return True

    def draw_collapse(self):
        if self.collapse is None:
            return
        ms = self.collapse_ms
        board = pygame.Rect(0, 0, BOARD_W, HEIGHT)
        self.screen.set_clip(board)     # 右のパネルにははみ出さない
        # 最初の一瞬だけ画面がゆれる
        shake = random.randint(-4, 4) if ms < 350 else 0
        for p in self.collapse:
            tile = animal_tile(p["kind"], CELL)
            if ms >= p["delay"] and p["angle"]:
                tile = pygame.transform.rotate(tile, p["angle"])
            cx = p["x"] + CELL / 2 + shake
            cy = p["y"] + CELL / 2
            self.screen.blit(tile, tile.get_rect(center=(int(cx), int(cy))))
        # 始まった瞬間に白く光る
        if ms < 250:
            flash = pygame.Surface(board.size, pygame.SRCALPHA)
            flash.fill((255, 255, 255, int(150 * (1 - ms / 250))))
            self.screen.blit(flash, (0, 0))
        self.screen.set_clip(None)
        self.dim(150, pygame.Rect(0, HEIGHT // 2 - 55, BOARD_W, 110))   # 文字を読みやすくする帯
        self.text(self.f_big, "くずれた！", WARN, (BOARD_W // 2, HEIGHT // 2 - 20),
                  center=True, shadow=True)
        self.text(self.f, "スコアはそのまま！", TEXT, (BOARD_W // 2, HEIGHT // 2 + 28),
                  center=True, shadow=True)

    # ---------- 十字がそろったときのエフェクト ----------
    CROSS_EFFECT_MS = 1200

    def update_effects(self, dt):
        """ゲームから届いた知らせをエフェクトにして、時間を進める"""
        for ev in self.game.events:
            if ev["type"] == "cross":
                self.effects.append({"cells": ev["cells"], "kind": ev["kind"], "ms": 0})
        self.game.events.clear()
        for e in self.effects:
            e["ms"] += dt
        self.effects = [e for e in self.effects if e["ms"] < self.CROSS_EFFECT_MS]

    def draw_effects(self):
        for e in self.effects:
            ms = e["ms"]
            t = ms / self.CROSS_EFFECT_MS
            # 5つのブロックがチカチカ光る
            if (ms // 100) % 2 == 0 and t < 0.7:
                glow = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
                glow.fill((255, 255, 255, 140))
                for x, y in e["cells"]:
                    self.screen.blit(glow, (x * CELL, y * CELL))
            for x, y in e["cells"]:
                pygame.draw.rect(self.screen, ACCENT, (x * CELL, y * CELL, CELL, CELL), 3)
            # まん中から「+1000」が浮かび上がる
            cx, cy = e["cells"][0]
            px = min(max(cx * CELL + CELL // 2, 90), BOARD_W - 90)
            py = cy * CELL - 85 - int(40 * t)       # 十字の上に出す
            if py < 70:                             # 上のほうなら十字の下に出す
                py = cy * CELL + 2 * CELL + 50 + int(40 * t)
            self.text(self.f_mid, "十字そろい！", ACCENT, (px, py - 30), center=True, shadow=True)
            self.text(self.f_big, f"+{CROSS_SCORE}", GOOD, (px, py + 4), center=True, shadow=True)

    # ---------- とくしゅアイテム・ボーナスタイムのエフェクト ----------
    POPUP_MS = 1300

    def reset_play_effects(self):
        self.sound.stop_bgm()
        self.popups = []
        self.sparks = []
        self.booms = []
        self.sparkle_timer = 0
        self.bgm_delay = 0

    def add_popup(self, text, color, x, y):
        """浮かび上がる文字 (color が None なら虹色)"""
        self.popups.append({"text": text, "color": color, "x": x, "y": y, "ms": 0})

    def burst(self, x, y, color, n=16):
        """はじける粒 (color が None なら虹色)"""
        for _ in range(n):
            ang = random.uniform(0, 2 * math.pi)
            sp = random.uniform(60, 240)
            self.sparks.append({"x": x, "y": y, "vx": math.cos(ang) * sp,
                                "vy": math.sin(ang) * sp - 60, "ms": 0,
                                "life": random.uniform(500, 900), "color": color,
                                "size": random.randint(3, 6), "twinkle": False})

    def apply_item(self, kind, x, y, demo=False):
        """アイテムがブロックにあたったときの効果。
        demo=True (チュートリアル) のときは、音と見た目だけで中身は変えない"""
        g = self.game
        info = ITEM_TYPES[kind]
        if kind == "gray":
            if not demo:
                g.score += ITEM_SCORE
            text, sound = f"+{ITEM_SCORE}点", "score"
        elif kind == "rainbow":
            if not demo:
                g.bonus_ms = BONUS_MS       # ボーナス中にもう一度取ったら1分にもどる
                self.bgm_delay = 900        # ファンファーレのあとに BGM
            text, sound = "ボーナスタイム！", "rainbow"
        else:
            if not demo:
                g.time_left += info["sec"] * 1000
            text, sound = f"時間 +{info['sec']}秒", "time"
        self.sound.play(sound)
        self.add_popup(text, info["color"], x, y)
        self.burst(x, y, info["color"], 28 if kind == "rainbow" else 16)

    def apply_bomb(self, x, y):
        """爆弾が動かしているブロックにあたったとき: 減点 (0点より下にはならない)"""
        g = self.game
        g.score = max(0, g.score - BOMB_PENALTY)
        self.bomb_hits += 1
        self.sound.play("bomb")
        self.add_popup(f"-{BOMB_PENALTY}点", WARN, x, y)
        for color, n in (((255, 140, 40), 18), ((255, 60, 40), 12), ((255, 230, 90), 8)):
            self.burst(x, y, color, n)
        self.booms.append({"x": x, "y": y, "ms": 0})

    def update_items(self, dt, demo=False):
        """落ちてくるアイテムと爆弾を動かして効果を出す。キャッチしたアイテムの種類のリストを返す"""
        caught = []
        groups = [grp for grp in (self.items, self.bombs) if grp]
        for group in groups:
            others = [o for o in groups if o is not group]
            for ev in group.update(dt, self.game, others):
                bomb = ev["kind"] == "bomb"
                if ev["type"] == "appear":
                    self.sound.play("bomb_appear" if bomb else "appear")
                elif ev["type"] == "hit":
                    if bomb:
                        self.apply_bomb(ev["x"], ev["y"])
                    else:
                        self.apply_item(ev["kind"], ev["x"], ev["y"], demo)
                        caught.append(ev["kind"])
                elif ev["type"] == "land":  # 積んだブロックや床: 効果なしで、ふっと消える
                    self.burst(ev["x"], ev["y"], (120, 120, 135), 8)
        self.game.trail.clear()             # 通りすぎたマスの記録は毎回リセット
        return caught

    def update_particles(self, dt):
        s = dt / 1000
        for p in self.sparks:
            p["ms"] += dt
            if not p["twinkle"]:
                p["vy"] += 300 * s          # 重力
            p["x"] += p["vx"] * s
            p["y"] += p["vy"] * s
        self.sparks = [p for p in self.sparks if p["ms"] < p["life"]]
        for p in self.popups:
            p["ms"] += dt
        self.popups = [p for p in self.popups if p["ms"] < self.POPUP_MS]
        for b in self.booms:
            b["ms"] += dt
        self.booms = [b for b in self.booms if b["ms"] < self.BOOM_MS]
        # ボーナスタイム中は盤面にキラキラを降らせる
        g = self.game
        if g.bonus_ms > 0 and not g.paused:
            self.sparkle_timer += dt
            while self.sparkle_timer > 60:
                self.sparkle_timer -= 60
                self.sparks.append({"x": random.uniform(0, BOARD_W), "y": random.uniform(0, HEIGHT),
                                    "vx": 0, "vy": random.uniform(10, 50), "ms": 0,
                                    "life": random.uniform(400, 900), "color": None,
                                    "size": random.randint(2, 4), "twinkle": True})

    def draw_falling_label(self, label, color, cx, top):
        """落ちてくるものの頭の上の文字 (盤面のはしで切れないように)"""
        if top <= -20:
            return
        half = self.f_small.size(label)[0] // 2 + 4
        lx = min(max(int(cx), half), BOARD_W - half)
        self.text(self.f_small, label, color, (lx, int(top) - 8), center=True, shadow=True)

    def draw_items(self):
        t = pygame.time.get_ticks()
        if self.items:
            for it in self.items.falling:
                info = ITEM_TYPES[it["kind"]]
                cx = it["col"] * CELL + CELL / 2 + math.sin(t / 150 + it["col"]) * 2  # ふわふわゆれる
                top = it["y"] - (len(ITEM_ART) * ITEM_PX - CELL) / 2
                draw_item(self.screen, it["kind"], cx, top, ITEM_PX, t)
                self.draw_falling_label(info["label"], info["color"] or rainbow_color(t), cx, top)
        if self.bombs:
            for b in self.bombs.falling:
                cx = b["col"] * CELL + CELL / 2 + math.sin(t / 60 + b["col"]) * 1.5   # ぷるぷるふるえる
                top = b["y"] - (len(BOMB_ART) * ITEM_PX - CELL) / 2
                draw_bomb(self.screen, cx, top, ITEM_PX, t)
                self.draw_falling_label(f"-{BOMB_PENALTY}", WARN, cx, top)

    BOOM_MS = 450

    def draw_booms(self):
        """爆発: 盤面が一瞬赤く光り、オレンジの輪が広がる"""
        for b in self.booms:
            k = b["ms"] / self.BOOM_MS
            if k < 0.5:
                flash = pygame.Surface((BOARD_W, HEIGHT), pygame.SRCALPHA)
                flash.fill((255, 60, 30, int(75 * (1 - k * 2))))
                self.screen.blit(flash, (0, 0))
            x, y = int(b["x"]), int(b["y"])
            pygame.draw.circle(self.screen, (255, 160, 50), (x, y), int(12 + 90 * k), 4)
            if k > 0.15:
                pygame.draw.circle(self.screen, (255, 230, 120), (x, y), int(8 + 60 * (k - 0.15)), 3)

    def draw_particles(self):
        t = pygame.time.get_ticks()
        self.screen.set_clip(pygame.Rect(0, 0, BOARD_W, HEIGHT))
        self.draw_booms()
        for p in self.sparks:
            k = 1 - p["ms"] / p["life"]
            size = max(1, int(p["size"] * (0.4 + 0.6 * k)))
            color = p["color"] or rainbow_color(t, p["x"] * 2)
            x, y = int(p["x"]), int(p["y"])
            if p["twinkle"]:                # 十字の形にキラッと光る
                pygame.draw.line(self.screen, color, (x - size, y), (x + size, y), 2)
                pygame.draw.line(self.screen, color, (x, y - size), (x, y + size), 2)
            else:
                self.screen.fill(color, (x - size // 2, y - size // 2, size, size))
        self.screen.set_clip(None)
        for p in self.popups:
            k = p["ms"] / self.POPUP_MS
            x = min(max(p["x"], 110), BOARD_W - 110)
            y = min(max(p["y"] - 40 - 50 * k, 100), HEIGHT - 30)   # 上のボーナス表示と重ならない
            color = p["color"] or rainbow_color(t)
            self.text(self.f_mid, p["text"], color, (int(x), int(y)), center=True, shadow=True)

    def draw_bonus_overlay(self):
        """ボーナスタイム中: 盤面のふちが虹色に光り、上に残り時間を出す"""
        g = self.game
        if g.bonus_ms <= 0:
            return
        t = pygame.time.get_ticks()
        for i in range(3):
            pygame.draw.rect(self.screen, rainbow_color(t, i * 40),
                             (i * 2, i * 2, BOARD_W - i * 4, HEIGHT - i * 4), 2)
        blink = g.bonus_ms > 5000 or (g.bonus_ms // 200) % 2 == 0   # 終わりぎわは点滅
        if blink:
            self.text(self.f_mid, "ボーナスタイム！", rainbow_color(t), (BOARD_W // 2, 26),
                      center=True, shadow=True)
            self.text(self.f_small, f"時間がへらない！  のこり {fmt_time(g.bonus_ms)}", TEXT,
                      (BOARD_W // 2, 56), center=True, shadow=True)

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
    MENU = ["ゲームスタート", "あそびかた（チュートリアル）"]

    def go_title(self):
        self.state = "title"
        self.menu_index = 0
        self.collapse = None
        self.effects = []
        self.items = None
        self.bombs = None
        self.reset_play_effects()

    def key_title(self, key):
        # タイトル画面からはゲームを終われないようにしている (ESC も効かない)
        if key == pygame.K_UP:
            self.menu_index = (self.menu_index - 1) % len(self.MENU)
        elif key == pygame.K_DOWN:
            self.menu_index = (self.menu_index + 1) % len(self.MENU)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.menu_index == 0:
                self.go_level()
            else:
                self.go_tutorial()

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
        bg = scaled_image(TITLE_BG_FILE, (WIDTH, HEIGHT))
        if bg:
            self.screen.blit(bg, (0, 0))
        for x, y, kind, _ in self.rain:
            self.screen.blit(animal_tile(kind, CELL), (x, int(y)))
        self.dim(150)

        cx = WIDTH // 2
        self.text(self.f_big, "Animal Block Remove", ACCENT, (cx, 70), center=True, shadow=True)

        # 真ん中の大きな猫 (画像があれば画像)
        draw_big_cat(self.screen, cx, 150, 9)
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

        if any(self.best.values()):
            scores = "   ".join(f"レベル{lv} {s}" for lv, s in self.best.items())
            self.text(self.f_small, f"ハイスコア   {scores}", TEXT, (cx, 535), center=True)
        self.text_with_enter(self.f_small, "↑↓ でえらぶ ／ ENTER", " で決定", SUB, (cx, 570))

    # ==================================================
    # レベルえらび画面
    # ==================================================
    def go_level(self):
        self.state = "level"
        self.level_index = self.difficulty - 1      # 前にえらんだレベルにカーソルを合わせる

    def key_level(self, key):
        levels = list(DIFFICULTY)
        if key == pygame.K_UP:
            self.level_index = (self.level_index - 1) % len(levels)
        elif key == pygame.K_DOWN:
            self.level_index = (self.level_index + 1) % len(levels)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.difficulty = levels[self.level_index]
            self.go_ready()
        elif key == pygame.K_ESCAPE:
            self.go_title()

    def update_level(self, dt):
        self.update_title(dt)       # 後ろで動物が降るのはタイトルと同じ

    def draw_level(self):
        self.screen.fill(BG)
        for x, y, kind, _ in self.rain:
            self.screen.blit(animal_tile(kind, CELL), (x, int(y)))
        self.dim(170)
        cx = WIDTH // 2
        t = pygame.time.get_ticks()
        self.text(self.f_big, "レベルをえらんでね", ACCENT, (cx, 60), center=True, shadow=True)
        for i, (lv, d) in enumerate(DIFFICULTY.items()):
            rect = pygame.Rect(0, 0, 440, 120)
            rect.center = (cx, 175 + i * 135)
            chosen = i == self.level_index
            pygame.draw.rect(self.screen, (45, 42, 30) if chosen else (30, 30, 48), rect, border_radius=14)
            pygame.draw.rect(self.screen, d["color"] if chosen else GRID, rect, 3 if chosen else 2,
                             border_radius=14)
            self.text(self.f_mid, f"レベル{lv}  {d['name']}", d["color"] if chosen else SUB,
                      (rect.x + 24, rect.y + 14))
            self.text(self.f, d["desc"], TEXT if chosen else SUB, (rect.x + 26, rect.y + 54))
            self.text(self.f_small, f"ハイスコア  {self.best[lv]}", SUB, (rect.x + 26, rect.y + 86))
            # 右がわに爆弾の数で「むずかしさ」を見せる
            for b in range(d["bomb_max"]):
                draw_bomb(self.screen, rect.right - 40 - b * 44, rect.y + 34, 3, t + b * 200)
            if d["bomb_max"] == 0:
                draw_item(self.screen, "gray", rect.right - 40, rect.y + 34, 3, t)
        self.text_with_enter(self.f_small, "↑↓ でえらぶ ／ ENTER", " で決定 ／ ESC でもどる", SUB,
                             (cx, 575))

    # ==================================================
    # スタート画面 (ルール説明 → 3,2,1 カウントダウン)
    # ==================================================
    def go_ready(self, skip_info=False):
        self.state = "ready"
        self.game = Tetris(time_limit=TIME_LIMIT_MS)
        self.collapse = None
        self.effects = []
        self.items = Items()
        d = DIFFICULTY[self.difficulty]
        if d["bomb_max"]:
            self.bombs = Items(first_ms=d["bomb_first"], interval=d["bomb_interval"],
                               weights={"bomb": 1}, max_falling=d["bomb_max"])
        else:
            self.bombs = None
        self.bomb_hits = 0
        self.reset_play_effects()
        self.ready_phase = "count" if skip_info else "info"
        self.count_ms = 3000

    def key_ready(self, key):
        if key == pygame.K_ESCAPE:
            self.go_level()
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
            d = DIFFICULTY[self.difficulty]
            self.box(pygame.Rect(cx - 220, cy - 215, 440, 430), border=d["color"])
            self.text(self.f_big, "スタート", ACCENT, (cx, cy - 172), center=True)
            self.text(self.f_mid, f"レベル{self.difficulty}  {d['name']}", d["color"],
                      (cx, cy - 125), center=True)
            lines = [
                ("制限時間", fmt_limit(TIME_LIMIT_MS), TEXT),
                ("1列", f"{LINE_SCORES[1]}点", TEXT),
                ("3列同時", f"{LINE_SCORES[3]}点！", TEXT),
                ("十字そろい", f"{CROSS_SCORE}点！", TEXT),
            ]
            if d["bomb_max"]:
                lines.append(("ばくだん", f"-{BOMB_PENALTY}点", WARN))
            for i, (a, b, color) in enumerate(lines):
                y = cy - 78 + i * 36
                self.text(self.f_mid, a, SUB, (cx - 175, y - 16))
                self.text(self.f_mid, b, color, (cx - 15, y - 16))
            if d["bomb_max"]:
                self.text(self.f_small, "ばくだんは、動かしているブロックにあたると減点！", WARN,
                          (cx, cy + 112), center=True)
            self.text(self.f_mid, "SPACE でスタート", ACCENT, (cx, cy + 150), center=True)
            self.text(self.f_small, "ESC でレベルえらびにもどる", SUB, (cx, cy + 185), center=True)
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
        elif self.collapse is not None:     # くずれている間は操作できない
            return
        elif key == pygame.K_p:
            g.paused = not g.paused
            self.sound.pause_bgm(g.paused)
        elif not g.paused:
            apply_game_key(g, key)

    def update_play(self, dt):
        if self.update_collapse(dt):        # くずれている間は時間も止まる
            return
        g = self.game
        self.update_effects(dt)
        self.update_particles(dt)
        if not g.paused:
            self.update_items(dt)
            if self.bgm_delay > 0:
                self.bgm_delay -= dt
                if self.bgm_delay <= 0 and g.bonus_ms > 0:
                    self.sound.start_bgm()
        in_bonus = g.bonus_ms > 0
        g.update(dt)
        if in_bonus and g.bonus_ms <= 0:    # ボーナスタイムがおわった
            self.sound.stop_bgm()
            self.sound.play("bonus_end")
            self.add_popup("ボーナスおわり", TEXT, BOARD_W // 2, HEIGHT // 2)
        if g.topped_out:
            self.start_collapse()
            return
        if g.finished:
            self.sound.stop_bgm()
            best = self.best[self.difficulty]
            self.new_record = g.score > best
            self.best[self.difficulty] = max(best, g.score)
            self.go_result()

    def draw_side_play(self):
        g = self.game
        px = BOARD_W + 20
        # 残り時間 (10秒を切ると赤く点滅)
        t = g.time_left
        bonus = g.bonus_ms > 0
        now = pygame.time.get_ticks()
        color = TEXT
        if bonus:                           # ボーナス中は止まった時間が虹色に光る
            color = rainbow_color(now)
        elif t <= 10000 and (t // 250) % 2 == 0:
            color = WARN
        self.text(self.f, "のこり時間", SUB, (px, 12))
        self.text(self.f_big, fmt_time(t), color, (px, 34))
        # 右上にいまのレベル
        d = DIFFICULTY[self.difficulty]
        tag = self.f_small.render(f"レベル{self.difficulty}", True, BG)
        pill = tag.get_rect(topright=(WIDTH - 20, 14)).inflate(16, 6)
        pygame.draw.rect(self.screen, d["color"], pill, border_radius=10)
        self.screen.blit(tag, tag.get_rect(center=pill.center))
        bar = pygame.Rect(px, 98, SIDE - 40, 10)
        pygame.draw.rect(self.screen, GRID, bar, border_radius=5)
        fill = bar.copy()
        fill.width = int(bar.width * min(1, t / TIME_LIMIT_MS))   # 時間がふえても枠からはみ出さない
        bar_color = rainbow_color(now) if bonus else (WARN if t <= 10000 else GOOD)
        pygame.draw.rect(self.screen, bar_color, fill, border_radius=5)

        self.draw_next_hold(125)

        # 「レベル」は難易度の名前に使うので、落ちる速さは「スピード」と表示する
        rows = [("スコア", g.score), ("ライン", g.lines), ("スピード", g.level),
                ("ハイスコア", self.best[self.difficulty])]
        for i, (label, val) in enumerate(rows):
            y = 235 + i * 34
            self.text(self.f, label, SUB, (px, y))
            self.text(self.f_mid, str(val), TEXT, (px + 105, y - 6))

        helps = ["← → ：いどう", "↓ ：ソフトドロップ", "↑ / X ・ Z ：かいてん",
                 "SPACE ：ハードドロップ", "C ：ホールド", "P ：一時停止", "ESC ：タイトルへ"]
        for i, s in enumerate(helps):
            self.text(self.f_small, s, SUB, (px, 400 + i * 26))

    def draw_play(self):
        self.draw_board(self.game, show_piece=self.collapse is None)
        self.draw_items()
        self.draw_bonus_overlay()
        self.draw_side_play()
        self.draw_effects()
        self.draw_particles()
        self.draw_collapse()
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

    def key_result(self, key):
        if self.result_ms < 800:    # 連打で一瞬で飛ばさないように少し待つ
            return
        if key in (pygame.K_SPACE, pygame.K_RETURN):
            self.go_ready(skip_info=True)
        elif key == pygame.K_ESCAPE:
            self.go_title()

    def update_result(self, dt):
        self.result_ms += dt        # 時間切れでタイトルにもどることはない

    def draw_result(self):
        g = self.game
        self.draw_board(g, show_piece=False)
        self.draw_side_play()
        self.dim(180)
        cx, cy = WIDTH // 2, HEIGHT // 2
        d = DIFFICULTY[self.difficulty]
        self.box(pygame.Rect(cx - 210, cy - 195, 420, 390), border=d["color"])

        title = "タイムアップ！" if g.time_up else "ゲームオーバー"
        self.text(self.f_big, title, ACCENT, (cx, cy - 150), center=True)
        self.text(self.f, f"レベル{self.difficulty}  {d['name']}", d["color"], (cx, cy - 108), center=True)
        self.text(self.f_mid, f"スコア  {g.score}", TEXT, (cx, cy - 70), center=True)
        self.text(self.f, f"消したライン  {g.lines}   十字そろい  {g.crosses}", TEXT,
                  (cx, cy - 34), center=True)
        if d["bomb_max"]:
            self.text(self.f, f"ばくだんにあたった  {self.bomb_hits}回", WARN, (cx, cy - 6), center=True)
        if self.new_record and g.score > 0:
            self.text(self.f_mid, "★ ハイスコア更新！ ★", GOOD, (cx, cy + 32), center=True)
        else:
            self.text(self.f, f"ハイスコア  {self.best[self.difficulty]}", SUB, (cx, cy + 32), center=True)

        self.text(self.f_mid, "コンティニュー？", TEXT, (cx, cy + 85), center=True)
        self.text(self.f, f"SPACE ：同じレベルでもう一度（{fmt_limit(TIME_LIMIT_MS)}）", GOOD,
                  (cx, cy + 125), center=True)
        self.text(self.f, "ESC ：タイトルにもどる", SUB, (cx, cy + 157), center=True)

    # ==================================================
    # チュートリアル
    # ==================================================
    def go_tutorial(self):
        self.state = "tutorial"
        self.game = Tetris(time_limit=None, gravity_ms=1200)  # ゆっくり落ちる
        self.collapse = None
        self.effects = []
        self.items = None
        self.bombs = None           # チュートリアルでは爆弾は出ない
        self.reset_play_effects()
        self.items_got = 0          # チュートリアルでキャッチしたアイテムの種類の数
        self.item_left = []         # まだキャッチしていないアイテムの種類
        self.step = 0
        self.step_done_ms = 0       # 「できた！」表示の残り時間
        self.start_step()

    def snapshot(self):
        return dict(self.game.stats, lines=self.game.lines, crosses=self.game.crosses,
                    items_got=self.items_got, collapses=self.collapses)

    def start_step(self):
        self.step_base = self.snapshot()
        self.items = None
        if TUTORIAL_STEPS[self.step].get("setup"):
            self.setup_practice()
        elif TUTORIAL_STEPS[self.step]["check"] is None:
            self.game.clear_board()     # 最後のページはまっさらな盤面で

    def setup_practice(self):
        """練習用の盤面を作る"""
        g = self.game
        g.clear_board()
        kind = TUTORIAL_STEPS[self.step]["setup"]
        bottom = ROWS - 1
        if kind == "line":
            # 一番下の列に4マスのすきまを作り、うさぎ(I)ブロックを出す
            g.board[bottom] = [None if 3 <= x <= 6 else random.choice(KINDS) for x in range(COLS)]
            g.current = Piece("I")
        elif kind == "cross":
            # 一番下にねこを1つ置き、その上にねこ(T)ブロックを落とすと ＋ になる
            others = [k for k in KINDS if k != "T"]
            g.board[bottom] = [random.choice(others) if x in (0, 1, 7, 8) else None
                               for x in range(COLS)]
            g.board[bottom][4] = "T"
            g.current = Piece("T")
        elif kind == "items":
            # 5しゅるいのアイテムを、まだ取っていないものから順番に落とす
            self.item_left = list(ITEM_TYPES)
            self.items = Items(first_ms=700, interval=(1000, 1500), choices=self.item_left)
        elif kind == "stack":
            # 下半分くらいまで積んでおき、すぐ一番上まで届くようにする。
            # 各段に1つすきまを空けてラインが消えないようにし、
            # となり同士がちがう動物になる並べ方で十字もできないようにしている
            for y in range(8, ROWS):
                gap = (y * 3) % COLS
                g.board[y] = [None if x == gap else KINDS[(x + 2 * y) % len(KINDS)]
                              for x in range(COLS)]
        for y in range(ROWS):
            g.ids[y] = [g.new_id() if c else None for c in g.board[y]]
        self.practice_locks = g.stats["locks"]

    def key_tutorial(self, key):
        last = self.step == len(TUTORIAL_STEPS) - 1
        if key == pygame.K_ESCAPE:
            self.go_title()
        elif last and key in (pygame.K_SPACE, pygame.K_RETURN):
            self.go_level()
        elif self.collapse is not None:       # くずれている間は操作できない
            return
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
        if step["check"] is None:     # 最後のページ
            return
        if self.update_collapse(dt):
            return
        self.update_effects(dt)
        self.update_particles(dt)
        for kind in self.update_items(dt, demo=True):
            if kind in self.item_left:
                self.item_left.remove(kind)
                self.items_got += 1
        g.update(dt)
        if g.topped_out:              # 本番と同じく、積み上がったらくずれる
            self.start_collapse()
            return

        if self.step_done_ms > 0:
            self.step_done_ms -= dt
            if self.step_done_ms <= 0:
                self.next_step()
            return

        now = self.snapshot()
        delta = {k: now[k] - self.step_base[k] for k in now}
        if step["check"](delta):
            self.step_done_ms = 1000
            if self.items:
                self.items.falling.clear()
        elif step.get("retry") and g.stats["locks"] > self.practice_locks:
            self.setup_practice()       # できなかったらやり直し

    def draw_item_checklist(self, x, y):
        """アイテム練習: 5しゅるいのうち、どれを取ったかの一覧"""
        t = pygame.time.get_ticks()
        for i, (kind, it) in enumerate(ITEM_TYPES.items()):
            row = y + i * 30
            got = kind not in self.item_left
            draw_item(self.screen, kind, x + 12, row, 2, t)
            color = (it["color"] or rainbow_color(t)) if got else SUB
            self.text(self.f, it["title"], color, (x + 34, row - 1))
            if got:                     # 取ったものにはチェックマーク
                cx, cy = x + 212, row + 12
                pygame.draw.lines(self.screen, GOOD, False,
                                  [(cx - 8, cy), (cx - 3, cy + 6), (cx + 8, cy - 7)], 4)

    def draw_tutorial(self):
        g = self.game
        step = TUTORIAL_STEPS[self.step]
        last = step["check"] is None
        self.draw_board(g, show_piece=not last and self.collapse is None)
        self.draw_items()
        self.draw_effects()
        self.draw_particles()
        self.draw_collapse()
        px = BOARD_W + 20

        self.text(self.f, f"チュートリアル  {self.step + 1} / {len(TUTORIAL_STEPS)}", SUB, (px, 12))
        # 進み具合のバー (ステップ数に合わせて幅を決める)
        n = len(TUTORIAL_STEPS)
        slot = (SIDE - 40) // n
        for i in range(n):
            color = ACCENT if i <= self.step else GRID
            pygame.draw.rect(self.screen, color, (px + i * slot, 42, slot - 5, 6), border_radius=3)

        if not last:
            self.draw_next_hold(62)

        top = 62 if last else 160
        # 長いタイトルはパネルからはみ出さないよう小さい文字にする
        title_font = self.f_mid if self.f_mid.size(step["title"])[0] <= SIDE - 30 else self.f
        self.text(title_font, step["title"], ACCENT, (px, top + (0 if title_font is self.f_mid else 6)))
        lines = wrap_text(self.f, step["text"], SIDE - 40)
        for i, line in enumerate(lines):
            self.text(self.f, line, TEXT, (px, top + 45 + i * 28))

        if step.get("setup") == "items":
            self.draw_item_checklist(px, top + 55 + len(lines) * 28)

        if last:
            self.text(self.f, "SPACE ：ゲームスタート", GOOD, (px, HEIGHT - 80))
            self.text(self.f, "ESC ：タイトルへ", SUB, (px, HEIGHT - 50))
            # 盤面側にはまとめの絵 (画像があれば画像)
            self.dim(120, pygame.Rect(0, 0, BOARD_W, HEIGHT))
            draw_big_cat(self.screen, BOARD_W // 2, 170, 10)
            self.text(self.f_big, "がんばって！", ACCENT, (BOARD_W // 2, 360), center=True, shadow=True)
        else:
            self.text(self.f_small, "ENTER ：この説明をとばす", SUB, (px, HEIGHT - 52))
            self.text(self.f_small, "ESC ：タイトルへ", SUB, (px, HEIGHT - 28))

        if self.step_done_ms > 0:
            self.text(self.f_big, "できた！", GOOD, (BOARD_W // 2, HEIGHT // 2), center=True, shadow=True)


if __name__ == "__main__":
    App().run()