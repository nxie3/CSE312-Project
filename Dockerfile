FROM python:3.8

ENV HOME /root
WORKDIR /root

COPY . .

EXPOSE 8000

RUN pip3 install -r requirements.txt

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && python tcp_server.py