# Extend the official Rasa SDK image
FROM rasa/rasa-sdk:2.0.0

# By best practices, don't run the code with root user
USER 1000

# Use subdirectory as working directory
WORKDIR /app
ENV HOME /app

# Copy config files and actions folder to working directory
COPY . /app

# Install extra requirements for actions code, if necessary (uncomment next line)
RUN source /opt/venv/bin/activate venv && \
    python3 -m pip install -t /app/.local --upgrade --no-cache-dir -r requirements.txt && \
    python3 -m pip install -t /app/.local --upgrade --no-cache-dir -r actions/requirements-actions.txt
ENV PATH "/app/.local/bin:/opt/venv/bin:/bin:/usr/bin:/usr/local/bin"
ENV PYTHONPATH "/app/.local/:/opt/venv/:/usr/local/"

EXPOSE 5005 5055 8000
CMD ["start", "--actions", "actions"]
