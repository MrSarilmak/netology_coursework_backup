import yadisk
import os


class YaUploader:
    def __init__(self, token: str, yad_save_folder_name: str):
        self.yad_save_folder_name = yad_save_folder_name
        self.yad = yadisk.YaDisk(token=token)
        if self.yad.check_token():
            # print('Токен Яндекс диска верный')
            self.token = token
        else:
            # print('Токен Яндекс диска неверный')
            self.token = ""

    def folder_creation(self, folder_name):
        self.yad.mkdir(folder_name)

    def upload(self, folder_name):
        photos = 0
        for address, _, files in os.walk(folder_name):
            for file in files:
                try:
                    self.yad.upload(f'{address}/{file}', f'/{self.yad_save_folder_name}/{file}')
                    print(f"Файл {file} загружен")
                    photos += 1
                except:
                    print(f"Файл {file} уже был загружен ранее")
        return photos
