"""A mrjob mapreduce wordcount example using EMR HDFS.
"""
import re
import cv2
import numpy

from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.compat import jobconf_from_env

#from cluster_iface.security_context import AwsSecurityContext
#from cluster_iface.configuration import AwsConfiguration
# from cluster_iface.datasets.color_feret import ColorFeret


WORD_RE = re.compile(r'[\w]+')
# AWS_SEC = AwsSecurityContext()
# AWS_CONF = AwsConfiguration()

video_dir = jobconf_from_env('job.settings.video')
cascade = jobconf_from_env('job.settings.cascade')
colorferet = jobconf_from_env('job.settings.colorferet')

face_labels_str = {
    'Black-or-African-American': 0,
    'Asian': 1,
    'Asian-Middle-Eastern': 2,
    'Hispanic': 3,
    'Native-American': 4,
    'Other': 5,
    'Pacific-Islander': 6,
    'White': 7
}

def load_from_small_dataset(ColorFeret, colorferet_small_dir):

    images = []
    labels = []

    for face_label_str in face_labels_str:
        face_label_num = face_labels_str[face_label_str]
        image_dir = os.path.join(colorferet_small_dir, face_label_str)
        image_files = [os.path.join(image_dir, image_file) for image_file in os.listdir(image_dir)]
        images_tmp = [cv2.resize(cv2.imread(image_file, 0), (256, 256)) for image_file in image_files if image_file.split('.')[-1] == 'png']
        labels_tmp = [face_label_num] * len(images_tmp)
        images.extend(images_tmp)
        labels.extend(labels_tmp)

    return images, labels

class MRWordFreqCount(MRJob):
    """A HDFS word count interface.
    """

    def mapper_init(self):
        lol = 1
        # self.video_dir = jobconf_from_env('job.settings.video')
        # cascade = jobconf_from_env('job.settings.cascade')
        # colorferet = jobconf_from_env('job.settings.colorferet')
        
        # self.output_dir = os.path.join(jobconf_from_env('mapreduce.task.output.dir'), 'faces')
        # self.recognizer = cv2.createLBPHFaceRecognizer()
        # self.recognizer = cv2.createFisherFaceRecognizer()
        # self.recognizer = cv2.createEigenFaceRecognizer()
        # images, labels = ColorFeret.load_from_small_dataset(colorferet)
        # self.recognizer.train(images, numpy.array(labels))
        # self.face_cascade = cv2.CascadeClassifier(cascade)
        # if not os.path.exists(self.output_dir):
        #     os.makedirs(self.output_dir)


    def mapper(self, _, line):
        """A wordcount mapper.
        """
        for word in WORD_RE.findall(line):
            yield word.lower(), 1

    def combiner(self, word, counts):
        """A wordcount combiner.
        """
        yield word, sum(counts)

    def reducer(self, word, counts):
        """A wordcount reducer.
        """
        yield word, sum(counts)


if __name__ == '__main__':
    MRWordFreqCount.run()


