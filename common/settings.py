import configparser


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


class ListConfigParser(configparser.ConfigParser):
    def __init__(self):
        super().__init__()

    def __getitem__(self, key):
        section_proxy = super().__getitem__(key)
        return ListSectionProxy(section_proxy)


full_settings = ListConfigParser()
full_settings.read("data/config.ini")

network_settings = full_settings["Network"]
mongo_settings = full_settings["Mongo"]
clean_settings = full_settings["Clean"]
annotate_settings = full_settings["Annotate"]
download_settings = full_settings["Download"]
urls_settings = full_settings["Urls"]
