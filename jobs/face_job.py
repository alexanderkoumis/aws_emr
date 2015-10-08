"""A face detection job
"""

import re

import cv2

from mrjob.job import MRJob

#from cluster_iface.security_context import AwsSecurityContext
#from cluster_iface.configuration import AwsConfiguration
# AWS_SEC = AwsSecurityContext()
# AWS_CONF = AwsConfiguration()
FACE_RE = re.compile(r'[\w]+')

class MRFaceTask(MRJob):
    """Do face tasks here.
    """
    def mapper(self, _, line):
        """Map out stuff.
        """
        # Not doing anything with image yet
        frame = cv2.imread(line, cv2.cv.CV_LOAD_IMAGE_GRAYSCALE)
        print frame.shape

        # print frame.shape()
        for face in FACE_RE.findall(line):
            # face some stuff.
            yield face.lower(), 1

    def combiner(self, face, counts):
        """Combine something here.
        """
        yield face, sum(counts)

    def reducer(self, face, counts):
        """What do we do here?
        """
        yield face, sum(counts)

if __name__ == '__main__':
    """Do a Face Task
    """
    MRFaceTask.run()


