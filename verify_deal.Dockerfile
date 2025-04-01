FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./verify_deal.py ./invokes.py ./amqp_lib.py ./
CMD [ "python", "./verify_deal.py" ]