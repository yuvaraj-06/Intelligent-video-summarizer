# compare with old request id and while till new id
import json
import requests
def get():
    URL ='https://webhook.site/token/a5d6f48a-b29e-4f8f-96a3-badb60823be4'
    page = requests.get(URL)
    var=page.content
    id=var.decode('utf-8')
    id1=json.loads(id)
    idnum=id1['latest_request_id']
    return idnum
def json_call(idf):
    URL = 'https://webhook.site/token/a5d6f48a-b29e-4f8f-96a3-badb60823be4/request/'+str(idf)+'/raw'
    page = requests.get(URL)
    var = page.content
    txt = var.decode('utf-8')
    txtd = json.loads(txt)
    print(page.content)
    file4 = open('final4.txt', 'w')
    file4.truncate(0)
    file4.write(str(txtd) + "\n")
    file4.close()
idi=get()
idf=get()
while(idf==idi):
    idf=get()
print(idf,"hello")
json_call(idf)