#!/usr/bin/env python

import requests
import re
import bs4 as BeautifulSoup
import csv
from termcolor import cprint

emails = []
passwords = []
output = []

with open('logins.csv', 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
        emails.append(row[0])
        passwords.append(row[1])


for x in range(0, len(emails)):
  email = emails[x]
  password = passwords[x]


  session=requests.Session()
  session.cookies.clear()

  headers={
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
  }

  url="https://cp.adidas.co.uk/web/eCom/en_GB/loadsignin?target=account"
  response=session.get(url,headers=headers)

  soup=BeautifulSoup.BeautifulSoup(response.text, "lxml")

  _signinSubmit=soup.find('button',{'name':'signinSubmit'}).get('value')
  _IdpAdapterId=soup.find('input',{'name':'IdpAdapterId'}).get('value')
  _SpSessionAuthnAdapterId=soup.find('input',{'name':'SpSessionAuthnAdapterId'}).get('value')
  _PartnerSpId=soup.find('input',{'name':'PartnerSpId'}).get('value')
  _validator_id=soup.find('input',{'name':'validator_id'}).get('value')
  _TargetResource=soup.find('input',{'name':'TargetResource'}).get('value')
  _InErrorResource=soup.find('input',{'name':'InErrorResource'}).get('value')
  _loginUrl=soup.find('input',{'name':'loginUrl'}).get('value')
  _cd=soup.find('input',{'name':'cd'}).get('value')
  _app=soup.find('input',{'name':'app'}).get('value')
  _locale=soup.find('input',{'name':'locale'}).get('value')
  _domain=soup.find('input',{'name':'domain'}).get('value')
  _email=soup.find('input',{'name':'email'}).get('value')
  _pfRedirectBaseURL_test=soup.find('input',{'name':'pfRedirectBaseURL_test'}).get('value')
  _pfStartSSOURL_test=soup.find('input',{'name':'pfStartSSOURL_test'}).get('value')
  _resumeURL_test=soup.find('input',{'name':'resumeURL_test'}).get('value')
  _FromFinishRegistraion=soup.find('input',{'name':'FromFinishRegistraion'}).get('value')
  _CSRFToken=soup.find('input',{'name':'CSRFToken'}).get('value')

  data={
    "username":email,
    "password":password,
    "signinSubmit":_signinSubmit,
    "IdpAdapterId":_IdpAdapterId,
    "SpSessionAuthnAdapterId":_SpSessionAuthnAdapterId,
    "PartnerSpId":_PartnerSpId,
    "validator_id":_validator_id,
    "TargetResource":_TargetResource,
    "InErrorResource":_InErrorResource,
    "loginUrl":_loginUrl,
    "cd":_cd,
    "app":_app,
    "locale":_locale,
    "domain":_domain,
    "email":_email,
    "pfRedirectBaseURL_test":_pfRedirectBaseURL_test,
    "pfStartSSOURL_test":_pfStartSSOURL_test,
    "resumeURL_test":_resumeURL_test,
    "FromFinishRegistraion":_FromFinishRegistraion,
    "CSRFToken":_CSRFToken
  }

  url="https://cp.adidas.co.uk/idp/startSSO.ping"
  response=session.post(url,headers=headers,data=data)

  #Parse resume URL
  p = re.compile("resURL = '([a-zA-Z0-9://.]+)'")
  result=re.findall(p,response.text)

  try:
    resumeURL=result[-1]
  except IndexError:
    cprint("Invalid login information for uk or account blocked, login details - " + email + " " + password, 'red')
    continue


  #Resume login
  response=session.get(resumeURL,headers=headers)

  soup=BeautifulSoup.BeautifulSoup(response.text, "lxml")

  _action=soup.find('form').get('action')
  _SAMLResponse=soup.find('input',{'name':'SAMLResponse'}).get('value')
  _RelayState=soup.find('input',{'name':'RelayState'}).get('value')

  data={
    "SAMLResponse":_SAMLResponse,
    "RelayState":_RelayState
  }

  #Resume login
  url="https://cp.adidas.co.uk"+_action
  response=session.post(url,headers=headers,data=data)

  soup=BeautifulSoup.BeautifulSoup(response.text, "lxml")

  _action=soup.find('form').get('action')
  _TargetResource=soup.find('input',{'name':'TargetResource'}).get('value')
  _REF=soup.find('input',{'name':'REF'}).get('value')

  data={
    "TargetResource":_TargetResource,
    "REF":_REF
  }

  #Resume login
  url=_action
  response=session.post(url,headers=headers,data=data)

  #Resume login
  url="https://www.adidas.co.uk/on/demandware.store/Sites-adidas-GB-Site/en_GB/MyAccount-Show"
  response=session.get(url,headers=headers)

  soup=BeautifulSoup.BeautifulSoup(response.text, "lxml")

  #_accountInfo=soup.find('div',{'class':'accountwelcome'})
  _orderLinkInfo=soup.find('div',{'class':'myaccount-your-latest-order-buttons'})
 # print(_accountInfo.find('h1').text)
  try:
    url= _orderLinkInfo.find('a').attrs['href']
  except AttributeError:
    cprint("No order for account login details - " + email + " " + password, 'red')
    output.append(email)
    output.append("No order")
    output.append("")
    continue


  response=session.get(url,headers=headers)

  soup=BeautifulSoup.BeautifulSoup(response.text, "lxml")

  _orderNumber=soup.find('div',{'class':'order-header-module'})
  orderNumber = (_orderNumber.find('h1').text)
  print(orderNumber)

  output.append(email)
  output.append(orderNumber)

  _orderStatus=soup.find('div',{'class':'order-progress-indicator'})
  orderStatus = ((' '.join(((soup.find('div',{'class':'selected'})).text).split()))[2:])
  print(orderStatus)
  output.append(orderStatus)


with open('output.csv','w') as file:
    for i in range(0,len(output),3):
         file.write(output[i] + ', ')
         file.write(output[i+1] + ', ')
         file.write(output[i+2])
         file.write('\n')

