FROM rasa/rasa-sdk:latest
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["start", "--actions", "actions"]
