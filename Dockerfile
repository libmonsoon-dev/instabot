FROM frolvlad/alpine-python3

WORKDIR instabot

RUN pip install --upgrade pip

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY ./src ./src

WORKDIR src

CMD ["python3", "main.py"]