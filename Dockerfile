FROM python:3.9

#
WORKDIR /

#
COPY requirements.txt requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install --upgrade mysql-connector-python

#
COPY . ./

#
CMD ["uvicorn", "main:app","--host", "0.0.0.0", "--port", "8000"]

#docker build -t smartchaudiere:latest .
#docker run --name smartchaudiere -d -p 8000:8000 smartchaudiere:latest