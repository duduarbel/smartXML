FROM python:3.9-slim

WORKDIR /app
#COPY ./Pipfile ./
#COPY ./Pipfile.lock ./

#RUN pipenv install --system --deploy

COPY ./test.py /app
COPY ./readme_example.py /app
COPY ./files/* /app/files/

RUN pip install --upgrade smartXML
RUN pip install --upgrade smartXML
Run pip install pytest


# Run your script
CMD ["python", "test.py"]
