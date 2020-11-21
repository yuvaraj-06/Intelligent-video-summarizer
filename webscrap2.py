# compare with old request id and while till new id
import json
import requests
def getw2():

    URLw2 = 'https://webhook.site/token/a703f1c6-b728-4562-9eee-a91d299c6f8f'
    pagew2 = requests.get(URLw2)
    varw2=pagew2.content

    idw2=varw2.decode('utf-8')

    id1w2=json.loads(idw2)
    idnumw2=id1w2['latest_request_id']
    return idnumw2
def json_callw2(idfw2):
    URLw2 = 'https://webhook.site/token/a703f1c6-b728-4562-9eee-a91d299c6f8f/request/' + str(idfw2) + '/raw'
    pagew2 = requests.get(URLw2)
    varw2 = pagew2.content
    txtw2 = varw2.decode('utf-8')
    txtdw2 = json.loads(varw2)
    print(pagew2.content)
    file2 = open('final2.txt', 'w')
    file2.truncate(0)
    file2.write(str(txtdw2) + "\n")
    file2.close()


idiw2=getw2()
idfw2=getw2()
while(idfw2==idiw2):
    idfw2=getw2()
print(idfw2,"hello")
json_callw2(idfw2)
