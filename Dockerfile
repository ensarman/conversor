# Usar una imagen base oficial de Python
FROM python:3.13-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos necesarios para generar requirements.txt
COPY Pipfile Pipfile.lock /app/

# Instalar pipenv y generar requirements.txt
RUN pip install --no-cache-dir pipenv \
  && pipenv lock --requirements > requirements.txt

# Instalar las dependencias desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Gunicorn
RUN pip install gunicorn

# Copiar el resto de los archivos del proyecto al contenedor
COPY . /app

# Exponer el puerto en el que se ejecutará la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "conversiones.wsgi:application", "--bind", "0.0.0.0:8000"]