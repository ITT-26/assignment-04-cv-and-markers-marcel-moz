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
        self.SPAWN_INTERVAL = 1
        self.last_spawn = 0
        self.run_time = 0
        self.current_spider_img = 1
        self.speed_divisor  = 10
        self.player_cheated = False
        self.cheating_message = ""
        self.cheating_detection_running = False

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
    
    def increase_movement_speed(self):
        if self.speed_divisor > 4:
            self.speed_divisor -= 0.05

    def move_spiders(self, dt):
        for spider in self.spiders:
            spider.x -=  (self.window.width // self.speed_divisor) * dt

    def check_spiders_reach_end(self):
        for spider in self.spiders:
            if spider.x < 0:  # 0 = window left side
                self.lives -= 1
                self.spiders.remove(spider)
                break  # break bc only 1 at a time reaches end due to spawn interval

    def destroy_hit_spiders(self, processed_frame):
        
        for spider in self.spiders.copy():
            spider_cv_x, spider_cv_y = opencv_pyglet.convert_pyglet_to_cv_coords(
                self.window.height, int(spider.x), int(spider.y)
            )

            spider_frame_cropped = processed_frame[
                spider_cv_y : spider_cv_y + spider.height,
                spider_cv_x : spider_cv_x + spider.width
            ]
            
            black_pixels = np.sum(spider_frame_cropped == 0)
            ratio = black_pixels / spider_frame_cropped.size
            
            
            HIT_THRESHOLD = 0.01
            
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
        img_cropped = processed_frame[border_offset_y:-border_offset_y, border_offset_x:-border_offset_x]

        black_pixels = np.sum(img_cropped == 0)

        ratio = black_pixels / img_cropped.size

        GRACE_THRESHOLD = 0.01

        if ratio > GRACE_THRESHOLD:
            cheating_message = "You can't put your hand in the middle!"
            self.end_game_after_cheating(cheating_message)
            
        

    def check_for_cheating_too_much_hand(self, processed_frame):
        black_pixels = np.sum(processed_frame == 0)
        ratio = black_pixels / processed_frame.size
        THRESHOLD = 0.05
        if ratio > THRESHOLD:
            cheating_message = "You can't use this much of your hand!"
            self.end_game_after_cheating(cheating_message)
