"""
https://oauth.vk.com/blank.html#access_token=vk1.a.fy7waudzliIGoyTwXEZ9AJZq12iIDOTC_5cGyP6UkXvkrcjDwofBgwDL8jeWcekDRSHUopnDa8frLBBuSNdNia3IoC3DIQA768v8YQRMhO1o1cgrVJ_RlUAJROzvjp66Qixv6ipcZy9sbt6AyLVR26ofHPU-JlfJwNYlEb08ruKkrh5T5JvgowTM8kuVdH0l&expires_in=86400&user_id=325931
325931
"""

with open("tokenVK.txt", "r") as file_object:
    vk_token = file_object.read().strip()


import requests
from pprint import pprint
import json
from datetime import datetime
from tqdm import tqdm

class VK:

    def __init__(self, vk_token, base_url: str = 'https://api.vk.com/method/'):
        self.vk_token = vk_token
        self.url = base_url
        self.params = {
            'access_token': vk_token,
            'v': '5.131'
        }


    def get_photo(self, vk_id: str):
        """
        Метод запрашивает фото профиля пользователя и возвращает json-файл с информацией о фото.
        :vk_id  id пользователя VK
        """

        count = int(input('Введите количество фотографий для получения: '))
        album_id = input('Выберите (из предложенного списка) из какого альбома начать скачку фотографий, '
                         'и введите в соответствии с названием:\n'
                         'wall - фотографии со стены\n'
                         'profile - фотографии профиля\n'
                         'saved -  сохраненные фотографии. Возвращается только с ключом доступа пользователя.\n'
                         'Ввод: ')
        url_photo = self.url + 'photos.get'

        params = {
            "owner_id": vk_id,
            "album_id": album_id,
            "extended": "likes",
            "photo_sizes": "1",
            "count": count
        }
        res = requests.get(url_photo, params={**self.params, **params}).json()
        return res['response']['items']

    def parsed_photo(self, photos_info: list):
        """
        Метод парсит json-файл с профиля пользователя VK
        :param photos_info: json файл с описанием фото пользователя VK
        :return: список словарей с url на фотографии
        """
        type_sizes = ['w', 'z', 'y', 'x', 'm', 's']
        user_profile_photos = []
        for photo in photos_info:
            photo_dict = {}
            name_photo = str(photo['likes']['count'])
            for user_photo in user_profile_photos:
                if user_photo['name'] == name_photo:
                    name_photo += f"({datetime.utcfromtimestamp(int(photo['date'])).strftime('%Y-%m-%d')})"
            for alpha in type_sizes:
                size = [x for x in photo['sizes'] if x['type'] == alpha]
                type_size = alpha
                if size:
                    break

            photo_dict.setdefault('name', name_photo)
            photo_dict.setdefault('url', size[0]['url'])
            photo_dict.setdefault('type_size', type_size)
            user_profile_photos.append(photo_dict)

        return user_profile_photos

# pprint(VK.parsed_photo(vk_photos, VK.get_photo(vk_photos, '325931')))

def get_token():
    with open('token.txt', 'r') as file:
        return file.readline()

class YandexDisk:

    def __init__(self, token):
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        self.token = token

    @property
    def headers(self):
        return {
            'Content-Type': "application/json",
            'Authorization': f'OAuth {self.token}'
        }

    def create_folder(self, path):
        requests.put(f'{self.url}?path={path}', headers=self.headers)

    def upload_file(self, files: list, name_dir: str):
        """
        Метод загружает на Яндекс Диск пользователя фото
        :param files: Список со словарями, которые содержат ссылки на фото
        :param name_dir: Наименование папки, в которую необходимо совешить загрузку
        :return: Прогресс-бар с ходом загрузки, результат загрузки и создает json-файл с информацией
        о загруженных фотографиях.
        """
        upload_url = self.url + 'upload'
        data_json = []

        for file in tqdm(files, desc="Loading: ", ncols=100, colour='green'):
            params_for_upload = {
                'url': file['url'],
                'path': f"{name_dir}/{file['name']}",
                'disable_redirects': 'true'
            }
            res = requests.post(upload_url, params=params_for_upload, headers=self.headers)
            status = res.status_code
            data = {
                        "file_name": f"{file['name']}.jpg",
                        "size": file['type_size']
                }
            data_json.append(data)
        with open('data.json', 'a') as outfile:
            json.dump(data_json, outfile, indent=0)

        if 400 > status:
            print(f'Фотографии загружены на: https://disk.yandex.ru/client/disk/{name_dir}')
        else:
            print('Ошибка загрузки:', status)

vk_photos = VK(vk_token = vk_token)
yandex_client = YandexDisk(get_token())
yandex_client.create_folder('project')
yandex_client.upload_file(VK.parsed_photo(vk_photos, VK.get_photo(vk_photos, '325931')), 'project')