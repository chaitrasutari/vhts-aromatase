# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies required by RDKit
RUN apt-get update && apt-get install -y \
    libxrender1 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Create a user to run the app (Hugging Face security requirement)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy the requirements file and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY --chown=user . .

# Expose the specific port Hugging Face requires
EXPOSE 7860

# Command to boot the Streamlit app on the correct port
CMD ["streamlit", "run", "src/app/app.py", "--server.port=7860", "--server.address=0.0.0.0"]