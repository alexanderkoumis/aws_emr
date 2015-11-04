#!/usr/bin/python
"""Face detection cluster job runner.
"""

import datetime
import os
import sys
import subprocess
import tarfile
import boto3

from boto.s3.key import Key
from boto.emr.step import StreamingStep
from boto.emr.instance_group import InstanceGroup
from mrjob.job import MRJob

from cluster_iface.connection import AwsConnection
from cluster_iface.configuration import AwsConfiguration
from cluster_iface.video_processor import SplitProcessor
from jobs.face_job import MRFaceTask

cascade         = 'haarcascade_frontalface_default'
video           = 'street'

cascade_xml     = '{}.xml'.format(cascade)
video_mp4       = '{}.mp4'.format(video)
video_tar       = '{}.tar.gz'.format(video)

video_dir       = os.path.join('input', 'videos')
video_split_dir = os.path.join(video_dir, 'split')
video_split_txt = os.path.join(video_split_dir, 'list.txt')

cascade_full    = os.path.join('resources', cascade_xml)
video_full      = os.path.join(video_dir, video_mp4)
video_tar_full  = os.path.abspath(os.path.join(video_dir, video_tar))

# local_or_emr    = 'local'
local_or_emr    = 'emr'

def make_archive(dir, out):
    cwd = os.getcwd()
    os.chdir(dir)
    with tarfile.open(out, "w:gz") as tar:
        for frame_path in os.listdir('.'):
            print frame_path
            tar.add(frame_path)    
    os.chdir(cwd)

if __name__ == '__main__':
    config = AwsConfiguration()
    max_wlen = 8
    items = []

    out_path = ''

    # splitter = SplitProcessor(video_full, video_split_dir, 'jpg')
    # splitter.run()
    # make_archive(video_split_dir, video_tar_full)

    for sbucket in xrange(100):
        # Find an s3 output that doesn't already exist.
        try:
            arguments = [
                '--verbose',
                '--file={}'.format(cascade_full),
                '--jobconf=job.settings.video_dir=video_dir',
                '--jobconf=job.settings.cascade={}'.format(cascade_xml),
                '--jobconf=job.settings.colorferet=colorferet',
                '--archive=resources/colorferet.tar.gz#colorferet',
                '--archive=input/videos/street.tar.gz#video_dir',
                video_split_txt
            ]
            if local_or_emr == 'local':
                out_path = os.path.join('output', 'result_{}'.format(sbucket))
                if os.path.isdir(out_path):
                    continue
                arguments.extend([
                    '-rlocal',
                    '--output-dir={}'.format(out_path)
                ])
            elif local_or_emr == 'emr':
                out_path = 's3://facedata/out2/trash_{}'.format(sbucket)
                arguments.extend([
                    '-remr',
                    '--output-dir={}'.format(out_path)
                ])
            else:
                print 'Unrecognized run type:', local_or_emr
                sys.exit(1)
            word_count = MRFaceTask(args=arguments)
            word_count.set_up_logging(verbose=True, stream=sys.stdout)
            with word_count.make_runner() as runner:
                runner.run()
                for line in runner.stream_output():
                    key, value = word_count.parse_output_line(line)
                    klen = len(key)
                    if klen > max_wlen:
                        max_wlen = klen
                    items.append((key, value))
            break
        except IOError, excp:
            if 'Output path' in excp.message and 'already exists' in excp.message:
                # This bucket already exists, try another one.
                continue
            # We don't know what this exception is, re-raise it.
            raise
    #########################
    # Lets give a nice output.
    # making a table: fmat = '{:int(len_longest_word)}:\t{}'
    pad = '{:' + '{}'.format(max_wlen) + '}'
    fmat = '{}:\t{}'.format(pad, '{}')

    print 'Output In: {}'.format(out_path)
    print fmat.format('--WORD--', '--COUNT--')
    for key, value in items:
        print '  {}'.format(fmat.format(key, value))

