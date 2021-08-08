import matplotlib
matplotlib.use('Agg')
import numpy as np
import cv2 as cv
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import pickle
import os
from django.conf import settings
import pathlib
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from matplotlib import rcParams
from django.conf import settings

SAVE_PATH = os.path.join(settings.STATICFILES_DIRS[0], 'graph')

def visualise_data(embedded, targets):
    X_embedded = TSNE(n_components=2).fit_transform(embedded)
    for i, t in enumerate(set(targets)):
        idx = targets == t
        plt.scatter(X_embedded[idx, 0], X_embedded[idx, 1], label=t)

    plt.legend(bbox_to_anchor=(1, 1))
    rcParams.update({'figure.autolayout': True})
    plt.tight_layout()
    plt.savefig(SAVE_PATH + "/" + "training.png")
    plt.close()


def Training():
    res = {}
    try:
        proto_path = os.path.join(settings.BASE_DIR, 'model', 'deploy.prototxt')
        caffe_model_path = os.path.join(settings.BASE_DIR, 'model', 'res10_300x300_ssd_iter_140000.caffemodel')
        face_detector = cv.dnn.readNetFromCaffe(prototxt=proto_path, caffeModel=caffe_model_path)

        recognition_model = os.path.join(settings.BASE_DIR, 'model', 'openface_nn4.small2.v1.t7')
        face_recognizer = cv.dnn.readNetFromTorch(model=recognition_model)
        image_path = os.path.join(settings.BASE_DIR, 'capture')

        filenames = []
        for path, subdirs, files in os.walk(image_path):
            for name in files:
                if pathlib.Path(name).suffix in ['.jpg', '.jpeg', '.png']:
                    filenames.append(os.path.join(path, name))

        face_embeddings = []
        face_names = []

        for (i, filename) in enumerate(filenames):

            image = cv.imread(filename)
            image = cv.resize(image, (600, 400))
            (h, w) = image.shape[:2]
            try:
                image_blob = cv.dnn.blobFromImage(image, 1.0, (150, 150), (104.0, 177.0, 123.0), False,
                                              False)
            except cv.error as e:
                print(str(e))

            fd = face_detector.setInput(image_blob)
            face_detections = face_detector.forward()

            i = np.argmax(face_detections[0, 0, :, 2])
            confidence = face_detections[0, 0, i, 2]

            if confidence >= 0.5:
                box = face_detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                face = image[startY:endY, startX:endX]

                try:
                    face_blob = cv.dnn.blobFromImage(face, 1.0 / 255, (96, 96), (0, 0), True, False)
                except cv.error as e:
                    print(str(e))

                face_recognizer.setInput(face_blob)
                face_recognitions = face_recognizer.forward()

                name = filename.split(os.path.sep)[-2]
                face_embeddings.append(face_recognitions.flatten())
                face_names.append(name)
                try:
                    cv.imshow("training", image)
                    cv.waitKey(100)
                except Exception as e:
                    print(str(e))

        cv.destroyWindow("training")
        data = {"embeddings": face_embeddings, "names": face_names}

        le = LabelEncoder()
        labels = le.fit_transform((data["names"]))

        recognizer = SVC(C=1.0, kernel="linear", probability=True)
        recognizer.fit(data["embeddings"], labels)

        targets = np.array(face_names)
        X1 = np.array(face_embeddings)
        visualise_data(X1, targets)

        recognizer_path = os.path.join(settings.BASE_DIR, 'train', 'recognizer.pickle')
        le_path = os.path.join(settings.BASE_DIR, 'train', 'le.pickle')

        with open(recognizer_path, "wb") as fp:
            fp.write(pickle.dumps(recognizer))

        with open(le_path, "wb") as fp:
            fp.write(pickle.dumps(le))

        res['status'] = 11

    except Exception as e:
        res['status'] = 00
        # cv.destroyWindow("training")
        print(str(e))
    cv.destroyAllWindows()
    return res
