# -*- coding: utf-8 -*-
import time
import cv2 as cv

from datetime import datetime
import requests
import base64

# WEBカメラを使って監視カメラを実現するプログラム
# 動体検知、そのときの日付時刻を埋め込んだjpgファイルを保存する


#画像を保存するディレクトリ
img = './img/cam.jpg'

# GASのurl
url = 'https://script.google.com/macros/s/AKfycbzYNih40FB457PgXz206pvkNgMYDKsa9S5COtD0UbW7Tgbk-5KcsOFpw-tMNJtbyWewaw/exec'


#ファイル名は日付時刻を含む文字列とする
#日付時刻のあとに付加するファイル名を指定する
fn_suffix = '.jpg'

# VideoCaptureのインスタンスを作成する。
cap = cv.VideoCapture(0) 

#縦と横の解像度指定
cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

#2値化したときのピクセルの値
DELTA_MAX = 255

#各ドットの変化を検知するしきい値
DOT_TH = 20

#どれくらいの点に変化があったか
#どの程度以上なら記録するか。
MOTHON_FACTOR_TH = 0.01

#比較用のデータを格納
avg = None

# GASの画像アップローダ
def upload(img):
    f = open(img, 'rb')
    b64_img=base64.b64encode(f.read())
    payload = {'timestamp':datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'temperature':motion_factor, 'humidity':0.0, 'pressure':0.0, 'file': b64_img}

    res = requests.post(url, data=payload)
    print(res.text)

if __name__ == '__main__':
    while True:
        ret, frame = cap.read()     # 1フレーム読み込む
        motion_detected = False     # 動きが検出されたかどうかを示すフラグ

        dt_now = datetime.now() #データを取得した時刻

        #ファイル名と、画像中に埋め込む日付時刻
        dt_format_string = dt_now.strftime('%Y-%m-%d %H:%M:%S') 
        f_name = "cam" + fn_suffix


        # モノクロにする
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        #比較用のフレームを取得する
        if avg is None:
            avg = gray.copy().astype("float")
            continue


        # 現在のフレームと移動平均との差を計算
        cv.accumulateWeighted(gray, avg, 0.6)
        frameDelta = cv.absdiff(gray, cv.convertScaleAbs(avg))

        # デルタ画像を閾値処理を行う
        thresh = cv.threshold(frameDelta, DOT_TH, DELTA_MAX, cv.THRESH_BINARY)[1]

        #モーションファクターを計算する。全体としてどれくらいの割合が変化したか。
        motion_factor = thresh.sum() * 1.0 / thresh.size / DELTA_MAX 
        motion_factor_str = '{:.08f}'.format(motion_factor)

        #画像に日付時刻を書き込み
        cv.putText(frame,dt_format_string,(25,50),cv.FONT_HERSHEY_SIMPLEX, 1.5,(0,0,255), 2)
        #画像にmotion_factor値を書き込む
        cv.putText(frame,motion_factor_str,(25,470),cv.FONT_HERSHEY_SIMPLEX, 1.5,(0,0,255), 2)

        #モーションファクターがしきい値を超えていれば動きを検知したことにする
        if motion_factor > MOTHON_FACTOR_TH:
            motion_detected = True

        # 動き検出していれば画像を保存する
        if motion_detected  == True:
            #save
            cv.imwrite(img, frame)
            print("DETECTED:" + f_name)
            upload(img)


        # ここからは画面表示する画像の処理
        # 画像の閾値に輪郭線を入れる
        contours, hierarchy = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        frame = cv.drawContours(frame, contours, -1, (0, 255, 0), 3)


        # 結果の画像を表示する
        cv.imshow('camera', frame)


        # 何かキーが押されるまで待機する
        k = cv.waitKey(1000)  #引数は待ち時間(ms)
        if k == 27: #Esc入力時は終了
            break


    print("Bye!\n")
    # 表示したウィンドウを閉じる
    cap.release()
    cv.destroyAllWindows()