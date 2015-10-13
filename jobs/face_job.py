"""A face detection job
"""

import os
import re

import cv2
import numpy

from mrjob.job import MRJob
from cluster_iface.datasets.color_feret import ColorFeret

FACE_RE = re.compile(r'[\w]+')
face_cascade_file = './resources/haarcascades/haarcascade_frontalface_default.xml'

class MRFaceTask(MRJob):

    MRJob.face_cascade = cv2.CascadeClassifier(os.path.abspath(face_cascade_file))
    # MRJob.recognizer = cv2.createFisherFaceRecognizer()
    MRJob.recognizer = cv2.createLBPHFaceRecognizer()
    # MRJob.recognizer = cv2.createEigenFaceRecognizer()

    # Why is this constructor called multiple times (cascade_file only set first time)?
    # I want to call init_classifiers() in constructor. Also, when I set values in 
    # init_classifiers(), any values set seem to be destroyed at the time MRJob.run()
    # is called 
    #
    # def __init__(self, cascade_file='', **kwargs):
    #     super(MRFaceTask, self).__init__(**kwargs)
    #     self.face_fascade = cv2.CascadeClassifier(cascade_file)

    def init_classifiers(self, cascade_file, colorferet_dir, out_dir):

        images, labels = ColorFeret.load_from_small_dataset(colorferet_dir)
        MRJob.recognizer.train(images, numpy.array(labels))
        MRJob.out_dir = os.path.abspath(os.path.join(out_dir, 'faces'))

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

    def mapper(self, _, image_path):

        frame = cv2.imread(image_path, cv2.cv.CV_LOAD_IMAGE_GRAYSCALE)
        faces = MRJob.face_cascade.detectMultiScale(frame, 2, 8)

        race_predicted = {
            'Black-or-African-American': 0,
            'Asian': 0,
            'Asian-Middle-Eastern': 0,
            'Hispanic': 0,
            'Native-American': 0,
            'Other': 0,
            'Pacific-Islander': 0,
            'White': 0
        }

        for (x, y, w, h) in faces:
            face_cutout = cv2.resize(frame[y:y+h, x:x+w], (256, 256))
            race_predicted_num, conf = MRJob.recognizer.predict(face_cutout)
            race_predicted_str = ColorFeret.face_labels_num[int(race_predicted_num)]
            race_predicted[race_predicted_str] += 1
            cv2.putText(face_cutout, race_predicted_str, (0, 200), cv2.FONT_HERSHEY_SIMPLEX, .7, (255, 255, 255), 1)
            out_path = os.path.join(MRJob.out_dir, '{}_{}_{}_{}.png'.format(x, y, w, h))
            cv2.imwrite(out_path, face_cutout)
            cv2.imshow('lol', face_cutout)
            cv2.waitKey(33)

        for race in race_predicted:
            yield race, race_predicted[race]

    def reducer(self, race, count):
        yield race, sum(count)

if __name__ == '__main__':
    """Do a Face Task
    """
    MRFaceTask.run()


