import argparse
import logging
import shutil
from contextlib import contextmanager
from datetime import datetime
from os import path, makedirs
from time import sleep
from urlparse import urlsplit

import requests

try:
    import gi

    gi.require_version('GExiv2', '0.10')
    from gi.repository.GExiv2 import Metadata as exiv_file
except:
    class exiv_file:
        def __init__(self, filepath):
            pass

        def set_date_time(self, date):
            pass

        def save_file(self):
            pass

from tuenti import TuentiSocialMessenger

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

retry_delays = [0, 2, 5, 10, 15, 15, 15, 15, 15, 30, 30]  # One more


@contextmanager
def really_retry():
    retries = 0
    while retries < 10:
        try:
            yield
            return
        except Exception as e:
            logger.exception("Failed but retrying for %d-th time", retries)
            sleep(retry_delays[retries])
            retries += 1
            if retries >= 10:
                logger.error("Giving up!")
                raise e


def get_user_album_photos(tsm, user=None):
    page = 0
    while True:
        with really_retry():
            if user:
                res = tsm.Profile_getAlbumPhotos({'page': page, 'pageSize': 1000, 'userId': user})
            else:
                res = tsm.Profile_getAlbumPhotos({'page': page, 'pageSize': 1000})
        for item in res['items']:
            yield item
        if not res['hasMore']:
            return
        page += 1


def gen_file_path(file_uri):
    _, _, uri_path, _, _ = urlsplit(file_uri)
    _, _, name = uri_path.rpartition('/')
    name = '%s.jpg' % name
    if not path.exists('dl'):
        makedirs('dl')
    file_path = path.join('dl', name)
    if path.exists(file_path):
        return None
    return file_path


class FileDownloader:
    def __init__(self):
        self.dl = requests.Session()

    def download_file(self, file_uri, file_path):
        with really_retry():
            r = self.dl.get(file_uri, stream=True)
            if r.status_code == 200:
                with open(file_path, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
                return True
            else:
                return False

    def save_photo(self, photo):
        file_uri = photo['photo']['fullUrl']
        file_path = gen_file_path(file_uri)
        ts = long(photo['photo']['timestamp'])
        if not file_path:
            logger.debug('Skipping file %s', file_uri)
            return
        logger.debug('Downloading file %s', file_path)
        if self.download_file(file_uri, file_path):
            logger.debug('Done')
            update_ts(file_path, ts)
        else:
            logger.debug('Failed')


def update_ts(file, timestamp):
    try:
        ef = exiv_file(file)
        ef.set_date_time(datetime.fromtimestamp(timestamp))
        ef.save_file()
    except Exception as e:
        logger.exception('Something happened when writting time metadata in file %s', file);


class IDCollector():
    def __init__(self):
        self.todo = set()
        self.done = set()
        self.user_id = ''

    def iterate(self):
        while self.todo:
            item = self.todo.pop()
            self.done.add(item)
            yield item

    def add(self, item):
        if item in self.done:
            return
        if len(self.todo) == 0 and len(self.done) == 1:
            self.user_id = item
        self.todo.add(item)

    def collect_ids(self, photo):
        self.add(photo['authorId'])
        for comment in photo['lastComments']:
            self.add(comment['authorId'])
        for tag in photo['photo']['tags']:
            self.add(tag['userId'])
        self.add(photo['photo']['uploaderId'])

    def is_photo_collectable(self, photo):
        if not self.user_id:
            return True
        if self.user_id == photo['authorId']:
            return True
        for comment in photo['lastComments']:
            if comment['authorId'] == self.user_id:
                return True
        for tag in photo['photo']['tags']:
            if tag['userId'] == self.user_id:
                return True
        if photo['photo']['uploaderId'] == self.user_id:
            return True
        return False

    def gen_log_message(self):
        done_len = len(self.done)
        logger.info('Users %d/%d', done_len, done_len + len(self.todo))


def main():
    args_eng = argparse.ArgumentParser(description='Tuenti image downloader', add_help=True)
    args_eng.add_argument('user', help='Tuenti login email')
    args_eng.add_argument('pwd', help='Tuenti password')
    args = args_eng.parse_args()

    tsm = TuentiSocialMessenger.from_credentials(args.user, args.pwd)
    file_downloader = FileDownloader()

    collector = IDCollector()
    collector.add('')

    total_count = 0
    saved_count = 0

    for user_id in collector.iterate():
        logger.debug("Inspecting user %s", user_id)
        collector.gen_log_message()
        for photo in get_user_album_photos(tsm, user_id):
            total_count += 1
            if collector.is_photo_collectable(photo):
                collector.collect_ids(photo)
                saved_count += 1
                file_downloader.save_photo(photo)
            if saved_count and not total_count % 100:
                logger.info("Downloaded %d/%d photos", saved_count, total_count)


if __name__ == '__main__':
    main()
