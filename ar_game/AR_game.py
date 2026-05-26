import numpy as np
import pyglet, time, cv2, image_processing
from PIL import Image
import sys, opencv_pyglet
from pathlib import Path
from image_processing import ArucoDetector
from spider_game import SpiderGame
from pyglet.window import key

sys.path.append(str(Path(__file__).resolve().parent.parent))
# for using perspective_transformation extend file path with parent path (to include task 1 dir)

import perspective_transformation.image_extractor as extractor

video_id = 0

if len(sys.argv) > 1:
    video_id = int(sys.argv[1])


cap = cv2.VideoCapture(video_id)

try:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, sys.maxsize)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  sys.maxsize)
    # just use maxsize bc these methods somehow falls back to biggest possible (!) resolution anyway 
except:
    pass # just in case


frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


window = pyglet.window.Window(frame_width, frame_height)

aruco = ArucoDetector()


last_timestamp = time.time()
time_without_board = 0
last_corners = None

game = SpiderGame(window)

batch = pyglet.graphics.Batch()

text_group = pyglet.graphics.Group(order=1)


game.create_lives_text(batch)
game.create_center_text(batch)

processed_frame = None


def transform_frame_with_corners(frame, corners):
    marker_points = []
    for marker in corners:
        points = marker.squeeze()
        marker_points.extend(points)
    marker_points = np.array(marker_points, dtype=np.float32)

    outer_rect = image_processing.get_points_for_outer_rect(marker_points)
    transformed_frame = extractor.perform_warping(
        frame, outer_rect, frame_width, frame_height
    )
    return transformed_frame


@window.event
def on_key_press(symbol, modifiers):
    global game, batch

    if symbol == pyglet.window.key.ESCAPE:
        window.close()
        pyglet.app.exit()
    elif symbol == pyglet.window.key.SPACE and game.has_ended:
        game = SpiderGame(window)
        batch = pyglet.graphics.Batch()
        game.create_lives_text(batch)
        game.create_center_text(batch)
        game.center_text.text = "Show the game board to start!"


def update_game(dt):
    batch, processed_frame

    game.lives_text.text = f"Lives: {game.lives}"

    if game.lives == 0:
        game.end()

    if game.has_ended:
        score = game.get_score_from_runtime()
        if game.player_cheated:
            game.center_text.text = f"You cheated!\n Your score is 0!\n{game.cheating_message}\nSPACE = restart\nESC = close"
        else:
            game.center_text.text = f"Game Over! You died.\n Your score is {score}!\nSPACE = restart\nESC = close"
    if not game.has_ended:
        if not game.is_paused and not game.is_started:
            game.update_countdown(dt)
        if game.is_paused and game.is_started:
            game.center_text.text = "Game paused! Show board to resume!"

        if not game.is_paused and game.is_started:
            game.center_text.text = ""
            game.run_time += dt
            if game.run_time > game.last_spawn + game.spawn_interval:
                game.create_spider(batch)
                game.last_spawn = game.run_time
                game.increase_game_speed()
            game.move_spiders(dt)
            game.check_spiders_reach_end()
            if processed_frame is not None:
                game.destroy_hit_spiders(processed_frame)
                if game.cheating_detection_running:
                    game.check_for_cheating_hand_mid(processed_frame)
                    game.check_for_cheating_too_much_hand(processed_frame)


@window.event
def on_draw():
    global time_without_board, last_timestamp, last_corners, processed_frame

    window.clear()

    ret, cv_frame = cap.read()

    corners, ids, rejectedImgPoints = aruco.get_markers(cv_frame)

    transformed_frame = None

    if len(corners) == 4:
        game.resume()
        time_without_board = 0
        last_timestamp = time.time()
        last_corners = corners

        transformed_frame = transform_frame_with_corners(cv_frame, corners)
        game.cheating_detection_running = True

    else:
        time_without_board += time.time() - last_timestamp
        last_timestamp = time.time()
        if last_corners is not None and time_without_board < 0.5:
            game.cheating_detection_running = False
            transformed_frame = transform_frame_with_corners(cv_frame, last_corners)
        else:
            # pause game and wait for board
            last_corners = None
            transformed_frame = None
            game.pause()

    img = None

    if transformed_frame is not None:
        transformed_frame = cv2.flip(transformed_frame, 1)
        # flip for more intuitve game
        img = opencv_pyglet.cv2glet(transformed_frame, "BGR")
    else:
        cv_frame = cv2.flip(cv_frame, 1)
        img = opencv_pyglet.cv2glet(cv_frame, "BGR")

    if transformed_frame is not None:
        processed_frame = image_processing.process_frame(
            transformed_frame, show_result=False
        )

    img.blit(0, 0, 0)

    batch.draw()


pyglet.clock.schedule_interval(update_game, 0.01)  # 100 fps

pyglet.app.run()
