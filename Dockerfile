FROM python:3.9-buster

RUN apt-get update
RUN apt-get -y install libvips libvips-dev 

# runtime interface consoleのインストール
RUN pip install awslambdaric

# localで実行するために、runtime interface emulatorのinstall
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
RUN chmod 755 /usr/bin/aws-lambda-rie
COPY entry.sh "/entry.sh"
RUN chmod 755 /entry.sh

# 実行ファイルをコンテナ内に配置。
ARG APP_DIR="/home/app/"
WORKDIR ${APP_DIR}
COPY app ${APP_DIR}
RUN pip install -r requirements.txt

ENTRYPOINT [ "/bin/bash", "/entry.sh" ]

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]