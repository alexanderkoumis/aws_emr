"""A face detection job
"""

import os
import re
import sys

import cv2
import numpy

from mrjob.compat import jobconf_from_env
from mrjob.job import MRJob

from cluster_iface.datasets.color_feret import ColorFeret


show_results = False
write_results = False


def display_result(image, race_predicted):
    cv2.putText(image, race_predicted, (0, 200), cv2.FONT_HERSHEY_SIMPLEX, .7, (255, 255, 255), 1)
    cv2.imshow('Race prediction', image)
    cv2.waitKey(33)


class MRFaceTask(MRJob):

    def mapper_init(self):

        cascade_xml = jobconf_from_env('job.settings.cascade_xml')
        colorferet_dir = jobconf_from_env('job.settings.colorferet_tar')
        self.output_dir = os.path.join(jobconf_from_env('mapreduce.task.output.dir'), 'faces')
        self.recognizer = cv2.createLBPHFaceRecognizer()
        # self.recognizer = cv2.createFisherFaceRecognizer()
        # self.recognizer = cv2.createEigenFaceRecognizer()
        images, labels = ColorFeret.load_from_small_dataset(colorferet_dir)
        self.recognizer.train(images, numpy.array(labels))
        self.face_cascade = cv2.CascadeClassifier(cascade_xml)
        self.race_predicted = {
            'Black-or-African-American': 0,
            'Asian': 0,
            'Asian-Middle-Eastern': 0,
            'Hispanic': 0,
            'Native-American': 0,
            'Other': 0,
            'Pacific-Islander': 0,
            'White': 0
        }
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def mapper(self, _, image_path):

        frame_bgr = cv2.imread(image_path)
        frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(frame_gray, 2, 8)

        for (x, y, w, h) in faces:

            cutout_bgr = cv2.resize(frame_bgr[y:y+h, x:x+w], (256, 256))
            cutout_gray = cv2.resize(frame_gray[y:y+h, x:x+w], (256, 256))
            race_predicted_num, conf = self.recognizer.predict(cutout_gray)
            race_predicted_str = ColorFeret.face_labels_num[int(race_predicted_num)]
            self.race_predicted[race_predicted_str] += 1

            if show_results:
                display_result(cutout_bgr, race_predicted_str)
            if write_results:
                cv2.imwrite(os.path.join(self.output_dir, '{}_{}_{}_{}.png'.format(x, y, w, h)), cutout_bgr)

        for race in self.race_predicted:
            yield race, self.race_predicted[race]

    def combinder(self, race, count):
        yield race, sum(count)

    def reducer(self, race, count):
        yield race, sum(count)


if __name__ == '__main__':

    MRFaceTask.run()
