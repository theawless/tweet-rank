import collections
import time

import bs4
import tornado
import tornado.httpclient
import tornado.ioloop

import common.mongo
import common.settings


# taken from https://github.com/tornadoweb/tornado/issues/1400
class BacklogClient(object):
    max_concurrent_requests = common.settings.urls_settings.getint("MaxConcurrentRequests")

    def __init__(self, ioloop):
        self.ioloop = ioloop
        self.client = tornado.httpclient.AsyncHTTPClient(max_clients=self.max_concurrent_requests)
        self.client.configure(None, defaults=dict(connect_timeout=200, request_timeout=300))
        self.backlog = collections.deque()
        self.concurrent_requests = 0

    def __get_callback(self, function):
        def wrapped(*args, **kwargs):
            self.concurrent_requests -= 1
            self.try_run_request()
            return function(*args, **kwargs)

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
        self.counter = 0

    def handle_request(self, response, url):
        self.counter += 1
        try:
            soup = bs4.BeautifulSoup(response.body)
            url["text"] = soup.title.string
            common.mongo.urls_collection.update_one({"id_str": url["id_str"]}, {"$set": url})
            common.mongo.urls_collection.save()
        except Exception:
            if common.settings.urls_settings.getboolean("RemoveUrlNotFound"):
                common.mongo.urls_collection.remove({"id_str": url["id_str"]})

        print(self.counter, response.code, url["expanded_url"], url["text"] if "text" in url else "")
        if not self.backlog.backlog and self.backlog.concurrent_requests == 0:
            tornado.ioloop.IOLoop.instance().stop()

    def _start_fetch(self, url):
        self.backlog.fetch(tornado.httpclient.HTTPRequest(url["expanded_url"], method='GET', headers=None),
                           lambda response: self.handle_request(response, url))

    def launch(self, urls):
        self.ioloop = tornado.ioloop.IOLoop.current()
        self.backlog = BacklogClient(self.ioloop)
        for url in urls:
            self._start_fetch(url)
        self.ioloop.start()


def main():
    start_time = time.time()
    UrlFetcher().launch(common.mongo.get_urls())
    common.mongo.urls_collection.drop()
    elapsed_time = time.time() - start_time
    print(elapsed_time)


if __name__ == "__main__":
    main()
