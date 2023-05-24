import json

profile =[]


#profile.append(newProfile1)
#profile.append(newProfile2)

def readProfile():
    namelist = []
    with open("profile.json","r") as f:
        data = json.load(f)
    for obj in data:
        namelist.append(obj["name"])

    #print(data)
    return namelist
    
def selectedProfile(nametoselected):
    with open("profile.json","r") as f:
        data = json.load(f)
    for obj in data:
        if obj["name"] == nametoselected:
            return obj["Parameter"]
    return None
            
def updateProfile(nametoupdate,dia,n,lap):
    with open("profile.json","r") as f:
        data = json.load(f)
    newData ={
    "name" : nametoupdate,
    "Parameter":{
            "Diameter": dia,
            "Speed" : n,
            "Lap":lap            
            }
    }
    for i, item in enumerate(data):
        if item['name'] == nametoupdate:
            data[i] = newData
            print(i)
            break
    else:
        data.append(newData)

    with open("profile.json","w") as f:
        json.dump(data,f)

def deleteProfile(nametodelete):
    with open("profile.json","r") as f:
        data = json.load(f)
    for obj in data:
        if obj.get('name') == nametodelete:
            data.remove(obj) 
    with open("profile.json","w") as f:
        json.dump(data,f)
        
if __name__ == "__main__":
    #updateProfile("profile5",5,30,20)
    #deleteProfile("profile15")
    #ob = selectedProfile('profile15')
    #print(ob)
    print(readProfile())

