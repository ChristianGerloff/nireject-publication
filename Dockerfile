FROM python:3.8.8-slim-buster
ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
RUN apt-get update && apt-get install -y \
    git gcc ffmpeg libsm6 libxext6 libgl1-mesa-dev xvfb -y

RUN mkdir /nireject
COPY . /nireject
WORKDIR /nireject
RUN chmod +x assets/install_assets.sh &&\
    ./assets/install_assets.sh
RUN pip3 install poetry &&\
    poetry config virtualenvs.create false &&\
    poetry install --no-dev