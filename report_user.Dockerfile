FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./report_user.py ./invokes.py ./amqp_lib.py ./
CMD [ "python", "./report_user.py" ]