from flask import Flask, render_template, Response, jsonify, request, session, redirect,url_for
from flask_mail import Mail, Message
import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
from datetime import datetime
import pywhatkit

app = Flask(__name__)
app.secret_key = 'supersecretkey'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'electronico4208978@gmail.com'
app.config['MAIL_PASSWORD'] = 'aoym rhqf jkxy splu'
mail = Mail(app)

# Variables globales
fatigue_detected = False
fatigue_alerts = []

def eye_aspect_ratio(eye_points):
    eye = np.array([(point.x, point.y) for point in eye_points])
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def calibrate_ear(detector, predictor):
    cap = cv2.VideoCapture(0)
    ear_values = []
    try:
        for _ in range(30):
            ret, frame = cap.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
            if faces:
                face = faces[0]
                shape = predictor(gray, face)
                left_eye = shape.parts()[42:48]
                right_eye = shape.parts()[36:42]
                left_ear = eye_aspect_ratio(left_eye)
                right_ear = eye_aspect_ratio(right_eye)
                ear = (left_ear + right_ear) / 2.0
                ear_values.append(ear)
            else:
                print("Ningún rostro detectado, ajuste su posición.")
    finally:
        cap.release()

    if ear_values:
        calibrated_ear = sum(ear_values) / len(ear_values)
        return calibrated_ear * 0.9
    else:
        return 0.3  # Valor predeterminado si la calibración falla

def gen_frames(detector, predictor, EAR_THRESHOLD):
    global fatigue_detected
    global fatigue_alerts
    cap = cv2.VideoCapture(0)
    frames_with_eyes_closed = 0
    FRAMES_FOR_FATIGUE_ALERT = 20
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        for face in faces:
            shape = predictor(gray, face)
            for part in shape.parts():
                cv2.circle(frame, (part.x, part.y), 2, (0, 255, 0), -1)

            left_eye = shape.parts()[42:48]
            right_eye = shape.parts()[36:42]
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            ear = (left_ear + right_ear) / 2.0

            if ear < EAR_THRESHOLD:
                frames_with_eyes_closed += 1
                if frames_with_eyes_closed >= FRAMES_FOR_FATIGUE_ALERT:
                    if not fatigue_detected:
                        cv2.putText(frame, "FATIGA DETECTADA", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        fatigue_detected = True
                        fatigue_alerts.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            else:
                frames_with_eyes_closed = 0
                fatigue_detected = False

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/check_fatigue')
def check_fatigue():
    global fatigue_detected
    result = {'isFatigued': fatigue_detected}
    fatigue_detected = False  # Reset the fatigue detection after checking
    return jsonify(result)

def send_fatigue_report():
    global fatigue_alerts
    user_email = session.get('user_email')
    if user_email:
        msg = Message("Reporte de Fatigas del Día",
                      sender="electronico4208978@gmail.com",
                      recipients=[user_email])
        msg.html = render_template('reporte_fatiga.html', total_fatigas=len(fatigue_alerts), alertas=fatigue_alerts)
        mail.send(msg)
        fatigue_alerts = []  # Reset the list after sending the report
        
@app.route('/stop_video', methods=['POST'])
def stop_video():
    send_fatigue_report()
    # send_fatigue_whatsapp(fatigue_alerts)
    return jsonify({'message': 'Video detenido y reporte enviado.'})


@app.route('/video_feed')
def video_feed():
    detector = dlib.get_frontal_face_detector()
    predictor_path = "shape_predictor_68_face_landmarks.dat"
    predictor = dlib.shape_predictor(predictor_path)
    EAR_THRESHOLD = calibrate_ear(detector, predictor)
    return Response(gen_frames(detector, predictor, EAR_THRESHOLD), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/principal')
def principal():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    user_email = request.form['email']
    session['user_email'] = user_email
    return redirect(url_for('principal'))

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('index'))



# def send_fatigue_whatsapp(alerts):
#     message = "Reporte de Fatigas del Día:\n" + "\n".join(alerts)
#     now = datetime.now()
#     hour = now.hour
#     minute = now.minute + 2  # Asegúrate de dar suficiente tiempo para evitar errores

#     # Envía el mensaje
#     pywhatkit.sendwhatmsg("+51923505083", message, hour, minute)


if __name__ == '__main__':
    app.run(debug=True, threaded=True, use_reloader=False)
