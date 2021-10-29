import requests
from pprint import pprint
import os
import json
from tqdm import tqdm
import configparser

# Конфигурационный файл config.ini подставить токены и id vk
config = configparser.ConfigParser()
config.read("config.ini")
ID_VK = config['ID_VK']['ID']
TOKEN_VK = config['TOKEN_VK']['TOKEN']
YANDEX_TOKEN = config['TOKEN_YA']['TOKEN']


class Backup_photo():

    def __init__(self, id, token: str):

        self.id = id
        self.token = token

    def authorization(self, count=5, album='profile'):

        method_vk = 'https://api.vk.com/method/photos.get'
        param = {
          'owner_id': self.id,
          'album_id': f'{album}',
          'photo_sizes': 1,
          'extended': 1,
          'count': count,
          'access_token' : self.token,
          'v': 5.131
        }

        if requests.get(method_vk, params=param).status_code > 201:

            print('Произошла ошибка авторизации на сервере')

        else:

            response = requests.get(method_vk, params=param).json()['response']
            return response
        
    def get_photo(self, num=5, path='images'):

        response = self.authorization(num)
        self.path = path
        to_json = []

        if os.path.exists(path) == False:

           os.mkdir(path)

        for photo in tqdm(response['items']):

            photo_size = photo['sizes'][-1]['type']
            photo_url = photo['sizes'][-1]['url']
            likes = photo['likes']['count']
            date = photo['date']
            photo_item = requests.get(photo_url)
            photo_info = {}

            if os.path.exists(f'{path}/{likes}.jpg') == False:

                with open(f'{path}/{likes}.jpg', 'wb') as img:

                    img.write(photo_item.content)
                    photo_info['file_name:'] = f'{likes}.jpg'
                    photo_info['size'] = f'{photo_size}'
                    to_json.append(photo_info)

            elif os.path.exists(f'{path}/{date}.jpg') == False:
                
                with open(f'{path}/{date}.jpg', 'wb') as img:

                   img.write(photo_item.content)
                   photo_info['file_name:'] = f'{date}.jpg'
                   photo_info['size'] = f'{photo_size}'
                   to_json.append(photo_info)

        print('Фото загружены')

        
        with open('log.json', 'w')as file:

            json.dump(to_json, file, indent=4)

        
    def get_album(self, alb=1, numbers=5, path='album'):

        self.numbers = numbers
        self.path = path
        data_json = {}
        to_json = {}

        if os.path.exists(path) == False:

            os.mkdir(path)
        
        album_arr = []
        method_vk = 'https://api.vk.com/method/photos.getAlbums'
        param = {
          'owner_id': self.id,
          'count': alb,
          'photo_sizes': 1,
          'extended': 1,
          'access_token' : self.token,
          'v': 5.131
        }

        response = requests.get(method_vk, params=param).json()['response']
        
        for album in response['items']:

            album_arr.append(album['id'])
            
        for i in tqdm(album_arr):

            response = self.authorization(numbers, i)

            for img in response['items']:

                img_name = img['date']
                to_json[img_name] = img['id']
                img = requests.get(img['sizes'][-1]['url'])
                

                
                with open(f'{path}/{img_name}.jpg', 'wb')as file:

                    file.write(img.content)
           
        print('Альбомы загружены')
        

class Ya_uploader():

    def __init__(self, token: str):

        self.token = token

    def authorization(self):

        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }
    
    def upload_link(self, file_path: str):

        upload_link = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.authorization()
        params = {"path": file_path, "overwrite": "true"}
        response = requests.get(upload_link, headers=headers, params=params)

        return response.json()  
               
    def upload(self, file_path='images'):

        href = self.upload_link(file_path=file_path).get("href", "")
        response = requests.put(href, data=open(file_path, 'rb'))

    def create_folder(self, folder='images'):

        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.authorization()
        params = {"path": folder}
        response = requests.put(url, headers=headers, params=params)
    
    def upload_files(self, files='images'):

         self.create_folder(files)
         self.files = files
         path = files
         files = os.listdir(files)

         for img in tqdm(files):

            self.upload(f'{path}/{img}')
            
         print('Данные отправлены на яндекс диск')

   


        

                
        
if __name__ == '__main__':
    backup_photo_1 = Backup_photo(ID_VK, TOKEN_VK).get_photo()   #Указать число фото, по умолчанию 5, путь куда будут падать фото
    backup_photo_1_disk = Ya_uploader(YANDEX_TOKEN).upload_files() # указать название папки на яндекс диске. По умолчанию images
    # backup_photo_album = Backup_photo(ID_VK, TOKEN_VK).get_album(5, 4,'album')  #1 количество альбомов, чилсо фотографий и путь
    # backup_photo_album_disk = Ya_uploader(YANDEX_TOKEN).upload_files('album') 
            

        


    






            




    



    
    
    