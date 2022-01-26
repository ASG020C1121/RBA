import cv2
from datetime import datetime
import schedule
import time
import base64
import requests
from PIL import Image 
import imagehash
import threading

img = './img/cam.jpg'

url = 'https://script.google.com/macros/s/AKfycby4JdB9hbkZLhTUx6T5lvFnUj7RR0mpktNHzJvoHw1tDSTW8uMQhkYJ_xYK_jg3rvA3/exec'

deviceid=0 # it depends on the order of USB connection. 
cap = cv2.VideoCapture(deviceid)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def upload(img):
    f = open(img, 'rb')
    b64_img=base64.b64encode(f.read())
    payload = {'timestamp':datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'temperature':stay, 'humidity':0.0, 'pressure':0.0, 'file': b64_img}

    res = requests.post(url, data=payload)

def job():
    ret, frame = cap.read()
    fname="cam.jpg"
    cv2.imwrite(img, frame) 
    print(fname + " is created.")

    # 基本画像と動体画像の比較
    hash = imagehash.average_hash(Image.open('./img2/default.jpg')) 

    otherhash = imagehash.average_hash(Image.open('./img/cam.jpg')) 

    print(hash - otherhash)

    global stay
    stay = hash - otherhash

    if stay <= 5:
        stay = 0
    else:
        pass

    upload(img)

#do job every 10 seconds
schedule.every(1/6).minutes.do(job)

# 基本となる画像の保存
while True:
    ret, frame = cap.read()
    cv2.imshow("camera", frame)

    k = cv2.waitKey(1)&0xff # キー入力を待つ
    if k == ord('p'):
        # 「p」キーで画像を保存
        path = "./img2/" + "default.jpg"
        cv2.imwrite(path, frame) # ファイル保存

    elif k == ord('q'):
        # 「q」キーが押されたら終了する
        break

while True:
    schedule.run_pending()
    time.sleep(1)

    ret, frame = cap.read()
    cv2.imshow("camera", frame)

    # 何かキーが押されるまで待機する
    k = cv2.waitKey(1000)  #引数は待ち時間(ms)
    if k == 27: #Esc入力時は終了
        break