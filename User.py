class inadduser:
    def __init__(self,id,name,path=""):
        self.id =id;
        self.name =name;
        self.path = path;
        pass
    def __str__(self): 
        i = "{"
        o ="}"
        return f'''{i}
            id:{self.id},
            name:{self.name},
            path:{self.path}
        {o}''';
    def tojson(self):
        i = "{"
        o ="}"
        return f'''{i}
            "id":{self.id},
            "name":"{self.name}",
            "path":"{self.path}"
        {o}''';
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

