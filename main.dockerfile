FROM python:3.5

WORKDIR /home/pi/CCTV

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./monitoring.py" ]