import random, math, pyglet, os, cv2
import numpy as np
from pyglet import image
import opencv_pyglet


class SpiderGame:
    def __init__(self, window):
        self.window = window
        self.is_paused = False
        self.is_started = False
        self.has_ended = False
        self.spiders = []
        self.lives = 5
        self.spawn_interval = 1
        self.last_spawn = 0
        self.run_time = 0
        self.current_spider_img = 1
        self.speed_divisor = 12
        self.player_cheated = False
        self.cheating_message = ""
        self.cheating_detection_running = False
        self.countdown_time = 0
        self.center_text = None
        self.lives_text = None

    def start(self):
        self.is_started = True
        self.cheating_detection_running = True

    def pause(self):
        self.is_paused = True
        self.cheating_detection_running = False

    def resume(self):
        self.is_paused = False
        self.cheating_detection_running = True

    def end(self):
        self.has_ended = True
        self.cheating_detection_running = False

    def get_score_from_runtime(self):
        return int(self.run_time)

    def update_countdown(self, dt):
        self.countdown_time += dt

        if self.countdown_time < 1:
            self.center_text.text = "3"
        elif self.countdown_time < 2:
            self.center_text.text = "2"
        elif self.countdown_time < 3:
            self.center_text.text = "1"
        elif self.countdown_time < 4:
            self.center_text.text = "Start!"
        else:
            self.start()
            self.countdown_time = 0
            self.center_text.text = ""

    def create_center_text(self, batch):
        self.center_text = pyglet.text.Label(
            "Show the game board to start!",
            font_name="Arial",
            font_size=72,
            multiline=True,
            x=self.window.width // 2,
            y=self.window.height // 2,
            batch=batch,
            anchor_x="center",
            anchor_y="center",
            width=self.window.width // 1.25,
            color=(200, 0, 0),
            align="center",
        )

    def create_lives_text(self, batch):
        self.lives_text = pyglet.text.Label(
            "Lives: 5",
            font_name="Arial",
            font_size=60,
            x=20,
            y=self.window.height - 20,
            anchor_x="left",
            anchor_y="top",
            batch=batch,
            color=(200, 0, 0),
        )

    def create_spider(self, batch):
        SPIDER_PATH = f".{os.sep}assets{os.sep}spider0{self.current_spider_img}.png"
        # spiders by Stephen "Redshrike" Challener (graphic artist)
        # and William.Thompsonj (contributor)
        # from https://opengameart.org/content/lpc-spider
        SPIDER_SIZE = self.window.height // 10

        x = self.window.width + SPIDER_SIZE
        y = math.floor(random.random() * 9 * SPIDER_SIZE)

        spider_image = image.load(SPIDER_PATH)

        spider = pyglet.sprite.Sprite(spider_image, x=x, y=y, batch=batch)
        spider.width, spider.height = SPIDER_SIZE, SPIDER_SIZE
        self.spiders.append(spider)

        if self.current_spider_img == 3:
            self.current_spider_img = 1
        else:
            self.current_spider_img += 1
        return spider

    def increase_game_speed(self):
        MIN_DIVISOR = 4
        SPEED_STEP = 0.05
        if self.speed_divisor > MIN_DIVISOR:
            self.speed_divisor -= SPEED_STEP

        MIN_INTERVAL = 0.25
        SPAWN_STEP = 0.005
        if self.spawn_interval > MIN_INTERVAL:
            self.spawn_interval -= SPAWN_STEP

    def move_spiders(self, dt):
        for spider in self.spiders:
            spider.x -= (self.window.width // self.speed_divisor) * dt

    def check_spiders_reach_end(self):
        for spider in self.spiders:
            if spider.x < 0:  # 0 = window left side
                self.lives -= 1
                self.spiders.remove(spider)
                break  # break bc only 1 at a time reaches end due to spawn interval

    def destroy_hit_spiders(self, processed_frame):
        HIT_THRESHOLD = 0.0125
        
        for spider in self.spiders[:]:
            # only do stuff if spider is in frame
            if spider.x <= self.window.width // 3:
                # only in left third (only 1/4 of space on left is allowed anyway)
                spider_cv_x, spider_cv_y = opencv_pyglet.convert_pyglet_to_cv_coords(
                    self.window.height, int(spider.x), int(spider.y)
                )

                spider_frame_cropped = processed_frame[
                    spider_cv_y : spider_cv_y + spider.height,
                    spider_cv_x : spider_cv_x + spider.width,
                ]

                black_pixels = np.count_nonzero(spider_frame_cropped == 0)
                ratio = black_pixels / spider_frame_cropped.size

                if ratio > HIT_THRESHOLD:
                    self.spiders.remove(spider)
                    spider.delete()

    def end_game_after_cheating(self, cheating_message):
        if self.cheating_detection_running:
            self.end()
            self.player_cheated = True
            self.cheating_message = cheating_message

    def check_for_cheating_hand_mid(self, processed_frame):
        border_offset_y = self.window.height // 8
        border_offset_x = self.window.width // 4
        img_cropped = processed_frame[
            border_offset_y:-border_offset_y, border_offset_x:-border_offset_x
        ]

        black_pixels = np.sum(img_cropped == 0)

        ratio = black_pixels / img_cropped.size

        GRACE_THRESHOLD = 0.01

        if ratio > GRACE_THRESHOLD:
            cheating_message = "You can't put your hand in the middle!"
            self.end_game_after_cheating(cheating_message)

    def check_for_cheating_too_much_hand(self, processed_frame):
        # mostly relevant for smaller resolution but hand in middle is better cheating detection
        # view cases where this is relevant bc u prbobaly hit middle earlier anyway

        black_pixels = np.sum(processed_frame == 0)
        ratio = black_pixels / processed_frame.size

        HAND_THRESHOLD = 0.35

        if ratio > HAND_THRESHOLD:
            cheating_message = "You can't use this much of your hand!"
            self.end_game_after_cheating(cheating_message)
