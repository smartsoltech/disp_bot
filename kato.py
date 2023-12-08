from db import engine, AddressClassifier, Session
import pandas as pd
from icecream import ic
# Загрузка и объединение двух файлов CSV, содержащих адресный классификатор Казахстана на русском и казахском языках

# file_path_ru = 'KATO_17.11.2023_ru.csv'
# file_path_kz = 'KATO_17.11.2023_kz.csv'

# def load_and_combine_csv(file_path_ru, file_path_kz):
#     try:
#         # Чтение обоих файлов
#         data_ru = pd.read_csv(file_path_ru, delimiter=';')
#         data_kz = pd.read_csv(file_path_kz, delimiter=';')

#         # Объединение файлов по общему идентификатору
#         combined_data = pd.merge(data_ru, data_kz, on='id', suffixes=('_ru', '_kz'))

#         return combined_data
#     except Exception as e:
#         return str(e)

# # Выполнение функции и проверка результатов
# combined_data = load_and_combine_csv(file_path_ru, file_path_kz)
# ic(combined_data)
# combined_data.head()  # Вывод первых нескольких строк для проверки

# ic(combined_data.to_sql('address_classifier', con=engine, if_exists='replace', index=False))

def get_cities():
    session = Session()
    try:
        cities = session.query(AddressClassifier).filter(AddressClassifier.code_ru.like('__00000000')).all()
        ic(cities)
        return [(city.code_ru, city.name_ru, city.name_kz) for city in cities]
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        session.close()
        
def get_districts_by_city(city_code):
    session = Session()
    try:
        districts = session.query(AddressClassifier).filter(AddressClassifier.code_ru.startswith(city_code[:2]), AddressClassifier.code_ru != city_code).all()
        return [(district.code_ru, district.name_ru, district.name_kz) for district in districts]
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        session.close()
 
def get_districts_by_city_name(city_name):
    session = Session()
    try:
        ic(city_name)
        # Находим код города по его названию
        city = session.query(AddressClassifier).filter(AddressClassifier.name_ru == city_name, AddressClassifier.code_ru.like('__00000000')).first()
        ic(city)

        if not city:
            ic("Город не найден")
            return []

        # Используем код города для поиска микрорайонов
        city_code = city.code_ru[:2]
        ic(city_code)
        districts = session.query(AddressClassifier).filter(AddressClassifier.code_ru.startswith(city_code), AddressClassifier.code_ru != city.code_ru).all()
        ic(districts)

        return [(district.code_ru, district.name_ru, district.name_kz) for district in districts]
    except Exception as e:
        ic(e)
        return []
    finally:
        session.close()

print(get_cities())
# print(get_districts_by_city_name(input('Введите название города: ')))
print(f"{get_districts_by_city(input('Введите код города: '))}, \n")
