FROM python:3.9
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "5000"]