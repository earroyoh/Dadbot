# Extend the official Rasa SDK image
FROM rasa/rasa:2.0.0

# By best practices, don't run the code with root user
USER 1000

# Use subdirectory as working directory
WORKDIR /app
ENV HOME /app

# Copy any additional custom requirements, if necessary (uncomment next line)
COPY requirements.txt ./
COPY actions/requirements-actions.txt ./

# Install extra requirements for actions code, if necessary (uncomment next line)
ENV PATH /app/.local/bin:/opt/venv/bin:/bin:/usr/bin:/usr/local/bin
RUN python -m pip install --user -r requirements.txt && \
    python -m pip install --user -r requirements-actions.txt
ENV PYTHONPATH /opt/venv/lib/python3.7:/app/.local/lib/python3.7:/usr/local/lib/python3.7

# Copy actions folder to working directory
COPY ./dadbot.py /app
COPY ./actions /app/actions

ENV FLASK_APP /app/dadbot.py
ENTRYPOINT ["python","-m","flask","run","--host=0.0.0.0"]
