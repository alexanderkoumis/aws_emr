import abc
import argparse
import os
import sys

import cv2

from jobs.face_job import MRFaceTask
from cluster_iface.video_processor import SplitProcessor


cascade_xml = 'haarcascade_frontalface_default.xml'
colorferet_tar = 'colorferet.tar.gz'
cascade_xml_full = os.path.join('resources', 'haarcascades', cascade_xml)
colorferet_tar_full = os.path.join('resources', colorferet_tar)
results_txt = os.path.join('output', 'part-00000')


class FaceRunner(object):

    def __init__(self, video_path, output_dir):
        self.video_path = video_path
        self.output_dir = output_dir


    def run(self):

        print 'Splitting video'
        splitter = SplitProcessor(self.video_path, os.path.join(self.output_dir, 'video_split'), 'jpg')

        print 'Delegating job'
        face_count = MRFaceTask(args=[
            splitter.list_path,
            '--archive={}'.format(colorferet_tar_full),
            '--file={}'.format(cascade_xml_full),
            '--output-dir={}'.format(os.path.abspath(self.output_dir)),
            '--jobconf=job.settings.colorferet_tar={}'.format(colorferet_tar),
            '--jobconf=job.settings.cascade_xml={}'.format(cascade_xml)
        ])

        max_wlen = 8
        items = []

        with face_count.make_runner() as runner:
            runner.run()

        for line in open(results_txt):
            item = line.rstrip('\n').split('\t')
            max_wlen = max(max_wlen, len(item[0]))
            items.append(item)

        pad = '{:' + '{}'.format(max_wlen) + '}'
        fmat = '{}:\t{}'.format(pad, '{}')
        print fmat.format('--RACE--', '--COUNT--')
        for item in items:
            print '{}'.format(fmat.format(item[0], item[1]))

    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('video_file', help='Specify location of video file')
    parser.add_argument('output_dir', help='Specify file output location')
    args = parser.parse_args()

    face_runner = FaceRunner(args.video_file, args.output_dir)
    face_runner.run()

    # Last results for ./input/videos/the_intern.mp4
    # Not looking very diverse...
    #
    # --RACE--                   :    --COUNT--
    # "Asian"                    :    196461
    # "Asian-Middle-Eastern"     :    0
    # "Black-or-African-American":    36873
    # "Hispanic"                 :    65288
    # "Native-American"          :    0
    # "Other"                    :    0
    # "Pacific-Islander"         :    0
    # "White"                    :    680119