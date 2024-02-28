
APP_ID = '51856200'  
MY_VK_ID = '17294014'
YD_FOLDER = 'VK-photos'

import requests
import logging
import webbrowser
import json

class VKAPIClient:

    def __init__(self, token, app_id):
        self.token = token
        self.app_id = app_id
        self.API_BASE_URL = 'https://api.vk.com/method/'

    def get_VK_token(self):
        webbrowser.open(
            f'https://oauth.vk.com/authorize?client_id={self.app_id}'
            '&display=page&redirect_uri=https://example.com/callback'
            '&scope=friends&response_type=token&v=5.131&state=123456', 
            new=2, autoraise=False)

    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.199',
            'extended': '1'
            }

    def get_photos(self, owner_id, album_id):
        params = self.get_common_params()
        params.update({'owner_id': owner_id})
        params.update({'album_id': album_id})
        response = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        return response.json()
        
class YDAPIClient:

    API_BASE_URL = 'https://cloud-api.yandex.net/v1/disk'

    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': token
            }

    def upload_file(self, file_name, file_url ):
        params = {'path': file_name, 'url': file_url}
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        response = requests.post(url, headers=self.headers, params=params)
        return response.json()

    def create_folder(self, folder_name):
        url = f'{self.API_BASE_URL}/resources'
        print(url)
        params = {'path': folder_name}
        response = requests.put(url, headers=self.headers, params=params)
        return response.json()


if __name__ == '__main__':

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("photobackup.log"),
            logging.StreamHandler()
        ]
    )

    vk_client = VKAPIClient(API_VK_TOKEN, APP_ID)
    #vk_client.get_VK_token()
    vk_owner_id = input('Введите id владельца альбома ВК:') or '17294014'

    photos = vk_client.get_photos(vk_owner_id, 'profile')
    if 'error' in photos:
        logging.error(f"Ошибка: {photos['error']['error_msg']}")
        quit()
    else:
        logging.info(
                f'В альбоме profile фотографий: {photos["response"]["count"]}')
        number_photos = input('Сколько фотографий сохраняем, 5?') or 5
        number_photos = int(number_photos)
    yd_token = input('Введите токен Яндекс Полигона:') or YD_TOKEN
    yd_client = YDAPIClient(yd_token)
    folder_response = yd_client.create_folder(YD_FOLDER)
    if 'error' in folder_response:
        if folder_response['error'] == 'DiskPathPointsToExistentDirectoryError':
            logging.info(folder_response['message'])
            logging.info('Используем существующую папку')
        else:
            logging.error(folder_response['message'])
            quit()
    else:
        logging.info('Папка создана')

    photos_list =[]
    for item in photos['response']['items'][0:number_photos]:
        max_sized_photo = max(item['sizes'], 
                key = lambda x: x['height']*x['width'])
        photo_name = (YD_FOLDER + '/' + str(item['likes']['count'])
                     + '.jpg')
        upload_photo_response = yd_client.upload_file(photo_name, 
                                                   max_sized_photo['url'])
        logging.info(f'{photo_name} загружено на Яндекс Диск')
        photos_list.append({'file_name': photo_name,
                        'size': max_sized_photo['type']})
          
    with open('photos_list.json', 'w') as fp:
        json.dump(photos_list, fp)
    logging.info('Список файлов сохранен в photos_list.json')
