import json
import os

import requests
import yadisk

vk_user_id = ""
vk_access_token = ""
yad_token = ""
yad_save_folder_name = "vk_avatar_save"


def json_save(data: dict | list, file_name: str) -> None:
    with open(file_name, "w") as file_io:
        json.dump(data, file_name, indent=2)


class VkDownloader:

    def __init__(self, token, app_id):
        self.token = token
        self.app_id = app_id

    def get_photos(self, offset=0, count=50):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.app_id,
                  'album_id': 'profile',
                  'access_token': self.token,
                  'v': '5.131',
                  'extended': '1',
                  'photo_sizes': '1',
                  'count': count,
                  'offset': offset
                  }
        res = requests.get(url=url, params=params)
        return res.json()

    def get_all_photos(self):
        data = self.get_photos()
        print(data)
        if data is None:
            return None
        if not data.get('response'):
            return None
        all_photo_count = data.get('response').get('count')  # Количество всех фотографий профиля
        i = 0
        count = 50
        photos = []  # Список всех загруженных фото
        max_size_photo = {}  # Словарь с парой название фото - URL фото максимального разрешения

        # Создаём папку на компьютере для скачивания фотографий
        if not os.path.exists('images_vk'):
            os.mkdir('images_vk')

        while i <= all_photo_count:
            if i != 0:
                data = self.get_photos(offset=i, count=count)

            # Проходимся по всем фотографиям
            for photo in data['response']['items']:
                max_size = 0
                photos_info = {}
                # Выбираем фото максимального разрешения и добавляем в словарь max_size_photo
                for size in photo['sizes']:
                    if size['height'] >= max_size:
                        max_size = size['height']
                if photo['likes']['count'] not in max_size_photo.keys():
                    max_size_photo[photo['likes']['count']] = size['url']
                    photos_info['file_name'] = f"{photo['likes']['count']}.jpg"
                else:
                    max_size_photo[f"{photo['likes']['count']} + {photo['date']}"] = size['url']
                    photos_info['file_name'] = f"{photo['likes']['count']}+{photo['date']}.jpg"

                # Формируем список всех фотографий для дальнейшей упаковки в .json

                photos_info['size'] = size['type']
                photos.append(photos_info)

            # Скачиваем фотографии
            photos_list = []
            for photo_name, photo_url in max_size_photo.items():
                with open(f'images_vk/{photo_name}.jpg', 'wb') as file_io:
                    photos_list.append([photo_name, photo_url])
                    img = requests.get(photo_url)
                    file_io.write(img.content)

            print(f'Загружено {len(max_size_photo)} фото')
            i += count
            # Записываем данные о всех скачанных фоторафиях в файл .json
            json_save(photos, "photos.json")


class YaUploader:
    def __init__(self, token: str):
        self.token = token
        self.y = yadisk.YaDisk(token=self.token)
        # print(self.y.check_token())

    def folder_creation(self, folder_name):
        self.y.mkdir(folder_name)

    def upload(self, folder_name):
        photos = 0
        for address, _, files in os.walk(folder_name):
            for file in files:
                # print(f'Файл {file} загружен')
                photos += 1
                self.y.upload(f'{address}/{file}', f'/{yad_save_folder_name}/{file}')
        return photos


def main():
    user_id = vk_user_id if vk_user_id else input('Введите id пользователя VK: ')
    downloader = VkDownloader(vk_access_token, user_id)
    downloader.get_all_photos()

    ya_token = yad_token if yad_token else input('Введите токен Яндекс диска: ')
    if not ya_token:
        print('Вы не ввели токен Яндекс диска')
        return None
    uploader = YaUploader(ya_token)
    folder_name = yad_save_folder_name if yad_save_folder_name else input(
        'Введите имя папки на Яндекс диске, в которую необходимо сохранить фото: ')
    if not folder_name:
        print('Вы не ввели имя папки')
        return None
    try:
        uploader.folder_creation(folder_name)
    except yadisk.exceptions.DirectoryExistsError:
        # print('Папка уже существует')
        pass

    if not os.path.exists('images_vk'):
        os.mkdir('images_vk')
    files_path = os.getcwd() + '\images_vk\\'
    result = uploader.upload(files_path)
    if result is None:
        return None
    print(f'Фотографий загружено на Яндекс диск: {result}')


if __name__ == '__main__':
    main()
