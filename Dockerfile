FROM python:3.10-slim

WORKDIR /code

# Copy only necessary files
COPY requirements.txt /code/requirements.txt

# Install dependencies without proxy
RUN pip install --no-cache-dir -r /code/requirements.txt

# Copy specific application files/directories
COPY ./api /code/api
COPY ./config /code/config
COPY ./data /code/data
COPY ./logs /code/logs
COPY ./models /code/models
COPY ./schemas /code/schemas
COPY ./services /code/services
COPY ./utils /code/utils
COPY init_db.py /code/init_db.py
COPY main.py /code/main.py
COPY .env /code/.env

# Set the entrypoint script
ENTRYPOINT ["sh", "-c", "python init_db.py && python main.py"]