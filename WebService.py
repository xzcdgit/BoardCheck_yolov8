# 该模块用于搭建web端，供外部通过网页查看标记的图像流


from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import base64
import cv2
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['web_img_ratio'] = 0.5
socketio = SocketIO(app)
img_info = None
text_info = None

@app.route('/')
def index():
    comment = request.args.get("resize")
    if comment is not None:
        try:
            ratio = float(comment)
            if ratio >= 0.1 and ratio <= 1:
                app.config['web_img_ratio'] = ratio
                print("resize={}".format(ratio))
        except ValueError as e:
            print(e)

    return render_template('index.html')

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

def update_content():
    while True:
        # 更新文本
        #if text_info is None:
        text = f"当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        #else:
        #    text = f"当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n    val_p: {text_info['person_num']} val_l: {text_info['arclight_num']} sum_p: {text_info['person_count_num']} sum_l: {text_info['arclight_count_num']} min_d:{str(int(text_info['min_distance']))}"
        socketio.emit('update_text', {'data': text})
        # 更新图片
        if img_info is None:
            time.sleep(1)
            continue
        else:
            img = img_info[0]
            img = cv2.resize(img, dsize=None, fx=app.config['web_img_ratio'], fy=app.config['web_img_ratio'], interpolation=cv2.INTER_LINEAR)
            encoded_image = cv2_to_base64(img)
            socketio.emit('update_image', {'data': encoded_image})
        time.sleep(0.04)

def cv2_to_base64(image):
    # 将 cv2 图像转换为 base64 编码
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

def main(host:str='127.0.0.1',port:int=5000):
    socketio.start_background_task(update_content)
    socketio.run(app, host, port, debug=False)


if __name__ == '__main__':
    socketio.start_background_task(update_content)
    socketio.run(app, debug=False)