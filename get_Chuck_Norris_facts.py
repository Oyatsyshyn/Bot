import requests

# функція яка надселає Get запит для отримання списку категорій яким можуть належати цитати
def get_List_Category():
    # Отримання списку категорій за допомогою ChuckNorris API за допомогою методу HTTP GET
    r = requests.get("https://api.chucknorris.io/jokes/categories")
    # отримані дані у форматі json
    json_data = r.json()
    # Перевірка чи запит виконався успішно і чи status дорівнює 200
    if not r.status_code == 200:
        raise Exception("Incorrect reply from ChuckNorris API. Status code: {}".format(r.statuscode))

    return json_data

# функція яка надселає Get запит для отримання випадкової цитати відносно отриманої назви категорії
def get_Random_fuct_API(category):
    # GET параметри для ChuckNorris API
    # "category" - це параметр який містить назву вибраної категорії цитати
    GetParameters = {
        "category": category
    }
    # перевірка чи не було задано категорію цитати
    if category == "":
        # Отримання інформацію про випадкову цитату з випадкової категорії із запиту до ChuckNorris API за допомогою методу HTTP GET
        r = requests.get("https://api.chucknorris.io/jokes/random")
    else:
        # Отримання інформацію про випадкову цитату з вибраної категорії із запиту до ChuckNorris API за допомогою методу HTTP GET
        r = requests.get("https://api.chucknorris.io/jokes/random", params=GetParameters)
    # отримані дані у форматі json
    json_data = r.json()
    # Перевірка чи запит виконався успішно і чи status дорівнює 200
    if not r.status_code == 200:
        raise Exception("Incorrect reply from ChuckNorris API. Status code: {}".format(r.statuscode))

    return json_data

# функція яка надселає Get запит для отримання списку всіх цитат в яких міститься текст для пошуку
def get_search_text_in_fuct_API(search_text):
    # GET параметри для ChuckNorris API
    # "query" - це параметр для пошуку тексту в цитатах
    GetParameters = {
        "query": search_text
    }
    # Отримання списку всіх цитат в яких міститься текст для пошуку із запиту до ChuckNorris API за допомогою методу HTTP GET
    r = requests.get("https://api.chucknorris.io/jokes/search", params=GetParameters)
    # отримані дані у форматі json
    json_data = r.json()
    # Перевірка чи запит виконався успішно і чи status дорівнює 200
    if not r.status_code == 200:
        raise Exception("Incorrect reply from ChuckNorris API. Status code: {}".format(r.statuscode))

    return json_data