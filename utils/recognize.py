import os
import numpy as np
import pickle
import cv2 as cv
from django.conf import settings


def Recognizer(status=None):
    file_path = os.path.join(settings.BASE_DIR, "train")
    label_encoding = pickle.loads(open(file_path+'/'+'le.pickle', 'rb').read())
    recognizer = pickle.loads(open(file_path+'/'+'recognizer.pickle', 'rb').read())

    # -- function Response
    res = {}
    # -- Loading Face Detection Model
    face_detector = cv.dnn.readNetFromCaffe(prototxt=settings.PROTO_PATH, caffeModel=settings.CAFFE_MODEL_PATH)

    # -- Loading face recognition Model
    face_recognizer = cv.dnn.readNetFromTorch(model=settings.RECOGNITION_MODEL)

    cap = cv.VideoCapture(0)
    found = False
    if cap.isOpened():
        while True:
            _, frame = cap.read()
            frame = cv.resize(frame, (600, 400))
            (h, w) = frame.shape[:2]
            try:
                image_blob = cv.dnn.blobFromImage(cv.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0), False)
            except cv.error as e:
                print(str(e))
            face_detector.setInput(image_blob)
            face_detections = face_detector.forward()

            for i in range(0, face_detections.shape[2]):
                confidence = face_detections[0, 0, i, 2]
                if confidence >= 0.5:
                    box = face_detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    face = frame[startX:endY, startX:endX]
                    (fh, fw) = face.shape[:2]
                    try:
                        face_blob = cv.dnn.blobFromImage(face, 1.0/255, (96, 96), (0, 0), True, False)
                        # print(face_blob)
                    except cv.error as e:
                        print(e)

                    face_recognizer.setInput(face_blob)
                    vector = face_recognizer.forward()

                    predictions = recognizer.predict_proba(vector)[0]
                    j = np.argmax(predictions)
                    probability = predictions[j]

                    name = label_encoding.classes_[j]

                    if name != 'unknown':
                        text = "{}: {:.2f}".format(name, probability * 100)
                        y = startY - 10 if startY - 10 > 10 else startY + 10
                        cv.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
                        cv.putText(frame, text, (startX, y), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255) ,1)
                        found = True
                    else:
                        text = "{}: {:.2f}".format("unknown", probability * 100)
                        y = startY - 10 if startY - 10 > 10 else startY + 10
                        cv.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
                        cv.putText(frame, text, (startX, y), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                        found = False

            if found:
                res['found'] = True
                res['status'] = 11
                res['username'] = name
                if status == 'in':
                    cv.putText(frame, "press m to mark your attendance", (20, 20), cv.FONT_HERSHEY_SIMPLEX, 0.65,
                               (255, 0, 0), 1)
                if status == 'out':
                    cv.putText(frame, "press o to mark out your attendance", (20, 20), cv.FONT_HERSHEY_SIMPLEX, 0.65,
                               (255, 0, 0), 1)
            else:
                cv.putText(frame, "press q to exit", (20, 20), cv.FONT_HERSHEY_SIMPLEX, 0.65,
                           (0, 255, 0), 1)

            key = cv.waitKey(50) & 0xff

            if status == 'in' and key == ord('m'):
                break

            if status == 'out' and key == ord('o'):
                break

            cv.imshow("Mark Attendance", frame)
            key = cv.waitKey(1) & 0xff

            if key == ord('q'):
                res['status'] = 10
                break
    else:
        res['msg'] = "Camera not found"
        res['status'] = 00

    cap.release()
    cv.destroyAllWindows()
    return res



