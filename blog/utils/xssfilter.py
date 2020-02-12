from bs4 import BeautifulSoup


class XSSFilter(object):
    __instance = None

    def __init__(self):
        self.valid_tags ={
            "script": [],   
        }

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            obj =object.__new__(cls, *args, **kwargs)
            cls.__instance = obj
        return cls.__instance

    def process(self, content):
        soup = BeautifulSoup(content, "lxml")  # lxml解析器
        for tag in soup.find_all(recursive=True):
            if tag.name in self.valid_tags:
                print(tag.name)
                tag.hidden = True
                tag.clean()

        return soup.renderContents()