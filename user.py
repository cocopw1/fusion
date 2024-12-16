class inadduser:
    def __init__(self,id,name):
        self.id =id;
        self.name =name;
        self.progress = 0;
        pass
class user:
    def __init__(self,id:int,name:str,amt:int,path:str):
        self.id =id;
        self.name =name;
        self.amt =amt;
        self.path =path;
        pass
    def getdette(self):
        return self.amt;
    def __str__(self):
        return f"{self.name}' '{self.amt}"
    def tojson(self):
        i = "{"
        o ="}"
        return f'''{i}
            "id":{self.id},
            "name":"{self.name}",
            "amt":{self.amt},
            "path":"{self.path}"
        {o}''';

