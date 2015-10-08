import abc
import os
import sys

import cv2

from jobs.face_job import MRFaceTask

face_cascade = cv2.CascadeClassifier('./resources/haarcascades/haarcascade_frontalface_default.xml')

def exit(message):
    print 'Exiting:', message
    sys.exit()

class _VideoProcessor(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, video_path):
        self.video_path = video_path

    @abc.abstractmethod
    def _process(self, frame_bgr, frame_num_curr):
        raise NotImplementedError

    def run(self):

        cap = cv2.VideoCapture(self.video_path)
        while not cap.isOpened():
            cap = cv2.VideoCapture(self.video_path)
            cv2.waitKey(1000)
            print 'Waiting for the header (' + self.video_path + ' probably doesn\'t exist'

        frame_num_curr = int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))
        frame_num_total = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

        while True:
            flag, frame_bgr = cap.read()
            if flag:
                frame_num_curr = int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))
                self._process(frame_bgr, frame_num_curr)
                if frame_num_curr == frame_num_total:
                    break
            else:
                print 'Error reading frame'

        print 'Read all images'


class FaceProcessorStandalone(_VideoProcessor):

    def __init__(self, video_path):
        super(FaceProcessor, self).__init__(video_path)

    def _process(self, frame_bgr, frame_num_curr):

        frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(frame_gray, 2, 8)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), (255,0,0), 2)

        cv2.imshow('face_capture', frame_bgr)
        if cv2.waitKey(10) == 27:
            exit('User entered esc')


class SplitProcessor(_VideoProcessor):

    frame_paths = []
    list_path = ""

    def __init__(self, video_path, out_dir, out_ext):
        super(SplitProcessor, self).__init__(video_path)
        self.out_ext = out_ext
        out_dir = os.path.abspath(out_dir)
        out_stem = os.path.splitext(os.path.basename(video_path))[0]
        self.out_base = os.path.join(out_dir, out_stem)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        self.run()
        self._write_list(out_dir)

    def _process(self, frame_bgr, frame_num_curr):
        frame_path = '{}_{}.{}'.format(self.out_base, frame_num_curr, self.out_ext)
        self.frame_paths.append(frame_path)
        cv2.imwrite(frame_path, frame_bgr)
        
    def _write_list(self, out_dir):
        self.list_path = os.path.join(out_dir, 'list.txt')
        list_file = open(self.list_path, 'w')
        for frame_path in self.frame_paths:
            list_file.write("%s\n" % frame_path)
        list_file.close()

    def remove_files(self):
        for frame_path in self.frame_paths:
            os.remove(frame_path)
        os.remove(self.list_path)


class FaceRunner(object):

    def __init__(self, video_path, out_dir):
        self.video_path = video_path
        self.out_dir = out_dir

    def run(self):
        print 'Splitting video'
        splitter = SplitProcessor(self.video_path, self.out_dir, 'jpg')

        print 'Delegating job'
        arguments = [splitter.list_path, '--output-dir={}'.format(self.out_dir)]
        face_count = MRFaceTask(args=arguments)
        with face_count.make_runner() as runner:
            runner.run()

        print 'Removing split frames'
        splitter.remove_files()


if __name__ == '__main__':
    video_path = sys.argv[1]
    out_dir = sys.argv[2]

    # processor = FaceProcessorStandalone(video_path)
    # processor.run()

    face_runner = FaceRunner(video_path, out_dir)
    face_runner.run()