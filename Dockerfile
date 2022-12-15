FROM python:3.10

# Install dependencies
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

ENV PYTHONUNBUFFERED True
# Copy the API code
COPY . /app/

# Set the working directory to the API code
WORKDIR /app/

# Expose the API port
EXPOSE 5000

# Run the API
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]