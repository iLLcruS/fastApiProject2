# Используйте базовый образ, подходящий для вашего приложения (например, Python)
FROM python:3.10

# Установите зависимости
WORKDIR app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопируйте код в образ
COPY . .

RUN chmod a+x *.sh

ENTRYPOINT ["sh", "app.sh"]

# Команда для запуска вашего приложения (замените ее на свою)
#CMD ["uvicorn", "app.main:app", "--host=0.0.0.0" , "--reload" , "--port", "8000"]