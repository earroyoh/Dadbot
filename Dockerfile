# Extend the official Rasa SDK image
FROM rasa/rasa:2.0.0

# Use subdirectory as working directory
WORKDIR /app

# Copy any additional custom requirements, if necessary (uncomment next line)
COPY requirements.txt ./
COPY actions/requirements-actions.txt ./

# Change back to root user to install dependencies
USER root

# Install extra requirements for actions code, if necessary (uncomment next line)
RUN python3 -m pip install --upgrade pip && \
      python3 -m pip install -r requirements.txt && \
      python3 -m pip install -r requirements-actions.txt

# Copy actions folder to working directory
COPY ./dadbot.py /app
COPY ./actions /app/actions

# By best practices, don't run the code with root user
USER 1001
ENV FLASK_APP dadbot.py
ENTRYPOINT ["python3","-m","flask","run","--host=0.0.0.0"]
