# Попытка получить список dataset с API data.egov.kz
import requests
from icecream import ic

# URL для получения списка dataset
url = "https://data.egov.kz/api/v4/mapping/dataset"

# Отправка GET запроса
response = requests.get(url)

# Проверка статуса ответа и вывод содержимого
if response.status_code == 200:
    datasets = response.json()
    datasets_list = datasets.keys()
else:
    datasets_list = f"Error: {response.status_code}"

ic(datasets_list)