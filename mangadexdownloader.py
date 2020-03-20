import coloredlogs
import cloudscraper
import logging
import yaml
import os
import tqdm
import pushover
import re
import pathlib

from pathvalidate import sanitize_filename

class mangadex():
    log = logging.getLogger("MangaDexDownloader")
    config = {}
    current_manga = {"json": {}, "config": {}}

    def __init__(self):
        self.load_config()
        self.scraper = cloudscraper.create_scraper()
    
    def start(self):
        for manga in reversed(self.config['mangas']):
            self.download_manga(manga)
        
    def notify_chapter(self, chapter_json):
        if not self.config['pushover']['enabled']:
            return
        
        if self.current_manga['config']['check_last']:
            return
        
        push = pushover.Client(self.config['pushover']['user'], api_token=self.config['pushover']['token']) 
        coverPath = pathlib.Path(self.config['downloadpath']).joinpath(self.current_manga['config']['name']).joinpath("cover.jpg")
        if coverPath.exists():
            with open(coverPath, 'rb') as image:
                push.send_message(f"New chapter of {self.current_manga['config']['name']}, \
                                    chapter {chapter_json['chapter']}! Title: {chapter_json['title']}", 
                                    attachment=image)
        else:
            push.send_message(f"New chapter of {self.current_manga['config']['name']}, \
                                    chapter {chapter_json['chapter']}! Title: {chapter_json['title']}")
        
    def get_boolean_option(self, config: dict, option: str, ) -> bool:
        if option in config:
            return config[option]
        return False
    
    def load_config(self):
        with open("config.yml", "rb") as fconfig:
            self.config = yaml.load(fconfig, Loader=yaml.FullLoader)
    
    def api_get_manga(self, manga_id: int) -> dict:
        resp = self.scraper.get(f"https://mangadex.org/api/manga/{manga_id}/").json()
        
        if "manga" in resp and "title" in resp['manga']:
            return resp
        
        raise Exception(f"{manga_id} is an invalid mangadex manga")

    def get_cover(self):
        coverPath = pathlib.Path(self.config['downloadpath']).joinpath(self.current_manga['config']['name']).joinpath("cover.jpg")

        if not coverPath.exists():
            resp = self.scraper.get(f"https://mangadex.org/{self.current_manga['json']['manga']['cover_url']}")
            
            if resp.status_code == 200:
                with open(coverPath, "wb") as fout:
                    fout.write(resp.content)

    def get_chapters(self, lang: str) -> list:
        chapters_sorted = []

        for chapter_id in self.current_manga['json']['chapter']:
            chapter = self.current_manga['json']['chapter'][str(chapter_id)]
            if chapter['lang_code'] == lang and chapter['group_name'] in self.current_manga['config']['group']:
                chapter['id'] = chapter_id
                if chapter['chapter'] == "":
                    chapter['chapter'] = 0
                    
                chapters_sorted.append(chapter)

        chapters_sorted.sort(key=lambda x: float(x['chapter']))
        
        if self.get_boolean_option(self.current_manga['config'], "check_last"):
            return chapters_sorted[len(chapters_sorted)-self.config['check_last_items']:]
        return chapters_sorted
    
    
    def download_chapter(self, chapter: dict): 
        chapter_path = pathlib.Path(self.config['downloadpath']).joinpath(self.current_manga['config']['name'])
        
        if self.get_boolean_option(self.config['naming'], "volumes"):
            if chapter["volume"] == "":
               chapter_path.joinpath("Unknown volume")
            else:
                chapter_path.joinpath(f"Volume {chapter['volume']}")
            
        chapter_path = chapter_path.joinpath(f"Chapter {chapter['chapter']} [{sanitize_filename(chapter['group_name'])}]")
        os.makedirs(chapter_path, exist_ok=True)
        
        chapter_json = self.scraper.get(f"https://mangadex.org/api/chapter/{chapter['id']}/").json()
        
        if len(os.listdir(chapter_path)) == len(chapter_json['page_array']):
            self.log.info(f"{self.current_manga['json']['manga']['title']} Chapter {chapter['chapter']} already downloaded, skipping.")
            return
        
        progress_bar = tqdm.tqdm(total=len(chapter_json['page_array']), unit="page", 
                                 desc=f"{self.current_manga['json']['manga']['title']} Chapter: {chapter['chapter']}")
        
        total_pages_number = len(str(len(chapter_json['page_array'])))
        for image in chapter_json['page_array']:
            image_url = f"{chapter_json['server']}{chapter_json['hash']}/{image}"
            image_ext = pathlib.Path(image).suffix
            
            page_num = re.findall('([\d]+)', image)[0].zfill(total_pages_number)
            image_path = pathlib.Path(chapter_path.joinpath(f"{page_num}{image_ext}"))
            
            if not image_path.exists():
                resp = self.scraper.get(image_url)
            
                with open(image_path, "wb") as fout:
                    fout.write(resp.content)
                os.utime(image_path, (chapter_json['timestamp'], chapter_json['timestamp']))
            progress_bar.update(1)
        
        progress_bar.close()
        os.utime(chapter_path, (chapter_json['timestamp'], chapter_json['timestamp']))
        self.notify_chapter(chapter_json)

    
    def download_chapters(self, manga_config: dict, manga_json: dict):
        chapters = self.get_chapters("gb")
        
        for chapter in chapters:
            self.download_chapter(chapter)
        
    def download_manga(self, manga_config: dict):
        self.log.info(f"Processing manga {manga_config['name']} ({manga_config['id']})")
        self.current_manga['config'] = manga_config
        self.current_manga['json'] = self.api_get_manga(manga_config['id'])

        downloadPath = pathlib.Path(self.config['downloadpath']).joinpath(manga_config['name'])
        downloadPath.mkdir(parents=True, exist_ok=True)

        if self.get_boolean_option(manga_config, "cover"):
            self.get_cover()
        
        self.download_chapters(self.current_manga['config'], self.current_manga['json'])
    

logging.basicConfig(level=logging.INFO)
coloredlogs.install(level='INFO', fmt="%(asctime)s %(name)s %(levelname)s %(message)s")    
md = mangadex()
md.start()

