import json
import User
# Charger la base de données JSON
def loaddb() -> list[User.user]:
    db = open("./db.json", "r")
    jons = json.load(db)
    db.close()
    data= jons['user']
    Users:list[User.user] = []
    for da in data:
        Users.append(User.user(da['id'],da['name'],da['amt'],da['path']))
    print(Users)
    db.close()
    return Users;

def writedb(Users:list[User.user]):
    db=open("db.json","w");
    str = """{
            "user":["""
    cpt = 0
    for user in Users:
        str+=user.tojson();
        if (cpt==len(Users)-1):
            continue;
        cpt+=1;
        str+=""",
        """
    str+="""]
    }"""
    print(str)
    db.write(str);
    db.close()

def loadadddb() -> list[User.inadduser]:
    db = open("./adddb.json", "r")
    jons = json.load(db)
    db.close()
    data= jons['inadduser']
    Users:list[User.inadduser] = []
    for da in data:
        Users.append(User.inadduser(da['id'],da['name'],da['path']))
    print(Users)
    db.close()
    return Users;

def writeadddb(Users:list[User.inadduser]):
    db=open("adddb.json","w");
    str = """{
            "inadduser":["""
    cpt = 0

    for user in Users:
        str+=user.tojson();
        if (cpt==len(Users)-1):
            continue;
        cpt+=1
        str+=""",
        """
    str+="""]
    }"""
    print(str)
    db.write(str);
    db.close()