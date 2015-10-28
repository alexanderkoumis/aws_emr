#!/usr/bin/python
"""A simple Cluster job runner.
"""

# Open-Source/Free Imports
import os
import subprocess
import boto3

import datetime
from boto.s3.key import Key
from boto.emr.step import StreamingStep
from boto.emr.instance_group import InstanceGroup

from mrjob.job import MRJob

# Private-IP Imports Carlis/Koumis.
from cluster_iface.connection import AwsConnection
from cluster_iface.configuration import AwsConfiguration

from mr_job import MRWordFreqCount

class JobRunner(object):
    """An abstract job runner object..
    """
    def __init__(self):
        raise Exception("UnImplemented")

class AwsJobRunner(AwsConnection, JobRunner):
    """An amazon job runner object.
    """

    def __init__(self):
        AwsConnection.__init__(self)
        #super(AwsJobRunner, self).__init__()
        self.steps = []
        self.keys = {}
        self.connect()

    def get_storage(self, name):
        """Get a reference to a AWS S3 bucket.
        """
        self.bucket = self.s3_conn.get_bucket(name)

    def key_from_file(self, key, fname):
        """Create an AWS s3 resource from fname.
        """
        new_key = Key(self.bucket)
        self.keys[key] = new_key
        with open(fname, 'r') as file_d:
            size_stored = key.set_contents_from_file(file_d)
        return size_stored

    def string_from_key(self, key):
        """Turn an AWS s3 resource into a str.
        """
        if key in self.keys:
            interest_key = self.keys[key]
        else:
            interest_key = bucket.get_key(key)
        if not interest_key:
            # We failed to get the bucket from S3.
            return interest_key
        data = interest_key.get_contents_as_string()
        print data
        return data

if __name__ == '__main__':
    config = AwsConfiguration()
    max_wlen = 8
    items = []
    for sbucket in xrange(100):
        # Find an s3 output that doesn't already exist.
        try:
            output_path = 's3://facedata/out2/trash{}'.format(sbucket)
            output_arg = '--output-dir={}'.format(output_path)
            arguments = [
            '-r',
            'emr',
            '--file={}'.format(os.path.join('input', 'videos', 'street.mp4')),
            'input/stanford_article.txt',
            output_arg]
            word_count = MRWordFreqCount(args=arguments)
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

    print 'Output In: {}'.format(output_path)
    print fmat.format('--WORD--', '--COUNT--')
    for key, value in items:
        print '  {}'.format(fmat.format(key, value))

