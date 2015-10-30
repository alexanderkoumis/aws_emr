"""A configuration module.
"""
import os
import yaml

from security_context import AwsSecurityContext

class Configuration(object):
    """Abstract Configuration class.
    """
    def __init__(self):
        pass

class AwsConfiguration(Configuration):
    """An AwsConfiguration for environment configuration control.
    """
    AWS_SEC = AwsSecurityContext()
    CONFIG_FILE = '.mrjob.conf'
    PEM_KEYS = '.ssh/key_pair.pem'
    CONFIGURATIONS = {
        'runners': {
            'emr': {
                'bootstrap': [
                    # 'sudo pip install youtube-dl',
                    # 'mkdir -p /home/hadoop/input && cd /home/hadoop/input && youtube-dl https://www.youtube.com/watch?v=HUzPwIP9BqE -o video.mp4',
                    # 'mkdir /home/hadoop/input/colorferet && cd /home/hadoop/input/colorferet && wget -O - https://github.com/alexanderkoumis/aws_emr/raw/master/resources/colorferet.tar.gz | tar xvz',
                    # 'cd /home/hadoop/input && wget https://raw.githubusercontent.com/Itseez/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml',
                    # 'sudo yum -y update && sudo yum -y install cmake',
                    # 'wget http://downloads.sourceforge.net/project/opencvlibrary/opencv-unix/3.0.0/opencv-3.0.0.zip',
                    # 'unzip opencv-3.0.0.zip && mkdir opencv-3.0.0/build && cd opencv-3.0.0/build',
                    # 'cmake -D WITH_1394=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_TESTS=OFF -D BUILD_WITH_DEBUG_INFO=OFF ..',
                    # 'make && sudo make install'
                    # 'echo "export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python2.7/dist-packages/" >> ~/.bashrc'
                ],
                'cleanup': [ # keep emr logs on S3 for debugging
                    'LOCAL_SCRATCH',
                    'JOB',
                    'JOB_FLOW'
                ],
                'setup': [
                    'sudo yum -y update && sudo yum -y install cmake',
                    'wget http://downloads.sourceforge.net/project/opencvlibrary/opencv-unix/3.0.0/opencv-3.0.0.zip',
                    'unzip opencv-3.0.0.zip && mkdir opencv-3.0.0/build && cd opencv-3.0.0/build',
                    'cmake -D WITH_1394=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_TESTS=OFF -D BUILD_WITH_DEBUG_INFO=OFF ..',
                    'make && sudo make install',
                    'export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python2.7/dist-packages/'
                #     'mkdir -p ~/input/colorferet && cd ~/input/colorferet && wget -O - https://github.com/alexanderkoumis/aws_emr/raw/master/resources/colorferet.tar.gz | tar xvz',
                #     'cd ~/input && youtube-dl https://www.youtube.com/watch?v=HUzPwIP9BqE -o video.mp4',
                #     'cd ~/input && wget https://raw.githubusercontent.com/Itseez/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml'
                ],
                # 'aws-region': 'us-east-1',
                ##### Cost Factors #####
                'num_ec2_instances': 2,
                'ec2_master_instance_type': 'm1.medium',
                'ec2_slave_instance_type': 'm1.medium',
                'max_hours_idle': 1,
                'mins_to_end_of_hour': 10,
                'pool_emr_job_flows': True,
                # 'pool_name': '',

                ##### Security Factors #####
                'ec2_key_pair': 'key_pair',
                'ec2_key_pair_file': os.path.join(AWS_SEC.HOME, PEM_KEYS),

                ##### Other #####
                'label': 'mcmc_konix',
                'ssh_tunnel_to_job_tracker': True,
                'visible_to_all_users': True,
                'ami_version': '3.10.0'
                # 'python_archives': None
            },
            'inline': {
                'base_tmp_dir': os.path.join(AWS_SEC.HOME, '.tmp')
            }
        }
    }
    if 'matt' not in os.path.basename(AWS_SEC.HOME):
        # If it's not matt it's alex. Hopefully.
        CONFIGURATIONS['runners']['emr']['owner'] = 'konixmusic'

    # The configured/formatted string resrouce.
    mrjob_conf = ''

    def __init__(self):
        self.conf_file = os.path.join(self.AWS_SEC.HOME, self.CONFIG_FILE)
        if not self.mrjob_conf:
            # We haven't config'd env b/c don't have the config'd format string.
            self.mrjob_conf = self._install_config(self.CONFIGURATIONS)
        # Control the environment.
        self._master_config_ctrlr()

    def _install_config(self, config):
        """Dump the config file.
        """
        return yaml.dump(config, default_flow_style=False)

    def _master_config_ctrlr(self):
        """Master environment config controller.
        """
        self._setenv_mrjob_config()
        self._setenv_aws_config()

    def _setenv_aws_config(self):
        """AWS uses a hidden directory with config files.
        """
        aws_hdir = '.aws'
        conf_file = 'config'
        cred_file = 'credentials'
        acc_kid = 'aws_access_key_id'
        sec_kid = 'aws_secret_access_key'

        aws_path = os.path.join(self.AWS_SEC.HOME, aws_hdir)
        if not os.path.isdir(aws_path):
            # We cant modify files in an dir that doesn't exist.
            os.mkdir(aws_path)

        aws_conf = os.path.join(aws_path, conf_file)
        if not os.path.isfile(aws_conf):
            # If the conf file doesn't exist write to it.
            conf = '[default]\nregion = us-east-1\n'
            with open(aws_conf, 'w+') as file_d:
                file_d.write(conf)

        aws_cred = os.path.join(aws_path, cred_file)
        if not os.path.isfile(aws_cred):
            # If the cred file doesn't exist write to it.
            cred = '[default]\n{} = {}\n{} = {}\n'
            data = cred.format(acc_kid,
                               self.AWS_SEC.access_key_id,
                               sec_kid,
                               self.AWS_SEC.secret_access_key)
            with open(aws_cred, 'w+') as file_d:
                file_d.write(data)

    def _setenv_mrjob_config(self):
        """Write the mrjob configuration file.
        """
        if not os.path.isfile(self.conf_file):
            # If it doesn't exist write it.
            with open(self.conf_file, 'w') as file_d:
                file_d.write(self.mrjob_conf)
        else:
            with open(self.conf_file, 'w+') as file_d:
                config = file_d.read()
                if config != self.conf_file:
                    # If it exists, but outdated, write the new config.
                    file_d.write(self.mrjob_conf)


if __name__ == '__main__':
    AWS_CONF = AwsConfiguration()


