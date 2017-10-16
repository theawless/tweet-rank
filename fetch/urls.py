import collections

import bs4
import tornado
import tornado.httpclient
import tornado.ioloop
from tqdm import tqdm

import common.mongo
import common.settings


# taken from https://github.com/tornadoweb/tornado/issues/1400
class BacklogClient(object):
    def __init__(self):
        self.max_concurrent_requests = common.settings.urls.getint("MaxConcurrentRequests")
        self.client = tornado.httpclient.AsyncHTTPClient(max_clients=self.max_concurrent_requests)
        self.client.configure(None, defaults=dict(connect_timeout=common.settings.urls.getint("ConnectTimeout"),
                                                  request_timeout=common.settings.urls.getint("RequestTimeout")))
        self.backlog = collections.deque()
        self.concurrent_requests = 0

    def __get_callback(self, func):
        def wrapped(*args, **kwargs):
            self.concurrent_requests -= 1
            self.try_run_request()
            return func(*args, **kwargs)

        return wrapped

    def try_run_request(self):
        while self.backlog and self.concurrent_requests < self.max_concurrent_requests:
            request, callback = self.backlog.popleft()
            self.client.fetch(request, callback=callback)
            self.concurrent_requests += 1

    def fetch(self, request, callback=None):
        wrapped = self.__get_callback(callback)
        self.backlog.append((request, wrapped))
        self.try_run_request()


class UrlFetcher:
    def __init__(self):
        self.backlog = BacklogClient()

    def handle_request(self, response, url):
        self.tqdm.update(1)
        try:
            soup = bs4.BeautifulSoup(response.body)
            url["text"] = soup.title.string
            common.mongo.urls_collection.update_one({"id_str": url["id_str"]}, {"$set": url})
        except Exception:
            if common.settings.urls.getboolean("RemoveUrlNotFound"):
                common.mongo.urls_collection.remove({"id_str": url["id_str"]})

        if not self.backlog.backlog and self.backlog.concurrent_requests == 0:
            tornado.ioloop.IOLoop.instance().stop()

    def _start_fetch(self, url):
        self.backlog.fetch(tornado.httpclient.HTTPRequest(url["expanded_url"], method='GET', headers=None),
                           lambda response: self.handle_request(response, url))

    def launch(self, urls):
        print("filling urls")
        self.tqdm = tqdm(total=len(urls))
        for url in urls:
            self._start_fetch(url)
        tornado.ioloop.IOLoop.current().start()


def urls():
    UrlFetcher().launch(common.mongo.get_urls())


if __name__ == "__main__":
    urls()
