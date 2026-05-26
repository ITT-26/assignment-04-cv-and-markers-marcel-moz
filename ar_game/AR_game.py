import cv2
import numpy as np
import pyglet, time
from PIL import Image
import sys, opencv_pyglet
from pathlib import Path
from image_processing import ArucoDetector
import image_processing
from spider_game import SpiderGame
from pyglet.window import key

sys.path.append(str(Path(__file__).resolve().parent.parent))
# for using perspective_transformation extend file path with parent path (to include task 1 dir)

import perspective_transformation.image_extractor as extractor

video_id = 0

if len(sys.argv) > 1:
    video_id = int(sys.argv[1])


cap = cv2.VideoCapture(video_id)

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


window = pyglet.window.Window(frame_width, frame_height)

aruco = ArucoDetector()


def get_points_for_outer_rect(points):
    sum = np.sum(points, axis=1)
    diff = np.diff(points, axis=1)

    top_left = points[np.argmin(sum)]
    top_right = points[np.argmin(diff)]
    bottom_right = points[np.argmax(sum)]
    bottom_left = points[np.argmax(diff)]

    return np.float32(np.array([top_left, top_right, bottom_right, bottom_left]))


def transform_frame_with_corners(frame, corners):
    marker_points = []
    for marker in corners:
        points = marker.squeeze()
        marker_points.extend(points)
    marker_points = np.array(marker_points, dtype=np.float32)

    outer_rect = get_points_for_outer_rect(marker_points)
    transformed_frame = extractor.perform_warping(
        frame, outer_rect, frame_width, frame_height
    )
    return transformed_frame


def create_lives_text(batch, text_group):
    return pyglet.text.Label(
        "Lives: 5",
        font_name="Arial",
        font_size=28,
        x=20,
        y=window.height - 20,
        anchor_x="left",
        anchor_y="top",
        batch=batch,
        group=text_group,
        color=(200, 0, 0),
    )


def create_center_text(batch):
    center_text = pyglet.text.Label(
        "Show the game board to start!",
        font_name="Arial",
        font_size=28,
        multiline=True,
        x=window.width // 2,
        y=window.height // 2,
        batch=batch,
        anchor_x="center",
        anchor_y="center",
        width=window.width // 1.25,
        color=(200, 0, 0),
        align="center",
    )
    return center_text


last_timestamp = time.time()
time_without_board = 0
last_corners = None

game = SpiderGame(window)

batch = pyglet.graphics.Batch()

text_group = pyglet.graphics.Group(order=1)


lives_text = create_lives_text(batch, text_group)
center_text = create_center_text(batch)
processed_frame = None


@window.event
def on_key_press(symbol, modifiers):
    global game, center_text

    if symbol == pyglet.window.key.ESCAPE:
        window.close()
        pyglet.app.exit()
    elif symbol == pyglet.window.key.SPACE and game.has_ended:
        game = SpiderGame(window)
        center_text.text = "Show the game board to start!"


def update_game(dt):
    global center_text, batch, processed_frame

    lives_text.text = f"Lives: {game.lives}"

    if game.lives == 0:
        game.end()

    if game.has_ended:
        score = game.get_score_from_runtime()
        if game.player_cheated:
            center_text.text = f"You cheated!\n Your score is 0!\n{game.cheating_message}\nSPACE = restart\nESC = close"
        else:
            center_text.text = f"Game Over! You died.\n Your score is {score}!\nSPACE = restart\nESC = close"
    if not game.has_ended:
        if not game.is_paused and not game.is_started:
            game.run_time += dt
            if game.run_time <= 1:
                center_text.text = "3"
            elif game.run_time <= 2:
                center_text.text = "2"
            elif game.run_time <= 3:
                center_text.text = "1"
            elif game.run_time <= 4:
                center_text.text = "Start!"
            else:
                game.start()
                game.run_time = 0
                center_text.text = ""

        if game.is_paused and game.is_started:
            center_text.text = "Game paused! Show board to resume!"

        if not game.is_paused and game.is_started:
            center_text.text = ""
            game.run_time += dt
            if game.run_time > game.last_spawn + game.SPAWN_INTERVAL:
                game.create_spider(batch)
                game.last_spawn = game.run_time
                game.increase_movement_speed()
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
        processed_frame = image_processing.process_frame(transformed_frame, show_result=False)

    img.blit(0, 0, 0)

    batch.draw()


pyglet.clock.schedule_interval(update_game, 0.02)  # 50 fps

pyglet.app.run()
