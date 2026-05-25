import cv2
from pathlib import Path
import argparse
import numpy as np


def mouse_callback(event, x, y, flags, param):
    global img
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(marker_positions) < 4:
            img = cv2.circle(img, (x, y), 5, (255, 0, 0), -1)
            marker_positions.append([x, y])
        elif len(marker_positions) == 4:
            error_msg = "You can only place 4 markers. Discard markers with ESC for new selection."
            cv2.putText(
                img, error_msg, (40, 40), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 0, 255)
            )


def discard_markers():
    global img, warped_img
    
    marker_positions.clear()
    img = og_img.copy()
    warped_img = None


def show_success_msg_saving(warped_img, file_path):
    msg = f"Image saved to {file_path}"
    cv2.putText(warped_img, msg, (20, 20), cv2.FONT_HERSHEY_TRIPLEX, 0.4, (0, 175, 0))


def get_result_file_with_version():
    global result_file_name, version_counter
    
    while (output_directory / result_file_name).exists():

        result_file_name = Path(
            result_stem_without_version + str(version_counter) + result_file_name.suffix
        )
        version_counter += 1
    return output_directory / result_file_name


def save_image(warped_img):
    output_directory.mkdir(exist_ok=True)
    final_file_name = get_result_file_with_version()
    cv2.imwrite(str(final_file_name), warped_img)
    show_success_msg_saving(warped_img, str(final_file_name))


def sort_markers(markers):
    sorted_markers = markers.copy()

    # x + y für jeden punktF
    sum = np.sum(markers, axis=1)
    # x -y für jeden punkt
    diff = np.diff(markers, axis=1)  # axis = horizontal

    sorted_markers[0] = markers[np.argmin(sum)]  # top-left
    sorted_markers[1] = markers[np.argmin(diff)]  # top-right
    sorted_markers[2] = markers[np.argmax(sum)]  # bottom-right
    sorted_markers[3] = markers[np.argmax(diff)]  # bottom-left
    # order like in exercise notebook

    return sorted_markers


def get_vector_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def get_warped_image(img, sorted_markers, target_width, target_height):

    target_top_left = [0, 0]
    traget_top_right = [target_width, 0]
    traget_bottom_right = [target_width, target_height]
    traget_bottom_left = [0, target_height]

    target = np.float32(
        np.array(
            [target_top_left, traget_top_right, traget_bottom_right, traget_bottom_left]
        )
    )

    mat = cv2.getPerspectiveTransform(sorted_markers, target)
    warped = cv2.warpPerspective(img, mat, (target_width, target_height))

    return warped


def perform_warping(img, markers):
    sorted_markers = np.float32(sort_markers(markers))
    return get_warped_image(img, sorted_markers, target_width, target_height)


def main():
    # ArgumentParser Code from ChatGPT after intial version working with position of arguments only (without ArgumentParser)
    global version_counter, result_stem_without_version, result_file_name, output_directory
    global img, warped_img
    global target_width, target_height
    global img, og_img, marker_positions
    
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", default="sample_image.jpg", help="input image path")
    parser.add_argument("--outdir", default="extracted", help="output directory")
    parser.add_argument("--name", default=None, help="output file name (optional)")
    parser.add_argument(
        "--out_width", type=int, required=True, help="output image width (required)"
    )
    parser.add_argument(
        "--out_height", type=int, required=True, help="output image height (required)"
    )

    args = parser.parse_args()

    input_file = Path(args.input)
    og_img = cv2.imread(str(input_file))

    if og_img is None:
        print(f"Error reading file: {input_file}. Try again with another file.")
        exit()

    output_directory = Path(args.outdir)

    if args.name:
        result_file_name = Path(args.name).with_suffix(input_file.suffix)
    else:
        result_file_name = Path(f"{input_file.stem}_extracted{input_file.suffix}")

    target_width = args.out_width
    target_height = args.out_height

    # until here altered by ChatGPT

    version_counter = 1
    result_stem_without_version = result_file_name.stem
    img = og_img.copy()
    warped_img = None

    marker_positions = []

    result_saved = False

    PREVIEW_WINDOW_NAME = "Preview Window"
    RESULT_WINDOW_NAME = "Result Window"

    cv2.namedWindow(PREVIEW_WINDOW_NAME)

    cv2.setMouseCallback(PREVIEW_WINDOW_NAME, mouse_callback)

    while True:

        cv2.imshow(PREVIEW_WINDOW_NAME, img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        elif key == 27:  # 27 == ESCAPE key
            discard_markers()
            result_saved = False
            try:
                cv2.destroyWindow(RESULT_WINDOW_NAME)
            except:
                pass
            # close result window (if open)

        if len(marker_positions) == 4:
            if warped_img is None:
                warped_img = perform_warping(og_img.copy(), np.array(marker_positions))
                # hier image warp

            cv2.namedWindow(RESULT_WINDOW_NAME)
            cv2.imshow(RESULT_WINDOW_NAME, warped_img)

            if key == ord("s") and not result_saved:
                save_image(warped_img)
                result_saved = True


if __name__ == "__main__":
    main()
