### check webcam resolution
### $ v4l2-ctl -d /dev/video0 --list-formats-ext

import cv2
import time
import os
from datetime import datetime


GREEN = (0, 255, 0)
GRAY = (75, 75, 75)
RED = (0, 0, 255)
BLACK = (0, 0, 0)
default_color = GRAY

isRecording = False
break_flag = False
MAX_REC_TIME = 60*30 # [sec]

DATA_DIR = "Recordings"
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

DEVICE_ID = 0
WIDTH, HEIGHT = (848, 480)
#WIDTH, HEIGHT = (640, 400)
FPS = 20
cap = cv2.VideoCapture(DEVICE_ID)

# フォーマット・解像度・FPSの設定
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cap.set(cv2.CAP_PROP_FPS, FPS)

# フォーマット・解像度・FPSの取得
#fourcc = decode_fourcc(cap.get(cv2.CAP_PROP_FOURCC))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
print(f"width={width}, height={height}, fps={fps}")

rec_button_area = {"top":int(height*0.02), "bottom":int(height*0.17), 
                   "left":int(width*0.87),"right":int(width*0.99)}

quit_button_area = {"top":int(height*0.20), "bottom":int(height*0.35), 
                   "left":int(width*0.87),"right":int(width*0.99)}

FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
LINE_TYPE=cv2.LINE_AA
FONT_SCALE = 1

TEXTS = ["Quit", "Rec", "Stop"]
text_size_dict = {}
for text in TEXTS:
    (w, h), baseline = cv2.getTextSize(text=text, fontFace=FONT_FACE, fontScale=FONT_SCALE, thickness=1)
    text_size_dict[text] = {"w":w, "h":h, "baseline":baseline}

print(text_size_dict)

def mouse_event(event, x, y, flags, param):
	global break_flag, isRecording
	if event == cv2.EVENT_LBUTTONUP:
		# if Quit button is pressed
		if (quit_button_area["top"] < y < quit_button_area["bottom"]) and \
			(quit_button_area["left"] < x < quit_button_area["right"]) and not(isRecording):
			print("quit")
			break_flag = True
		
		# if Rec button is pressed
		if (rec_button_area["top"] < y < rec_button_area["bottom"]) and \
			(rec_button_area["left"] < x < rec_button_area["right"]):
			isRecording = not(isRecording)
			print("rec pressed", isRecording)

cv2.namedWindow("camera", cv2.WINDOW_NORMAL)
# cv2.setWindowProperty('camera', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.setMouseCallback("camera", mouse_event)


def main():
	global isRecording, break_flag
	isRecordingOld = isRecording
	rec_time = 0
	old_t = time.time()

	if cap.isOpened():
		try:
			while True:

				new_t = time.time()
				dt = new_t - old_t
				old_t = new_t
				print(f"fps={1/dt:.1f}")

				ret, img = cap.read()
				frame = img.copy()

				#----- draw rec button -----#
				if isRecording:
					rec_button_color = RED
					rec_button_text = "Stop"
				else:
					rec_button_color = GRAY
					rec_button_text = "Rec"

				cv2.rectangle(frame,
					(rec_button_area["left"], rec_button_area["top"]),
					(rec_button_area["right"], rec_button_area["bottom"]),
					color=rec_button_color, thickness=1, lineType=cv2.LINE_AA)
				cv2.putText(frame, rec_button_text,
					(int((rec_button_area["left"]+(rec_button_area["right"])-text_size_dict[rec_button_text]["w"])/2),
					int((rec_button_area["bottom"]+(rec_button_area["top"])+text_size_dict[rec_button_text]["h"])/2)),  
					fontFace=FONT_FACE, fontScale=FONT_SCALE, color=rec_button_color, thickness=1, lineType=LINE_TYPE)
				#---------------------------#

				#----- draw quit button -----#
				if not isRecording:
					cv2.rectangle(frame,
						(quit_button_area["left"], quit_button_area["top"]),
						(quit_button_area["right"], quit_button_area["bottom"]),
						color=default_color, thickness=1, lineType=cv2.LINE_AA)
					cv2.putText(frame, "Quit",
						(int((quit_button_area["left"]+(quit_button_area["right"])-text_size_dict["Quit"]["w"])/2),
						int((quit_button_area["bottom"]+(quit_button_area["top"])+text_size_dict["Quit"]["h"])/2)),  
						fontFace=FONT_FACE, fontScale=FONT_SCALE, color=default_color, thickness=1, lineType=LINE_TYPE)
				#----------------------------#
				
				

				if (isRecordingOld == False) and (isRecording == True):
					filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".mp4"
					filepath = os.path.join(DATA_DIR, filename)
					print(f"start recording! {filepath}")
					#writer = cv2.VideoWriter(filepath, cv2.VideoWriter_fourcc(*'DIVX'), fps, (width, height))
					writer = cv2.VideoWriter(filepath, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
					rec_start_time = time.time()

				if (isRecordingOld == True) and (isRecording == True):
					#print("now recording ....")
					rec_time = time.time() - rec_start_time
					cv2.putText(frame, f"Recording... {rec_time:.1f}",(int(width*0.02), int(height*0.1)),  
					fontFace=FONT_FACE, fontScale=FONT_SCALE, color=RED, thickness=1, lineType=LINE_TYPE)
					writer.write(img)
		
				if (isRecordingOld == True) and (isRecording == False):
					print("stop recording")
					writer.release()
					rec_time = 0

				isRecordingOld = isRecording

				cv2.imshow("camera", frame)

				if rec_time > MAX_REC_TIME:
					isRecording = False
		
				# break
				k = cv2.waitKey(1)
				if k == 27 or k == ord('q'): break
				if break_flag: break

		finally:
			cap.release()
			cv2.destroyAllWindows()

	else:
		print("Error: Unable to open camera")

	cap.release()

if __name__ == "__main__":
	main()
