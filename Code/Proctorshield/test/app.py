from flask import Flask, render_template,Response
import cv2
 
app = Flask(__name__)
 
 
@app.route("/")
def index():

    from PIL import ImageGrab
    import numpy as np
    import cv2
    from win32api import GetSystemMetrics
    import datetime

    # width = GetSystemMetrics(0)
    # height = GetSystemMetrics(1)

    # time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    # filename = f'{time_stamp}.mp4'
    # fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    # captured_video = cv2.VideoWriter(filename, fourcc, 20.0, (width, height)) 

    # webcam = cv2.VideoCapture(0)

    # while True:
    #     img = ImageGrab.grab(bbox = (0, 0, width, height)) # captures screen
    #     img_np = np.array(img)
    #     img_final = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

    #     _, frame = webcam.read() # webcam capture
    #     frame_h, frame_w, _ = frame.shape
    #     img_final[0:frame_h, 0:frame_w, :] = frame[0:frame_h, 0:frame_w, :]  # overlay webcam on screen
    #     # cv2.imshow('webcam', frame)
    #     cv2.imshow('Capture', img_final)
    #     captured_video.write(img_final)
    #     if cv2.waitKey(10) == ord('q'):
    #         break

    

app = Flask(__name__)

# OpenCV camera capture
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()
        if not success:
            break
        else:
            import audio
            import head_pose
            import detection
            import threading as th

            # Placeholder function to generate fake data for the graph
def generate_fake_data():
    x = np.arange(0, 10, 0.1)
    y = np.sin(x)
    return x, y

# Function to generate camera frames
def generate_frames():
    while True:
        frame = head_pose.get_frame()  # Get frame from head_pose module (replace with actual function)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# Function to update the graph data
def update_graph_data():
    while True:
        # Generate fake data (replace with actual data from detection module)
        x, y = generate_fake_data()
        plt.clf()
        plt.plot(x, y)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Graph Title')
        plt.grid(True)
        plt.savefig('static/graph.png')  # Save the plot as an image
        time.sleep(1)  # Update interval (adjust as needed)

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the video feed
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)




   