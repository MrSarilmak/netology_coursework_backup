import json
import os
import sys

import yadisk

from vk_downloader import VkDownloader
from yadisk_uploader import YaUploader

if os.path.exists("settings.json"):
    config = json.load(open("settings.json", "rt"))
    vk_user_id = config.get("vk_user_id")
    vk_access_token = config.get("vk_access_token")
    vk_images_count = config.get("count")
    yad_token = config.get("yad_token")
    yad_save_folder_name = config.get("yad_save_folder_name")
else:
    vk_user_id = ""
    vk_app_id = ""
    vk_access_token = ""
    vk_images_count = 0
    yad_token = ""
    yad_save_folder_name = ""


def main():
    global vk_images_count
    global vk_access_token
    user_id = vk_user_id if vk_user_id else input("Введите id пользователя VK: ")
    # print(f"vk_access_token = {vk_access_token}")
    vk_access_token = vk_access_token if vk_access_token else input(
        "Введите токен доступа к API ВКонтакте: "
    )
    downloader = VkDownloader(vk_access_token, user_id)
    vk_images_count = vk_images_count if vk_images_count else input("Введите количество загружаемых фото: ")
    res1 = downloader.get_photos(vk_images_count)
    if not res1:
        print("Ошибка получения фотографий")
        return -1

    ya_token = yad_token if yad_token else input("Введите токен Яндекс диска: ")
    if not ya_token:
        print("Вы не ввели токен Яндекс диска")
        return -2
    folder_name = yad_save_folder_name if yad_save_folder_name else input(
        "Введите имя папки на Яндекс диске, в которую необходимо сохранить фото: ")
    if not folder_name:
        print("Вы не ввели имя папки")
        return -3
    uploader = YaUploader(ya_token, folder_name)
    try:
        uploader.folder_creation(folder_name)
    except yadisk.exceptions.DirectoryExistsError:
        # print("Папка уже существует")
        pass

    if not os.path.exists("images_vk"):
        os.mkdir("images_vk")
    # files_path = "C:/Users/muraa/Downloads/CourseWork-main/images_vk/"
    # files_path = os.getcwd() + "/images_vk/"
    files_path = "images_vk/"
    result = uploader.upload(files_path)
    if result is None:
        return -4
    print(f"Фотографий загружено на Яндекс диск: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
