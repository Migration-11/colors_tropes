FROM python:3.9.12-slim

# Set working directory
WORKDIR /app

# Set environment variable
ENV INSTALL_ON_LINUX=1

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start


# Copy the application code
COPY . .

# Create a directory for logs
# RUN mkdir /app/logs

# Expose the port for Streamlit
EXPOSE 8501

CMD [ "/start" ]
