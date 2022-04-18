import requests
from time import sleep
from bs4 import BeautifulSoup
from urllib.error import HTTPError

s = requests.Session()

header = {    
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.47"
}

def login(email, password, token):
    data = {
        "utf8":"✓",
        "user[email]":email,
        "user[password]":password,
        "commit":"SIGN IN",
        "authenticity_token":token
    }

    r = s.post('https://shift.gearboxsoftware.com/sessions', params=data)

    soup = BeautifulSoup(r.content, "html5lib")
    if soup.find("div", attrs={"class":"alert error"}):
        print("Email or password was incorrect!")
        return False
    else:
        print("Logged in!")
        return True

def getToken():
    r = s.get('https://shift.gearboxsoftware.com/home', headers=header)
    soup = BeautifulSoup(r.content, "html5lib")
    token = soup.find("input", attrs={"name":"authenticity_token"})["value"]
    return token

def getCodes():
    listOfCodes = []
    r = s.get('https://shift.orcicorn.com/tags/steam/index.json', headers=header)
    j = r.json()[0]
    codes = j["codes"]
    with open("RedeemdCodes.txt", "r+") as f:
        data = f.read()
        for x in codes:
            if x["code"] not in data:
                listOfCodes.append(x["code"])
                f.write("\n")
                f.write(x["code"])

    return listOfCodes

def CodeExpired(codes, token):
    try:
        r = s.get('https://shift.gearboxsoftware.com/entitlement_offer_codes?code={}'.format(codes), headers={"x-csrf-token": token, "x-requested-with":"XMLHttpRequest"})
        soup = BeautifulSoup(r.content, "html5lib")
        if soup.find("form", class_="new_archway_code_redemption"):

            token = soup.find("input",attrs= {"name":"authenticity_token"})
            code = soup.find("input", attrs={"name":"archway_code_redemption[code]"})
            check = soup.find("input", attrs={"name":"archway_code_redemption[check]"})
            title = soup.find("input", attrs={"name":"archway_code_redemption[title]"})

            redeemData ={
                "authenticity_token":token["value"],
                "archway_code_redemption[code]":code["value"],
                "archway_code_redemption[check]":check["value"],
                "archway_code_redemption[service]":"steam",
                "archway_code_redemption[title]":title["value"]
            }
            return redeemData
        else:
            print("Code has expired")

    except HTTPError as httpErr:
        print("HTTP error ocures: {}".format(httpErr))
    except Exception as err:
        print("Different error ocures: {}".format(err))

def RedeemCode(redeemData):
    r = s.post('https://shift.gearboxsoftware.com/code_redemptions', data=redeemData)
    soup = BeautifulSoup(r.content, "html5lib")
    status = str(soup.find("p"))
    for specialCharacter in "</p>":
        status = status.replace(specialCharacter, "")

    if "Your code was successfully redeemed" == status:
        print("Code {} has been successfilly redeemed".format(redeemData["archway_code_redemption[code]"]))
    elif "This SHiFT code has already been redeemed" == status:
        print("Code {} has already been redeemed".format(redeemData["archway_code_redemption[code]"])) 
    
    sleep(2.5)

def main():
    accountEmail = input("Enter email: ")
    password = input("Enter password: ")
    token = getToken() 
    loggedIn = login(accountEmail, password, token)
    while True:
        if loggedIn:
            listOfCodes = getCodes()
            if listOfCodes == []:
                print("All codes has been already redeemd")
            else:    
                for code in listOfCodes:
                    list = CodeExpired(code, token)
                    if list != None:    
                        RedeemCode(list)
        sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass