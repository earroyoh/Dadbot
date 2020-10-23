# Extend the official Rasa SDK image
FROM rasa/rasa:2.0.0

# Use subdirectory as working directory
USER 1000
WORKDIR /app
ENV HOME /app

# Copy any additional custom requirements, if necessary (uncomment next line)
COPY requirements.txt ./
COPY actions/requirements-actions.txt ./

# Change back to root user to install dependencies

# Install extra requirements for actions code, if necessary (uncomment next line)
RUN python3 -m pip install --user -r requirements.txt && \
      python3 -m pip install --user -r requirements-actions.txt
ENV PATH /app/.local//bin:/bin:/usr/bin:/usr/local/bin
ENV PYTHONPATH /app/.local/lib/python3.7:/opt/venv/lib/python3.7:/usr/local/lib/python3.7

# Copy actions folder to working directory
COPY ./dadbot.py /app
COPY ./actions /app/actions

# By best practices, don't run the code with root user
ENV FLASK_APP dadbot.py
ENTRYPOINT ["python3","-m","flask","run","--host=0.0.0.0"]
