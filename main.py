# Підключення бібліотек
import get_ISS_flyover_information as ISSflyover
import get_location_from_name as ParseLocation
import get_post_webex_api as WebexAPI
import get_Chuck_Norris_facts as ChuckFuct
import requests
import datetime
import random
import time

# змінна в якій буде зберігатися Id вибраної кімнати
roomIdToGetMessages = None

# функція для отримання списку кімант і вибір кімнати через пошук за назвою і збереження Id цієї кімнати
def initialisation():
    global roomIdToGetMessages
    # отримання списку кімнат в Webex
    rooms = WebexAPI.get_list_rooms_webex()
    print("Список кімнат:")
    # виводжу список кімнат в термінал
    for room in rooms:
        print (room["title"])

    # Шукаємо назву кімнати та записуємо її назву в терміналі
    while True:
        # Введення назву кімнати, яку потрібно шукати
        roomNameToSearch = input("Which room should be monitored for send messages with webex bot? ")

        # призначаю змінну, яка буде містити Id вибраної кімнати
        roomIdToGetMessages = None
        for room in rooms:
            # Пошук назви кімнати за допомогою змінної roomNameToSearch
            if (room["title"] == roomNameToSearch):
                # Відображення кімнати, знайденої за допомогою змінної roomNameToSearch з додатковими параметри
                print("Found rooms with the word " + roomNameToSearch)

                # Збереження ідентифікатора кімнати та назву кімнати у змінні
                roomIdToGetMessages = room["id"]
                roomTitleToGetMessages = room["title"]
                print("Found room : " + roomTitleToGetMessages)
                break
        # перевірка чи в змінні roomIdToGetMessages є записано id знайденої кімнати
        if (roomIdToGetMessages == None):
            print("Sorry, I didn't find any room with " + roomNameToSearch + " in it.")
            print("Please try again...")
        else:
            break
    return 0

# відправлення повідомлення-відповіді в Webex кімнату з часом початку перельоту і його тривалістю
# відносно отриманого повідомлення з назвою місця розташування і Id кімнати в яку буде надсилатися повідомлення
def cmd_ISS_Location(messages, msg_id):
    # збереження тексту першого повідомлення в масиві
    message = messages[0]["text"]
    try:
        # отриманна назви місця розташування з вхідного повідомлення
        location = message[13:]
        # отримання координат місця розташування відносно введеної назви місця розташування
        json_data_location = ParseLocation.get_Location(location)
        # збереження місцезнаходження, отримане від MapQuest API, у змінній
        locationResults = json_data_location["results"][0]["providedLocation"]["location"]
        print("Розташування: " + locationResults)
        # збереження в змінних широту та довготу GPS, отримані від API MapQuest
        locationLat_Lng = json_data_location["results"][0]["locations"][0]["latLng"]
        locationLat = locationLat_Lng["lat"]
        locationLng = locationLat_Lng["lng"]
        # виведення в терміналі адресу розташування
        print("Розташування в GPS координатах: " + str(locationLat) + ", " + str(locationLng))

        # отримання час підйому та тривалість першого перельоту відносно ортиманих координат місця розташування
        risetime_durationInEpochSeconds = ISSflyover.get_ISS_flyover(locationLat_Lng)
        # збереження час підйому та тривалість першого перельоту у змінну
        risetimeInEpochSeconds = risetime_durationInEpochSeconds["risetime"]
        durationInSeconds = risetime_durationInEpochSeconds["duration"]
        # перетворити час підйому, який повертає служба API, у час Unix Epoch
        risetimeInFormattedString = str(datetime.datetime.fromtimestamp(risetimeInEpochSeconds))

        # зібірка повідомлення-відповіді
        responseMessage = f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n" \
                          f"Для місця розташування '{locationResults}' з координатами широти: {locationLat} і довготи {locationLng}\n" \
                          f"Початок першого перельоту МКС над заданими місцем буде: {risetimeInFormattedString}\n" \
                          f"Тривалість перельоту становить: {durationInSeconds} секунд.\n" \
                          f"Гарного дня!"
        # виведення повідомлення-відповідь в терміналі
        print("Відправлення до Webex Teams: " + responseMessage)

        # Відправлення повідомлення-відповіді до webex API
        WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage, parentId_To_Get_Messages=msg_id)

    except:
        # зібірка повідомлення-відповіді про помилку
        responseMessage = "Ви ввели неправильні дані."
        # виведення повідомлення-відповідь в терміналі
        print("Відправлення до Webex Teams: " + responseMessage)

        # Відправлення повідомлення-відповіді до webex API
        WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage, parentId_To_Get_Messages=msg_id)
    return 0

# відправлення повідомлення-відповіді в Webex кімнату з випадковою цитатою для вибраної або випадкової категорії
# відносно отриманого повідомлення з назвою категорії або виду вхідного прараметра і
# Id кімнати в яку буде надсилатися повідомлення
def cmd_chuck(messages, msg_id):
    # збереження тексту першого повідомлення в масиві
    message = messages[0]["text"]
    category_data = "" # змінна для списку можливиз категорій цитат
    responseMessage = "" # змінна для повідомлення-відповіді
    try:
        # перевіряємо чи користувач ввів додатковий параметр для команди
        if len(message) > 7:
            # якщо так то зберігаємо ці параметри в змінну
            params = message[7:]
        else:
            # в іншому випадку створюємо пусту змінну
            params = ""
        # перевіряємо чи користувач ввів праметр для отримання усього списку категорій після виконання команди
        if params == "-category":
            # отримання усього списку категорій цитат
            category_data = ChuckFuct.get_List_Category()
            # створюємо повідомлення-відповідь
            responseMessage = f"Категорії цитат від Чака Норіса:\n"
            # перебираємо кожну категорію і додаємо її назву до повідомлення-відповіді
            for category in category_data:
                responseMessage = responseMessage + category + "\n"
        # перевіряємо чи користувач ввів додатковий параметр для команди
        elif not params == "":
            # перевіряємо чи користувач ввів параметр для задання назви категорії
            if params[:2] == "-c":
                # витягуємо назву категорії з параметрів
                name_category = params[3:]
                # отримуємо випадкову цитату з категорії назву якої ввів коритсувач
                fuct_data = ChuckFuct.get_Random_fuct_API(name_category)
                # витягуємо текст цитати з отриманих даних
                fuct_text = fuct_data["value"]
                # збираємо повідомлення-відповідь
                responseMessage = f"Випадкова цитата від Чака Норіса з категорії '{name_category}':\n\t{fuct_text}"
            elif params[:2] == "-s":
                # витягуємо текст для пошуку його в цитатах
                search_text = params[3:]
                # отримуємо список цитат за текстом для пошуку серед усіх цитат який ввів коритсувач
                fucts_data = ChuckFuct.get_search_text_in_fuct_API(search_text)
                # витягуємо кількість знайдених цитат у яких міститься текст який задав користувач
                total_fucts = fucts_data["total"]
                # витягуємо цитати з отриманих даних
                result_fucts = fucts_data["result"]
                # збираємо повідомлення-відповідь з результатами пошуку по тексту
                responseMessage = f"Пошук в цитатах від Чака Норіса тексту '{search_text}'.\n" \
                                  f"Кількість знайдених цитат: {total_fucts}.\n" \
                                  f"Знайдені цитати:\n"
                # перебираємо кожну цитату і додаємо її текст до повідомлення-відповіді
                for i in range(len(result_fucts)):
                    # перевіряємо чи кількість читат не є більшою за 6
                    if i >= 6:
                        # якщо так то додаємо в кінець повідомлення три крапки і виходимо з циклу
                        responseMessage = responseMessage + "\t..."
                        break;
                    # витягуємо текст цитати з отриманих даних
                    fuct_text = result_fucts[i]["value"]
                    # додаємо цитату до повідомлення-відповіді
                    responseMessage = responseMessage + "\t" + fuct_text + "\n\n"
        else: # якщо параметрів до введеної команди немає то
            # отримуємо випадкову цитату з випадкової категорії
            fuct_data = ChuckFuct.get_Random_fuct_API(params)
            # витягуємо текст цитати з отриманих даних
            fuct_text = fuct_data["value"]
            # збираємо повідомлення-відповідь
            responseMessage = f"Випадкова цитата від Чака Норіса з випадкової катрегорії:\n\t{fuct_text}"

        # виведення повідомлення-відповідь в терміналі
        print("Відправлення до Webex Teams: " + responseMessage)

        # Відправлення повідомлення-відповіді до API webex
        WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage,parentId_To_Get_Messages=msg_id)

    except:
        # Відправлення повідомлення-відповіді про помилку
        responseMessage = "Ви ввели неправильні дані."
        # виведення повідомлення-відповідь в терміналі
        print("Відправлення до Webex Teams: " + responseMessage)

        # Відправлення повідомлення-відповіді до API webex
        WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage,parentId_To_Get_Messages=msg_id)
    return 0

# відправлення повідомлення-відповіді в Webex кімнату з зображенням і назвою мема
# відносно отриманого повідомлення з Id кімнати в яку буде надсилатися повідомлення
def cmd_meme(msg_id):
    try:
        # отримання списку мемів
        response = requests.get("https://api.imgflip.com/get_memes").json()
        # витягуємо url-адреси мемів і їхні назви
        memes = response["data"]["memes"]
        # записуємо кількість отриманих мемів
        count_memes = len(memes)
        # вибвраємо випадковим чином індекс мема
        number_meme = random.randint(0, count_memes)
        # витягуємо дані для мема відносно згенерованого індекса
        meme_data = memes[number_meme]
        # витягуємо url-адресу мема з отриманих даних
        foto_url_meme = [meme_data["url"]]
        # витягуємо назву мема з отриманих даних
        name_meme = meme_data["name"]
        # Відправлення повідомлення-відповіді в якому є фото і текст до API webex
        WebexAPI.post_send_photo_and_text_webex(roomIdToGetMessages, name_meme, foto_url_meme, parentId_To_Get_Messages=msg_id)
    except:
        # Відправлення повідомлення-відповіді про помилку
        responseMessage = "Сталася неочікувана помилка."
        # виведення повідомлення-відповідь в терміналі
        print("Відправлення до Webex Teams: " + responseMessage)

        # Відправлення повідомлення-відповіді до API webex
        WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage, parentId_To_Get_Messages=msg_id)
    return 0

# відправлення повідомлення-відповіді в Webex кімнату з інформацією про вміння цього бота
# відносно отриманої Id кімнати в яку буде надсилатися повідомлення
def cmd_start(msg_id):
    # зібірка повідомлення-відповіді
    responseMessage = "Ви запустили бота. \nЦей бот має такі можливості: \n" \
                      "\t- Виводить дату і час першого імовірного перельоту МКС над координатами місця яке було введено.\n" \
                      "\t- Виводить випадково вибрану цитату Чака Норіса з катигорії заданої користувачем або випадково \n" \
                      "\t- Виводить один випадковий мем і його назву отриманого списку мемів який оновлюється\n" \
                      "\t- За допомогою команд '/help' і '/start' можна отримати інформацію про опис команд, " \
                      "які може виконувати бот і загальну інформацію про нього відповідно. "

    # виведення повідомлення-відповідь в терміналі
    print("Відправлення до Webex Teams: " + responseMessage)

    # Відправлення повідомлення-відповіді до API webex
    WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage,parentId_To_Get_Messages=msg_id)
    return 0

# відправлення повідомлення-відповіді в Webex кімнату з інформацією про команди яакі бот може виконувати
# відносно отриманої Id кімнати в яку буде надсилатися повідомлення
def cmd_help(msg_id):
    # зібірка повідомлення-відповіді
    responseMessage = "Цей бот може виконувати такі команди: \n" \
                      "-\t'/help' - ця команда повернтає список достурпних команд і інформацію про них\n" \
                      "-\t'/start' - ця команда запускається в основному напочатку, а як результат вона надсилає інформацію про можливості бота\n" \
                      "-\t'/isslocation {location}' - ця команда виводить дату і час першого імовірного перельоту МКС над координатами місця яке було введено.\n" \
                      "Приклад запуску: '/isslocation Rivne'\n" \
                      "Примітка: місце розташування вводити на англійські мові, " \
                      "якщо ж будете використовуватии іншу мову то можуть виникнути неочікувані результати\n" \
                      "-\t'/chuck' - ця команда виводтить випадкову цитату з випадкової категорії\n" \
                      "-\t'/chuck -c {category_name}' - ця команда виводтить випадкову цитату з категорії введеної користувачем\n" \
                      "-\t'/chuck -s {search_text}' - ця команда виводтить список цитат в яких міститься пошуковий текст який задав користувач\n" \
                      "-\t'/chuck -category' - ця команда виводтить список назві категорій яким можуть належати цитати\n" \
                      "Приклад запуску: '/chack -c food', '/chack -s are'\n" \
                      "-\t'/meme' - ця команда виводтить випадковий мем з отриманого списку мемів"
    # виведення повідомлення-відповідь в терміналі
    print("Відправлення до Webex Teams: " + responseMessage)

    # Відправлення повідомлення-відповіді до API webex
    WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage,parentId_To_Get_Messages=msg_id)
    return 0

# основна програма бота
if __name__ == '__main__':
    # отримуємо список кімант і вибираємо кімнату через пошук за назвою і зберігаємо Id цієї кімнати
    initialisation()
    # змінна в якій буде міститися ID останнього повідомлення
    msg_id = "0"
    # запускайте цикл "bot" він буде виконуватися доки не буде зупинено вручну або не станеться виняток
    while True:
        # отримання останнього повідомлення з вибраної кімнати в Webex
        messages = WebexAPI.get_last_massages_webex(roomIdToGetMessages, 1)
        try:
            # збереження тексту першого повідомлення в масиві
            message = messages[0]["text"]
        except: # якщо повідомлення не є текстове то
            # очищуємо вміст змінної для тестового повідомлення
            message = ""
            # виводимо в термінал відповідне повідомлення
            print("Останнє повідомлення не містить тексту")
            # Засинаємо на 5 секунд
            time.sleep(5)
            # пропускаємо один цикл
            continue
        try:
            # перевірка чи Id отриманого повідомлення було збережено тобто чи дане повідомлення переглядалося раніше
            if msg_id != messages[0]["id"]:
                # якщо повідомлення нове то виводимо його в термінал
                print("Отримане повідомлення: " + message)
                # зберігаємо Id нового повідомлення в змінну
                msg_id = messages[0]["id"]
                # перевірка, чи починається текст повідомлення з ключового символу "/".
                if message.find("/") == 0:
                    # перевірка на те яка команда була надіслана через повідомлення і запускає відповідну функцію
                    # якщо команда не коректна то бот відправляє відповідне повідомлення
                    if message == "/start":
                        cmd_start(msg_id)
                    elif message.find("/isslocation") == 0:
                        cmd_ISS_Location(messages, msg_id)
                    elif message.find("/chuck") == 0:
                        cmd_chuck(messages, msg_id)
                    elif message.find("/meme") == 0:
                        cmd_meme(msg_id)
                    elif message == "/help":
                        cmd_help(msg_id)
                    else:
                        # зібірка повідомлення-відповіді про помилку
                        responseMessage = "Ви ввели некоректну команду."
                        # виведення повідомлення-відповідь в терміналі
                        print("Відправлення до Webex Teams: " + responseMessage)

                        # Відправлення повідомлення-відповіді до webex API
                        WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage,
                                                         parentId_To_Get_Messages=msg_id)
        except:
            # якщо повідомлень в кімнаті немає то виводимо відповідне повідомлення в термінал
            print("Повідомлень в кімнаті не знайдено")
            # і засинаємо на 5 секунд
            time.sleep(5)


