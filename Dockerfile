FROM python:3.10-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de dependencias
COPY backend/requirements.txt ./requirements.txt

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la app
COPY backend/ .

# Exponer el puerto para que Render pueda acceder
EXPOSE 8080

# Comando para iniciar la app
CMD ["python", "app.py"]
