FROM python:3.10.16 AS base 

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt 

COPY . .

RUN mkdir -p /app/output

RUN pylint ./main.py && pylint ./**/*.py

RUN python -m unittest -v tests.test_ukri_utils.Testing

CMD ["streamlit", "run", "./main.py"]
