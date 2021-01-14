import os
import requests
import psycopg2
import data

from time import sleep

from telethon import TelegramClient, events, sync
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class Parser:
    def parser_links(self):
        URL =  bot.site_link + '/best/'
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        }

        response = requests.get(URL, headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.findAll('div', class_='download')

        links = []
        for item in items:
            if item.find('a', href=True)['href'][0] == '/':
                links.append(
                    item.find('a', href=True)['href']
                )
        return links

    def music_in_db(self, music):
        connection = psycopg2.connect(
            host='127.0.0.1',
            database='music',
            user='postgres',
            password=data.db_password,
            port=''
        )

        connection.autocommit = True
        cur = connection.cursor()

        try:
            db_music = music.split('/')[-2]
            cur.execute(f"INSERT INTO music_links(url) VALUES('{db_music}')")
        except:
            return False
        finally:
            connection.close()
        return True

    def send_music(self, music):
        api_id = data.api_id
        api_hash = data.api_hash

        client = TelegramClient('music', api_id, api_hash)
        client.start()
        client.send_file('https://t.me/top_tracksss', music)

    @property
    def download_music(self):
        path = os.getcwd()

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        preferences = {'download.default_directory': path + '/music'}
        options.add_experimental_option('prefs', preferences)

        for link in self.parser_links():
            if self.music_in_db(link):
                print('start')
                driver = webdriver.Chrome(path + '/chromedriver', chrome_options=options)
                driver.get(data.site_link + link)
                driver.find_element_by_link_text('Скачать').click()
                sleep(30)
                driver.quit()

                try:
                    music_path = path + '/music/'
                    find_music = music_path + os.listdir(music_path)[0]
                    self.send_music(find_music)
                    os.remove(find_music)
                except FileNotFoundError:
                    pass
            else:
                pass
            sleep(600)
        else:
            sleep(43200)
            self.download_music()


if __name__ == '__main__':
    music = Parser()
    music.download_music
