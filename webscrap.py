import json
import requests
#https://webhook.site/token/0cc50c80-7812-4684-b669-e88944dcffa4
#https://webhook.site/token/729fb752-49b8-4157-b7d8-c174be6ca8b2
def getw1():
    URLw1 = 'https://webhook.site/token/7396dbb9-c236-4997-aa62-571c8aca0ce7'
    pagew1 = requests.get(URLw1)
    varw1=pagew1.content
    idw1=varw1.decode('utf-8')
    id1w1=json.loads(idw1)
    idnumw1=id1w1['latest_request_id']
    return idnumw1
def json_callw1(idfw1):
    URLw1 = 'https://webhook.site/token/7396dbb9-c236-4997-aa62-571c8aca0ce7/request/' + str(idfw1) + '/raw'
    pagew1 = requests.get(URLw1)
    varw1 = pagew1.content
   # txtw1 = varw1.decode('utf-8')
    txtdw1 = json.loads(varw1)
    print(pagew1.content)
    file1 = open('final1.txt', 'w')
    file1.truncate(0)
    file1.write(str(txtdw1)+"\n")
    file1.close()

idiw1=getw1()
idfw1=getw1()
while(idfw1==idiw1):
    idfw1=getw1()
print(idfw1,"hello")
json_callw1(idfw1)
