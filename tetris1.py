import random
from dataclasses import dataclass

import pyxel


CELL_SIZE = 8
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BOARD_X = 12
BOARD_Y = 12
SIDE_X = 108
WINDOW_WIDTH = 208
WINDOW_HEIGHT = 240
DROP_FRAMES = 18
LOCK_DELAY_FRAMES = 20
PREVIEW_COUNT = 3
CONTROL_Y = 186

PIECE_COLORS = {
    "I": 12,
    "O": 10,
    "T": 2,
    "S": 11,
    "Z": 8,
    "J": 5,
    "L": 9,
}

PIECES = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

WALL_KICKS = [(0, 0), (-1, 0), (1, 0), (0, -1), (-2, 0), (2, 0)]
LINE_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}


@dataclass
class ActivePiece:
    kind: str
    x: int
    y: int
    rotation: int = 0


@dataclass(frozen=True)
class TouchButton:
    name: str
    x: int
    y: int
    w: int
    h: int
    label: str
    color: int


TOUCH_BUTTONS = [
    TouchButton("left", 12, CONTROL_Y, 42, 20, "LEFT", 5),
    TouchButton("right", 58, CONTROL_Y, 42, 20, "RIGHT", 12),
    TouchButton("rotate", 104, CONTROL_Y, 42, 20, "ROT", 9),
    TouchButton("down", 150, CONTROL_Y, 46, 20, "DOWN", 11),
    TouchButton("drop", 12, CONTROL_Y + 28, 88, 20, "HARD DROP", 8),
    TouchButton("restart", 104, CONTROL_Y + 28, 92, 20, "RESTART", 2),
]


class TetrisApp:
    def __init__(self) -> None:
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT, title="Pyxel Tetris", fps=30)
        pyxel.mouse(True)
        self.touch_frames = {button.name: 0 for button in TOUCH_BUTTONS}
        self.touch_down = {button.name: False for button in TOUCH_BUTTONS}
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self) -> None:
        self.board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.bag = []
        self.next_queue = [self.draw_from_bag() for _ in range(PREVIEW_COUNT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.drop_timer = 0
        self.lock_timer = 0
        self.game_over = False
        self.current_piece = self.spawn_piece()

    def draw_from_bag(self) -> str:
        if not self.bag:
            self.bag = list(PIECES.keys())
            random.shuffle(self.bag)
        return self.bag.pop()

    def spawn_piece(self) -> ActivePiece:
        kind = self.next_queue.pop(0)
        self.next_queue.append(self.draw_from_bag())
        piece = ActivePiece(kind=kind, x=3, y=0)
        if self.collides(piece):
            self.game_over = True
        return piece

    def update(self) -> None:
        self.update_touch_state()

        if pyxel.btnp(pyxel.KEY_R) or self.touch_btnp("restart"):
            self.reset_game()
            return

        if self.game_over:
            return

        moved = False
        if pyxel.btnp(pyxel.KEY_LEFT, hold=8, repeat=2) or self.touch_btnp("left", hold=8, repeat=2):
            moved = self.try_move(-1, 0) or moved
        if pyxel.btnp(pyxel.KEY_RIGHT, hold=8, repeat=2) or self.touch_btnp("right", hold=8, repeat=2):
            moved = self.try_move(1, 0) or moved
        if pyxel.btnp(pyxel.KEY_Z):
            moved = self.try_rotate(-1) or moved
        if pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.KEY_UP) or self.touch_btnp("rotate"):
            moved = self.try_rotate(1) or moved
        if pyxel.btnp(pyxel.KEY_SPACE) or self.touch_btnp("drop"):
            self.hard_drop()
            return

        drop_speed = self.current_drop_frames()
        soft_drop = pyxel.btn(pyxel.KEY_DOWN) or self.touch_btn("down")
        self.drop_timer += 1

        if soft_drop:
            if self.try_move(0, 1):
                self.score += 1
            else:
                self.lock_timer += 2

        if moved:
            self.lock_timer = 0

        if self.drop_timer >= drop_speed:
            self.drop_timer = 0
            if not self.try_move(0, 1):
                self.lock_timer += 1

        if not self.can_move(self.current_piece, 0, 1):
            self.lock_timer += 1
            if self.lock_timer >= LOCK_DELAY_FRAMES:
                self.lock_piece()
        else:
            self.lock_timer = 0

    def current_drop_frames(self) -> int:
        return max(4, DROP_FRAMES - (self.level - 1) * 2)

    def update_touch_state(self) -> None:
        pointer_down = pyxel.btn(pyxel.MOUSE_BUTTON_LEFT)
        pointer_x = pyxel.mouse_x
        pointer_y = pyxel.mouse_y

        for button in TOUCH_BUTTONS:
            is_down = pointer_down and self.point_in_rect(pointer_x, pointer_y, button)
            self.touch_frames[button.name] = self.touch_frames[button.name] + 1 if is_down else 0
            self.touch_down[button.name] = is_down

    def touch_btn(self, name: str) -> bool:
        return self.touch_down[name]

    def touch_btnp(self, name: str, hold: int | None = None, repeat: int | None = None) -> bool:
        frames = self.touch_frames[name]
        if frames == 1:
            return True
        if hold is None or repeat is None or frames < hold:
            return False
        return (frames - hold) % repeat == 0

    def point_in_rect(self, x: int, y: int, button: TouchButton) -> bool:
        return button.x <= x < button.x + button.w and button.y <= y < button.y + button.h

    def try_move(self, dx: int, dy: int) -> bool:
        if self.can_move(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False

    def hard_drop(self) -> None:
        distance = 0
        while self.try_move(0, 1):
            distance += 1
        self.score += distance * 2
        self.lock_piece()

    def try_rotate(self, direction: int) -> bool:
        next_rotation = (self.current_piece.rotation + direction) % 4
        candidate = ActivePiece(
            kind=self.current_piece.kind,
            x=self.current_piece.x,
            y=self.current_piece.y,
            rotation=next_rotation,
        )
        for dx, dy in WALL_KICKS:
            candidate.x = self.current_piece.x + dx
            candidate.y = self.current_piece.y + dy
            if not self.collides(candidate):
                self.current_piece = ActivePiece(
                    kind=candidate.kind,
                    x=candidate.x,
                    y=candidate.y,
                    rotation=candidate.rotation,
                )
                return True
        return False

    def can_move(self, piece: ActivePiece, dx: int, dy: int) -> bool:
        candidate = ActivePiece(
            kind=piece.kind,
            x=piece.x + dx,
            y=piece.y + dy,
            rotation=piece.rotation,
        )
        return not self.collides(candidate)

    def collides(self, piece: ActivePiece) -> bool:
        for x, y in self.piece_cells(piece):
            if x < 0 or x >= BOARD_WIDTH or y >= BOARD_HEIGHT:
                return True
            if y >= 0 and self.board[y][x]:
                return True
        return False

    def piece_cells(self, piece: ActivePiece):
        for dx, dy in PIECES[piece.kind][piece.rotation]:
            yield piece.x + dx, piece.y + dy

    def lock_piece(self) -> None:
        for x, y in self.piece_cells(self.current_piece):
            if y < 0:
                self.game_over = True
                return
            self.board[y][x] = PIECE_COLORS[self.current_piece.kind]

        cleared = self.clear_lines()
        if cleared:
            self.lines += cleared
            self.score += LINE_SCORES[cleared] * self.level
            self.level = 1 + self.lines // 10

        self.drop_timer = 0
        self.lock_timer = 0
        self.current_piece = self.spawn_piece()

    def clear_lines(self) -> int:
        remaining = [row for row in self.board if any(cell == 0 for cell in row)]
        cleared = BOARD_HEIGHT - len(remaining)
        while len(remaining) < BOARD_HEIGHT:
            remaining.insert(0, [0 for _ in range(BOARD_WIDTH)])
        self.board = remaining
        return cleared

    def draw(self) -> None:
        pyxel.cls(0)
        self.draw_frame()
        self.draw_board()
        self.draw_piece_shadow()
        self.draw_piece(self.current_piece, BOARD_X, BOARD_Y)
        self.draw_side_panel()
        self.draw_touch_controls()

        if self.game_over:
            self.draw_overlay()

    def draw_frame(self) -> None:
        pyxel.rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, 1)
        pyxel.rectb(BOARD_X - 2, BOARD_Y - 2, BOARD_WIDTH * CELL_SIZE + 4, BOARD_HEIGHT * CELL_SIZE + 4, 7)
        pyxel.text(BOARD_X, 3, "TETRIS", 7)
        pyxel.text(SIDE_X, 3, "TOUCH READY", 10)

    def draw_board(self) -> None:
        for y, row in enumerate(self.board):
            for x, color in enumerate(row):
                px = BOARD_X + x * CELL_SIZE
                py = BOARD_Y + y * CELL_SIZE
                pyxel.rect(px, py, CELL_SIZE, CELL_SIZE, 0)
                if color:
                    self.draw_block(px, py, color)
                else:
                    pyxel.rectb(px, py, CELL_SIZE, CELL_SIZE, 1)

    def draw_piece_shadow(self) -> None:
        ghost = ActivePiece(
            kind=self.current_piece.kind,
            x=self.current_piece.x,
            y=self.current_piece.y,
            rotation=self.current_piece.rotation,
        )
        while not self.collides(ghost):
            ghost.y += 1
        ghost.y -= 1
        for x, y in self.piece_cells(ghost):
            if y >= 0:
                px = BOARD_X + x * CELL_SIZE
                py = BOARD_Y + y * CELL_SIZE
                pyxel.rectb(px + 1, py + 1, CELL_SIZE - 2, CELL_SIZE - 2, 13)

    def draw_piece(self, piece: ActivePiece, offset_x: int, offset_y: int) -> None:
        color = PIECE_COLORS[piece.kind]
        for x, y in self.piece_cells(piece):
            if y >= 0:
                self.draw_block(offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, color)

    def draw_preview_piece(self, kind: str, x: int, y: int) -> None:
        color = PIECE_COLORS[kind]
        for dx, dy in PIECES[kind][0]:
            px = x + dx * 5
            py = y + dy * 5
            pyxel.rect(px, py, 5, 5, color)
            pyxel.rectb(px, py, 5, 5, 7)

    def draw_side_panel(self) -> None:
        pyxel.text(SIDE_X, 16, f"SCORE {self.score}", 7)
        pyxel.text(SIDE_X, 28, f"LINES {self.lines}", 7)
        pyxel.text(SIDE_X, 40, f"LEVEL {self.level}", 7)
        pyxel.text(SIDE_X, 56, "NEXT", 10)

        for index, kind in enumerate(self.next_queue):
            self.draw_preview_piece(kind, SIDE_X, 66 + index * 24)

        pyxel.text(SIDE_X, 146, "KEYBOARD:", 6)
        pyxel.text(SIDE_X, 154, "Z/X OR TAP", 6)
        pyxel.text(SIDE_X, 162, "SPACE=HARD", 6)
        pyxel.text(SIDE_X, 170, "R=RESTART", 6)

    def draw_overlay(self) -> None:
        pyxel.rect(28, 70, 150, 44, 0)
        pyxel.rectb(28, 70, 150, 44, 8)
        pyxel.text(73, 82, "GAME OVER", 8)
        pyxel.text(45, 96, "TAP RESTART OR PRESS R", 7)

    def draw_touch_controls(self) -> None:
        pyxel.text(12, 176, "TOUCH CONTROLS", 10)
        for button in TOUCH_BUTTONS:
            border = 7 if self.touch_btn(button.name) else 13
            pyxel.rect(button.x, button.y, button.w, button.h, button.color)
            pyxel.rectb(button.x, button.y, button.w, button.h, border)
            label_x = button.x + max(2, (button.w - len(button.label) * 4) // 2)
            label_y = button.y + 7
            pyxel.text(label_x, label_y, button.label, 7)

    def draw_block(self, px: int, py: int, color: int) -> None:
        pyxel.rect(px, py, CELL_SIZE, CELL_SIZE, color)
        pyxel.line(px, py, px + CELL_SIZE - 1, py, 7)
        pyxel.line(px, py, px, py + CELL_SIZE - 1, 7)
        pyxel.line(px, py + CELL_SIZE - 1, px + CELL_SIZE - 1, py + CELL_SIZE - 1, 1)
        pyxel.line(px + CELL_SIZE - 1, py, px + CELL_SIZE - 1, py + CELL_SIZE - 1, 1)


if __name__ == "__main__":
    TetrisApp()
