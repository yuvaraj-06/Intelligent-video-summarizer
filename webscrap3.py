# compare with old request id and while till new id
import json
import requests
def get():

    URL = 'https://webhook.site/token/bb5f026f-6d96-46c8-ac50-5a4d45b79324'
    page = requests.get(URL)
    var=page.content

    id3=var.decode('utf-8')

    id13=json.loads(id3)
    idnum=id13['latest_request_id']
    return idnum
def json_call(idf):
    URL = 'https://webhook.site/token/bb5f026f-6d96-46c8-ac50-5a4d45b79324/request/'+str(idf)+'/raw'
    page = requests.get(URL)
    var = page.content
    txt = var.decode('utf-8')
    txtd = json.loads(txt)
    print(page.content)
    file3 = open('final3.txt', 'w', encoding="utf-8")
    file3.truncate(0)
    file3.write(str(txtd) + "\n")
    file3.close()
idi=get()
idf=get()
while(idf==idi):
    idf=get()
print(idf,"hello")
json_call(idf)
