import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist

def eye_aspect_ratio(eye_points):
    eye = np.array([(point.x, point.y) for point in eye_points])
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def calibrate_ear(cap, detector, predictor):
    print("Calibración iniciada. Por favor, mire directamente a la cámara con los ojos abiertos.")
    ear_values = []
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
    if ear_values:
        calibrated_ear = sum(ear_values) / len(ear_values)
        print(f"Calibración completa. EAR promedio calculado: {calibrated_ear}")
        return calibrated_ear * 0.9
    else:
        print("No se pudieron capturar suficientes datos para la calibración. Usando valor predeterminado.")
        return 0.3

def main():
    cap = cv2.VideoCapture(0)
    detector = dlib.get_frontal_face_detector()
    predictor_path = "shape_predictor_68_face_landmarks.dat"
    predictor = dlib.shape_predictor(predictor_path)
    EAR_THRESHOLD = calibrate_ear(cap, detector, predictor)
    
    frames_with_eyes_closed = 0
    FRAMES_FOR_FATIGUE_ALERT = 20
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar el video.")
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
                    cv2.putText(frame, "FATIGA DETECTADA", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                frames_with_eyes_closed = 0

        cv2.imshow('Video en Vivo con Detección Facial y Fatiga', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
