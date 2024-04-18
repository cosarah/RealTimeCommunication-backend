FROM python:3.9

ENV DEPLOY 1

WORKDIR /app

COPY requirements.txt .

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY . .

EXPOSE 80

COPY start.sh /start.sh

RUN chmod +x /start.sh
RUN chown 1000:1000 /start.sh
USER 1000

CMD ["bash","./start.sh"]