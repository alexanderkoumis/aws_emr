#!/usr/bin/python

""" Face detection cluster job runner.
"""

import argparse
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


verbose = True

def print_debug(message):
    if verbose:
        print '[DEBUG]', message

def make_archive(files, out):
    with tarfile.open(out, 'w:gz') as tar:
        print_debug('Creating tar: {}'.format(out))
        for file in files:
            print file
            tar.add(file, arcname=os.path.basename(file))

def get_youtube_filename(youtube_url):
    try:
        return subprocess.check_output(['youtube-dl', '--get-filename', youtube_url]).rstrip().replace(' ', '').replace('&', '')
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            sys.exit('youtube-dl not found, install with: pip install youtube-dl')
        else:
            raise


if __name__ == '__main__':

    config = AwsConfiguration()
    run_type = 'local' # Currently supports local and emr
    max_wlen = 8
    out_path = None
    results = []

    video_tar_full = None
    video_txt_full = None
    cascade_xml = 'haarcascade_frontalface_default.xml'
    cascade_full = os.path.join('resources', cascade_xml)

    parser = argparse.ArgumentParser()
    parser.add_argument('--run', help='Run type (same as MRJob) (defaults to local)')
    parser.add_argument('--youtube', help='Process YouTube video (requires youtube-dl)')
    args = parser.parse_args()

    if args.run:
        run_type = args.run

    if args.youtube:
        video_file = get_youtube_filename(args.youtube)
        video_stem = video_file.split('.')[0]
        video_tar = '{}.tar.gz'.format(video_stem)
        video_dir_full = os.path.join('input', 'videos', video_stem)
        video_file_full = os.path.join('input', 'videos', video_file)
        video_tar_full = os.path.join('input', 'videos', video_tar)
        video_txt_full = os.path.join(video_dir_full, 'list.txt')

        if not os.path.exists(video_dir_full):
            os.makedirs(video_dir_full)

        print_debug('Downloading video {} to {}'.format(video_stem, video_file_full))
        subprocess.call(['youtube-dl', '-q', '-o', video_file_full, args.youtube])

        print_debug('Splitting frames to {}'.format(video_dir_full))
        splitter = SplitProcessor(video_file_full, video_dir_full, 'jpg')
        splitter.run()

        print_debug('Creating archive of frames as {}'.format(video_tar_full))
        make_archive(splitter.frame_paths_full, video_tar_full)

    else:
        parser.print_help()
        sys.exit(2)

    if not video_tar_full or not video_txt_full:
        sys.exit('Something went wrong. video_tar_full is None')

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
                '--archive={}#video_dir'.format(video_tar_full),
                video_txt_full
            ]
            if run_type == 'local':
                out_path = os.path.join('output', 'result_{}'.format(sbucket))
                if os.path.isdir(out_path):
                    continue
                arguments.extend([
                    '-rlocal',
                    '--output-dir={}'.format(out_path)
                ])
            elif run_type == 'emr':
                out_path = 's3://facedata/out2/trash_{}'.format(sbucket)
                arguments.extend([
                    '-remr',
                    '--output-dir={}'.format(out_path)
                ])
            else:
                sys.exit('Unrecognized run type: {}'.format(run_type))
            word_count = MRFaceTask(args=arguments)
            word_count.set_up_logging(verbose=True, stream=sys.stdout)
            with word_count.make_runner() as runner:
                runner.run()
                for line in runner.stream_output():
                    key, value = word_count.parse_output_line(line)
                    klen = len(key)
                    if klen > max_wlen:
                        max_wlen = klen
                    results.append((key, value))
            break
        except IOError, excp:
            if 'Output path' in excp.message and 'already exists' in excp.message:
                continue
            raise

    pad = '{:' + '{}'.format(max_wlen) + '}'
    fmat = '{}:\t{}'.format(pad, '{}')

    print 'Output In: {}'.format(out_path)
    print fmat.format('--WORD--', '--COUNT--')
    for key, value in results:
        print '  {}'.format(fmat.format(key, value))
