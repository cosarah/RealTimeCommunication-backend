FROM python:3.9

ENV DEPLOY 1

WORKDIR /app

COPY requirements.txt .

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY . .

EXPOSE 79

COPY start.sh /start.sh

RUN chmod +x /start.sh

CMD ["./start.sh"]