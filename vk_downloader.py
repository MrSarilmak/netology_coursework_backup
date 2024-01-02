import os
import requests

from lib import json_save


class VkDownloader:
    def __init__(self, token, app_id):
        self.token = token
        self.app_id = app_id

    def get_photos_request(self, offset=0, count=5):
        url = "https://api.vk.com/method/photos.get"
        params = {"owner_id": self.app_id,
                  "album_id": "profile",
                  "access_token": self.token,
                  "v": "5.131",
                  "extended": "1",
                  "photo_sizes": "1",
                  "count": count,
                  "offset": offset
                  }
        res = requests.get(url=url, params=params)
        return res.json()

    def get_photos(self, count=5, debug=False):
        i = 0
        data = self.get_photos_request(i, count)
        if data is None:
            if debug:
                print("сервер вернул не корректный json")
            return False
        if not data.get("response"):
            if debug:
                if data.get("error"):
                    print(data.get("error").get("error_msg"))
            return False
        response = data.get("response")
        all_photo_count = response.get("count")  # Количество всех фотографий профиля
        photos = []  # Список всех загруженных фото
        max_size_photo = dict()  # Словарь с парой название фото - URL фото максимального разрешения

        # Создаём папку на компьютере для скачивания фотографий если ее нет
        if not os.path.exists("images_vk"):
            os.mkdir("images_vk")

        while i <= all_photo_count:
            if i != 0:
                photos_data = self.get_photos_request(i, count)
                print(f"photos_data: {photos_data}")

            # Проходимся по всем фотографиям
            items = response.get("items") if response.get("items") else []
            for photo in items:
                max_size = 0
                photos_info = {}
                # Выбираем фото максимального разрешения и добавляем в словарь max_size_photo
                for size in photo["sizes"]:
                    if size["height"] >= max_size:
                        max_size = size["height"]
                if photo["likes"]["count"] not in max_size_photo.keys():
                    max_size_photo[photo["likes"]["count"]] = size["url"]
                    photos_info["file_name"] = f"{photo['likes']['count']}.jpg"
                else:
                    max_size_photo[f"{photo['likes']['count']} + {photo['date']}"] = size["url"]
                    photos_info["file_name"] = f"{photo['likes']['count']}+{photo['date']}.jpg"

                # Формируем список всех фотографий для дальнейшей упаковки в .json

                photos_info["size"] = size["type"]
                photos.append(photos_info)

            # Скачиваем фотографии
            photos_list = []
            for photo_name, photo_url in max_size_photo.items():
                with open(f"images_vk/{photo_name}.jpg", "wb") as imj_file_io:
                    photos_list.append([photo_name, photo_url])
                    img = requests.get(photo_url)
                    imj_file_io.write(img.content)

            print(f"Загружено {len(max_size_photo)} фото")
            if type(count) is not int:
                count = int(count)
            i += count
            # Записываем данные о всех скачанных фоторафиях в файл .json
            json_save(photos, "photos.json")
            return True
