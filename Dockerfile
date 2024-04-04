FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install software-properties-common -y
RUN add-apt-repository ppa:paparazzi-uav/ppa -y
RUN apt-get install git -y

RUN apt-get install gcc-arm-none-eabi gdb-multiarch pprzgcs -y
RUN apt-get -f -y install paparazzi-dev paparazzi-jsbsim dfu-util



RUN git clone --origin upstream https://github.com/paparazzi/paparazzi.git && cd paparazzi
RUN cd paparazzi && make
ENV PAPARAZZI_SRC=/paparazzi
ENV PAPARAZZI_HOME=/paparazzi
ADD paparazzi_diff paparazzi_diff
RUN cp -r paparazzi_diff/* /paparazzi

RUN apt-get update && apt-get upgrade -y && apt-get install -y git cmake gfortran libopenmpi-dev openmpi-bin libnetcdf-dev libnetcdff-dev nco python3 python3-pip
RUN pip install bs4
RUN pip install pymoo netCDF4

ENV OMPI_ALLOW_RUN_AS_ROOT=1
ENV OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

RUN ln -sf ../bin/python3 ../bin/python
RUN cd paparazzi && make -f Makefile.ac AIRCRAFT="ardrone2" nps.compile


RUN git clone https://github.com/uDALES/u-dales.git
ADD u-dales_diff u-dales_diff
RUN cp -r u-dales_diff/* u-dales/
RUN mkdir -p u-dales/build/release && cd u-dales/build/release && cmake -LA ../.. && make

ADD Kaze Kaze
