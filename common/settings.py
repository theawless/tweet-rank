from configparser import ConfigParser


class ListSectionProxy:
    def __init__(self, section_proxy):
        self.section_proxy = section_proxy

    def __getattr__(self, attr):
        return self.section_proxy.__getattribute__(attr)

    def getstring(self, item):
        return self.section_proxy.get(item)

    def getstringlist(self, item):
        return self.getstring(item).split(",")

    def getintlist(self, item):
        return [int(string) for string in self.getstringlist(item)]

    def getfloatlist(self, item):
        return [float(string) for string in self.getstringlist(item)]


class ListConfigParser(ConfigParser):
    def __init__(self):
        super().__init__()

    def __getitem__(self, key):
        section_proxy = super().__getitem__(key)
        return ListSectionProxy(section_proxy)


all_settings = ListConfigParser()
all_settings.read("data/config.ini")

network_settings = all_settings["Network"]
mongo_settings = all_settings["Mongo"]
clean_settings = all_settings["Clean"]
annotate_settings = all_settings["Annotate"]
download_settings = all_settings["Download"]
urls_settings = all_settings["Urls"]
