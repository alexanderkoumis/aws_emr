import abc
import argparse
import os
import sys
import tarfile

import cv2

from jobs.face_job import MRFaceTask
from cluster_iface.configuration import AwsConfiguration
from cluster_iface.video_processor import SplitProcessor

# Input


cascade         = 'haarcascade_frontalface_default'
colorferet      = 'colorferet'
video           = 'street'

cascade_xml     = '{}.xml'.format(cascade)
colorferet_tar  = '{}.tar.gz'.format(colorferet)
video_mp4       = '{}.mp4'.format(video)
video_tar       = '{}.tar.gz'.format(video)

video_dir       = os.path.join('input', 'videos')
video_split_dir = os.path.join(video_dir, 'split')

colorferet_full = os.path.join('resources', colorferet_tar)
cascade_full    = os.path.join('resources', cascade_xml)
video_full      = os.path.join(video_dir, video_mp4)
video_tar_full  = os.path.abspath(os.path.join(video_dir, video_tar))

# Output
# results_txt    = os.path.join(output_dir, 'part-00000')

def make_archive(dir, out):
    cwd = os.getcwd()
    os.chdir(dir)
    with tarfile.open(out, "w:gz") as tar:
        for frame_path in os.listdir('.'):
            print frame_path
            tar.add(frame_path)    
    os.chdir(cwd)

class FaceRunner(object):

    def run(self):

        config = AwsConfiguration()
        items = []
        max_wlen = 8

        # print 'Splitting video'
        # splitter = SplitProcessor(self.video_path, os.path.join(self.output_dir, 'video_split'), 'jpg')

        for sbucket in xrange(100):
            try:
                output_path = 's3://facedata/out2/trash{}'.format(sbucket + 50)

                print 'Delegating job, output path', output_path

                splitter = SplitProcessor(video_full, video_split_dir, 'jpg')                

                splitter.run()

                make_archive(video_split_dir, video_tar_full)                   

                face_count = MRFaceTask(args=[
                    '-v',
                    '-r',
                    'emr',
                    '--file={}'.format(cascade_full),
                    '--archive={}'.format(colorferet_full),
                    '--archive={}'.format(video_tar_full),
                    '--output-dir={}'.format(output_path),
                    '--jobconf=job.settings.video={}'.format(video),
                    '--jobconf=job.settings.cascade={}'.format(cascade_xml),
                    '--jobconf=job.settings.colorferet={}'.format(colorferet),
                    splitter.list_path
                ])


                with face_count.make_runner() as runner:
                    runner.run()

                # for line in open(results_txt):
                #     item = line.rstrip('\n').split('\t')
                #     max_wlen = max(max_wlen, len(item[0]))
                #     items.append(item)
            except IOError, excp:
                if 'Output path' in excp.message and 'already exists' in excp.message:
                    # This bucket already exists, try another one.
                    continue
                # We don't know what this exception is, re-raise it.
                raise           

        pad = '{:' + '{}'.format(max_wlen) + '}'
        fmat = '{}:\t{}'.format(pad, '{}')
        print fmat.format('--RACE--', '--COUNT--')
        for item in items:
            print '{}'.format(fmat.format(item[0], item[1]))

    
if __name__ == '__main__':


    # parser = argparse.ArgumentParser()
    # parser.add_argument('video_file', help='Specify location of video file')
    # parser.add_argument('output_dir', help='Specify file output location')
    # args = parser.parse_args()

    # face_runner = FaceRunner(args.video_file, args.output_dir)
    face_runner = FaceRunner()
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