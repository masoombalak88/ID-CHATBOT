FROM python:3.10.4
RUN apt update && apt upgrade -y
RUN apt install python3-pip -y
RUN apt install ffmpeg -y
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs
RUN npm i -g npm
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
RUN pip install -U -r requirements.txt
