#### CUDA

CUDA_DIR=/usr/local/cuda
DRIVERS_DIR=$PWD/nvidia

CUDA_RUN=http://developer.download.nvidia.com/compute/cuda/7.5/Prod/local_installers/cuda_7.5.18_linux.run
NVIDIA_RUN=http://us.download.nvidia.com/XFree86/Linux-x86_64/352.55/NVIDIA-Linux-x86_64-352.55.run

mkdir $DRIVERS_DIR

sudo yum -y update && sudo yum -y install cmake && sudo yum -y groupinstall "Development tools"
sudo pip -v install numpy

wget $CUDA_RUN -P $DRIVERS_DIR
wget $NVIDIA_RUN -P $DRIVERS_DIR

chmod +x $DRIVERS_DIR/*.run

# sudo reboot

$DRIVERS_DIR/cuda_7.5.18_linux.run -extract=$DRIVERS_DIR
sudo $DRIVERS_DIR/NVIDIA-Linux-x86_64-352.55.run -s -N --no-kernel-module
sudo $DRIVERS_DIR/cuda-linux64-rel-7.5.18-19867135.run -noprompt
sudo $DRIVERS_DIR/cuda-samples-linux-7.5.18-19867135.run -noprompt
rm -rf $DRIVERS_DIR

echo "export PATH=$PATH:$CUDA_DIR/bin" >> ~/.bashrc
echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUDA_DIR/lib64" >> ~/.bashrc

#### OPENCV

OPENCV_DIR=$PWD/opencv
OPENCV_CONTRIB_DIR=$PWD/opencv_contrib
git clone https://github.com/Itseez/opencv $OPENCV_DIR
git clone https://github.com/Itseez/opencv_contrib $OPENCV_CONTRIB_DIR
mkdir $OPENCV_DIR/build && cd $OPENCV_DIR/build
cmake -D WITH_1394=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_TESTS=OFF -D BUILD_WITH_DEBUG_INFO=OFF -D CPACK_SOURCE_TGZ=ON -D OPENCV_EXTRA_MODULES_PATH=$OPENCV_CONTRIB_DIR/modules ..
make -j$(nproc)
make -j$(nproc) package
echo "export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python2.7/dist-packages/" >> ~/.bashrc





/usr/local/lib/python2.7/dist-packages/



  #   1  sudo yum -y update && sudo yum -y install cmake && sudo yum -y groupinstall "Development tools"
  #   2  sudo pip install numpy
  #   3  wget http://us.download.nvidia.com/XFree86/Linux-x86_64/352.55/NVIDIA-Linux-x86_64-352.55.run
  #   4  wget http://developer.download.nvidia.com/compute/cuda/7.5/Prod/local_installers/cuda_7.5.18_linux.run
  #   5  chmod +x ./cuda_7.5.18_linux.run 
  #   6  mkdir nvidia
  #   7  DRIVERS_DIR=$PWD/nvidia
  #   8  ./cuda_7.5.18_linux.run -extract=$DRIVERS_DIR
  #   9  chmod +x $DRIVERS_DIR/*.run
  #  10  cd $DRIVERS_DIR 
  #  11  ls
  #  12  cd ..
  #  13  NVIDIA_RUN=http://us.download.nvidia.com/XFree86/Linux-x86_64/352.55/NVIDIA-Linux-x86_64-352.55.run
  #  14  wget $NVIDIA_RUN -P $DRIVERS_DIR
  #  15  $DRIVERS_DIR/NVIDIA-Linux-x86_64-352.55.run -s -N --no-kernel-module
  #  16  chmod +x $DRIVERS_DIR/*.run
  #  17  $DRIVERS_DIR/NVIDIA-Linux-x86_64-352.55.run -s -N --no-kernel-module
  #  18  sudo $DRIVERS_DIR/NVIDIA-Linux-x86_64-352.55.run -s -N --no-kernel-module
  #  19  $DRIVERS_DIR/cuda-linux64-rel-7.5.18-19867135.run -noprompt -cudaprefix=$CUDA_DIR
  #  20  sudo $DRIVERS_DIR/cuda-linux64-rel-7.5.18-19867135.run -noprompt -cudaprefix=$CUDA_DIR
  #  21  ${nproc}
  #  22  $nproc
  #  23  $(nproc)
  #  24  nproc
  #  25  lol=${nproc}
  #  26  echo $lol
  #  27  lol=$(nproc)
  #  28  echo $lol
  #  29  OPENCV_DIR=$PWD/opencv
  #  30  git clone https://github.com/Itseez/opencv opencv
  #  31  ls
  #  32  git clone https://github.com/Itseez/opencv $OPENCV_DIR 
  #  33  mkdir $OPENCV_DIR/build && cd $OPENCV_DIR/build
  #  34  cmake -D WITH_1394=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_TESTS=OFF -D BUILD_WITH_DEBUG_INFO=OFF -D CPACK_SOURCE_TGZ=ON ..
  #  35  make -j$(nproc)
  #  36  cat Makefile | grep install
  #  37  vim Makefile 
  #  38  make package
  #  39  ls
  #  40  aws configure
  #  41  aws s3 cp ./OpenCV-3.0.0-715-gb4112a5-x86_64.tar.gz s3://facedata
  #  42  rm -rf $DRIVERS_DIR 
  #  43  http://facedata.s3.amazonaws.com/OpenCV-3.0.0-715-gb4112a5-x86_64.tar.gz
  #  44  cd ..
  #  45  ls
  #  46  cd ..
  #  47  ls
  #  48  mkdir lol
  #  49  cd lol
  #  50  http://facedata.s3.amazonaws.com/OpenCV-3.0.0-715-gb4112a5-x86_64.tar.gz
  #  51  wget http://facedata.s3.amazonaws.com/OpenCV-3.0.0-715-gb4112a5-x86_64.tar.gz
  #  52  tar -xvf OpenCV-3.0.0-715-gb4112a5-x86_64.tar.gz 
  #  53  ls
  #  54  cd OpenCV-3.0.0-715-gb4112a5-x86_64
  #  55  ls
  #  56  tar -C . -f OpenCV-3.0.0-AmazonLinux2015.03-GPU-x86_64.tar.gz -z -c .
  #  57  ls
  #  58  rm OpenCV-3.0.0-AmazonLinux2015.03-GPU-x86_64.tar.gz 
  #  59  cd ..
  #  60  ls
  #  61  cd OpenCV-3.0.0-715-gb4112a5-x86_64
  #  62  rm ../OpenCV-3.0.0-715-gb4112a5-x86_64.tar.gz 
  #  63  tar -C . -f OpenCV-3.0.0-AmazonLinux2015.03-GPU-x86_64.tar.gz -z -c ../
  #  64  ls
  #  65  rm OpenCV-3.0.0-AmazonLinux2015.03-GPU-x86_64.tar.gz 
  #  66  tar -C . -f OpenCV-3.0.0-AmazonLinux2015.03-GPU-x86_64.tar.gz -z -c /home/ec2-user/lol/
  #  67  ls
  #  68  rm OpenCV-3.0.0-AmazonLinux2015.03-GPU-x86_64.tar.gz 
  #  69  tar -C . -f OpenCV-3.0.0-AmazonLinux2015.03-GPU-x86_64.tar.gz -z -c /home/ec2-user/lol
  #  70  ls
  #  71  rm OpenCV-3.0.0-AmazonLinux2015.03-GPU-x86_64.tar.gz 
  #  72  ls
  #  73  cd ..
  #  74  ls
  #  75  tar -C OpenCV-3.0.0-715-gb4112a5-x86_64 -f OpenCV-3.0.0-AmazonLinux2015.03-GPU-x86_64.tar.gz -z -c .
  #  76  ls
  #  77  mkdir lolly
  #  78  cd lolly/
  #  79  mv ../OpenCV-3.0.0-AmazonLinux2015.03-GPU-x86_64.tar.gz .
  #  80  tar -xvf OpenCV-3.0.0-AmazonLinux2015.03-GPU-x86_64.tar.gz 
  #  81  ls
  #  82  aws s3 cp ./OpenCV-3.0.0-AmazonLinux2015.03-GPU-x86_64.tar.gz s3://facedata
  #  83  ls
  #  84  cd ..
  #  85  ls
  #  86  cd ..
  #  87  ls
  #  88  rm -rf lol
  #  89  mkdir lol
  #  90  cd lol
  #  91  aws s3 cp s3://facedata/OpenCV-3.0.0-AmazonLinux2015.03-GPU-x86_64.tar.gz .
  #  92  ls
  #  93  sudo tar -xzvf ./OpenCV-3.0.0-AmazonLinux2015.03-GPU-x86_64.tar.gz -C /usr/local
  #  94  ls
  #  95  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
  #  96  export PATH=$PATH:/usr/local/bin
  #  97  python
  #  98  ls /usr/local/lib/python2.7/dist-packages/
  #  99  echo $PYTHONPATH
  # 100  export PYTHONPATH=/usr/local/lib/python2.7/dist-packages/
  # 101  python
  # 102  ls
  # 103  history
