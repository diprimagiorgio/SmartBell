###################################
#       The smart Doorbell        #
###################################
#

################
## BASE IMAGE ##
################

FROM balenalib/raspberrypi3-debian-python:build



##########################
## DEPENDENCIES INSTALL ##
##########################
## Install face_recognition dependencies
RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS

######################
## PICAMERA INSTALL ##
######################
## Install picamera for python 3

RUN apt-get install -y python3-picamera
RUN python3 -m pip install --upgrade pip
RUN pip3 install --upgrade picamera[array]


##################
## Pypi INSTALL ##
##################
## Install required python packages

#RUN pip install face_recognition && pip install RPi.GPIO && pip install Pillow && pip install python-telegram-bot
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

#####################
## Numpy install   ##
#####################
## A Numpy version is installed during the disutils installation of dlib.
## However, it was buggy and outdated.
## Also, it's better practice to install python packages using pip

RUN rm -rf /usr/lib/python3/dist-packages/numpy* && \
    cd ~ && \
    pip install numpy

# cp takes all the files located in the current directory and copies them into the image
COPY . .
# run the app
CMD ["flask","run"]
