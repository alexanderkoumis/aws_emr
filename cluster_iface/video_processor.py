import abc
import os
import cv2


face_cascade_file = './resources/haarcascades/haarcascade_frontalface_default.xml'
colorferet_dir = './resources/colorferet'


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
                self._process(frame_bgr, frame_num_curr, frame_num_total)
                if frame_num_curr == frame_num_total:
                    break
            else:
                print 'Error reading frame'

        print 'Read all images'


class FaceProcessorStandalone(_VideoProcessor):

    def __init__(self, video_path):
        super(FaceProcessorStandalone, self).__init__(video_path)
        self.face_cascade = cv2.CascadeClassifier(os.path.abspath(face_cascade_file))

    def _process(self, frame_bgr, frame_num_curr, frame_num_total):

        frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(frame_gray, 2, 8)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), (255,0,0), 2)

        cv2.imshow('face_capture', frame_bgr)
        if cv2.waitKey(10) == 27:
            print 'Exiting: User entered esc'
            sys.exit()


class SplitProcessor(_VideoProcessor):

    frame_paths_full = []
    frame_paths_relative = []
    list_path = ""

    def __init__(self, video_path, out_dir, out_ext):
        super(SplitProcessor, self).__init__(video_path)
        self.out_ext = out_ext
        # out_dir = os.path.abspath(out_dir)
        self.out_stem = os.path.splitext(os.path.basename(video_path))[0]
        self.out_base = os.path.join(out_dir, self.out_stem)

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        self.run()
        self._write_list(out_dir)

    def _process(self, frame_bgr, frame_num_curr, frame_num_total):
        frame_relative = '{}_{}.{}'.format(self.out_stem, frame_num_curr, self.out_ext)
        # frame_path = '{}_{}.{}'.format(self.out_base, frame_num_curr, self.out_ext)
        frame_full = '{}_{}.{}'.format(self.out_base, frame_num_curr, self.out_ext)
        if not os.path.isfile(frame_full):
            cv2.imwrite(frame_full, frame_bgr)
            print 'wrote frame :: {}/{} :: {}'.format(frame_num_curr, frame_num_total, frame_full)
        else:
            print 'skipping (exists) :: {}/{} :: {}'.format(frame_num_curr, frame_num_total, frame_full)
        self.frame_paths_full.append(frame_full)
        self.frame_paths_relative.append(frame_relative)
        
    def _write_list(self, out_dir):
        self.list_path = os.path.join(out_dir, 'list.txt')
        list_file = open(self.list_path, 'w')
        for frame_path in self.frame_paths_relative:
            list_file.write("%s\n" % frame_path)
        list_file.close()

    def remove_files(self):
        for frame_path in self.frame_paths:
            os.remove(frame_path)
        os.remove(self.list_path)
