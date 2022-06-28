import json
import os
import sys
import io
from os.path import exists

import bson
import requests
from bs4 import BeautifulSoup
import re
from requests import get


def createJsonAktyPrawne(oid, przedmiotAktu, numerRocznikaAktu, dataWydania, dataObowiazywania, isPresent, tagi, fkIdStatusAktu, \
               fkIdRodzajAktu, fkIdJednostkaInicjujaca, czyPlikWordPubliczny, zmieniaAktyPrawne, uchylaAktyPrawne, fkIdAlertu, klasas,\
                         dataPublikacji, dataModyfikacji, ktoPublikowal, ktoWytowrzyl):
    f = io.open("wyniki.json", "a", encoding='utf-8')
    f.write("{")
    f.write('"_id":{"$oid":"' + str(oid) + '"},')
    f.write('"przedmiotAktu":"' + str(przedmiotAktu) + '",')
    f.write('"numerRocznikAktu":"' + str(numerRocznikaAktu) + '",')
    f.write('"dataWydania":{"$date":"' + str(dataWydania) + '"},')
    f.write('"dataObowiazywania":{"value":{"$date":"' + dataObowiazywania + '"},"isPresent":' + isPresent + '},')
    f.write('"dataPublikacji":{"$date":"' + str(dataPublikacji) + '"},')
    f.write('"dataModyfikacji":{"$date":"' + str(dataModyfikacji) + '"},')
    f.write('"ktoPublikowal":"' + str(ktoPublikowal) + '",')
    f.write('"ktoWytowrzyl":"' + str(ktoWytowrzyl) + '",')
    f.write('"tagi":[' + str(tagi) + '],')
    f.write('"fkIdStatusAktu":"' + str(fkIdStatusAktu) + '",')
    f.write('"fkIdRodzajAktu":"' + str(fkIdRodzajAktu) + '",')
    f.write('"fkIdJednostkaInicjujaca":"' + str(fkIdJednostkaInicjujaca) + '",')
    f.write('"czyPlikWordPubliczny":' + czyPlikWordPubliczny + ',')
    f.write('"zmieniaAktyPrawne":[' + str(zmieniaAktyPrawne) + '],')
    f.write('"uchylaAktyPrawne":[' + str(uchylaAktyPrawne) + '],')
    f.write('"fkIdAlertu":{"value":"' + str(fkIdAlertu) +'","isPresent":' + isPresent + '},')
    f.write('"_class":"' + str(klasas) + '"')
    f.write("},\n")
    f.close()

def createJsonFiles(path, isPresent, dataDodania, oidAktu, nazwaPliku, value, rodzajPliku, mime):
    f = io.open("files.json", "a", encoding='utf-8')
    oid = bson.objectid.ObjectId()
    f.write('{')
    f.write('"_id":{"$oid":"' + str(oid) + '"},')
    f.write('"sciezka":"' + str(path) + '",')
    f.write('"nrZalacznika":{"isPresent":' + str(isPresent) + '},')
    f.write('"dataDodania":{"$date":"' + str(dataDodania) + '"},')
    f.write('"fkIdAktyPrawne":"' + str(oidAktu) + '",')
    f.write('"nazwaPliku":"' + str(nazwaPliku) + '",')
    f.write('"uwagi":{"value":"' + str(value) + '","isPresent":' + str(isPresent) + '},')
    f.write('"rodzajPliku":"' + str(rodzajPliku) + '",')
    f.write('"mime":"' + str(mime) + '",')
    f.write('"_class":"pl.edu.uph.rapu.model.ZalacznikAktuPrawnego"')
    f.write("},\n")
    f.close()

def Akt_Rodzaj(RodzajAktu):
    if RodzajAktu == "UchwałyRady":
        RodzajAktu = "60dade91cce322714ed30c54"
    elif RodzajAktu == "UchwałySenatu":
        RodzajAktu = "60d8b602cce322714ed30c3f"
    elif RodzajAktu == "ZarządzeniaRektora":
        RodzajAktu = "60dade58cce322714ed30c52"
    elif RodzajAktu == "ObwieszczeniaRektora":
        RodzajAktu = "60dade71cce322714ed30c53"
    return RodzajAktu

def Akt_date(tytulAktu):
    miesiace = {'stycznia':'01', 'lutego':'02', 'marca':'03', 'kwietnia':'04', 'maja':'05', 'czerwca':'06', 'lipca':'07', 'sierpnia':'08', 'września':'09', 'wrzesnia':'09', 'października':'10', 'listopada':'11', 'grudnia':'12'}
    date = re.findall("(?<=dnia )[0-9]{1,2} *.* [0-9]{4}",tytulAktu)[0].split(' ')
    rok = date[2]
    miesiac = miesiace[date[1]]
    dzien = date[0]
    if(int(dzien) < 10):
        dataWydania = rok + "-" + miesiac + "-0" + dzien + 'T23:00:00Z'
    else:
        dataWydania = rok + "-" + miesiac + "-" + dzien + 'T23:00:00Z'
    return dataWydania

def Akt_numer_Rocznik(tytulAktu):
    date = re.findall("(?<=dnia )[0-9]{1,2} *.* [0-9]{4}",tytulAktu)[0].split(' ')
    numer = re.findall("(?<=Nr )[0-9]{1,3}", tytulAktu)[0].split(' ')
    return str(numer[0]) + "/" + str(date[2])


def Akt_status(przedmiotAktu, tytulAktu):
    statusSearch1 = re.search(".*archiw.*|.*ARCHIW.*", przedmiotAktu[:])
    statusSearch2 = re.search(".*archiw.*|.*ARCHIW.*", tytulAktu)
    if statusSearch1 or statusSearch2:
        status = "60dadfbecce322714ed30c5a"
    else:
        status = "60d8b61ccce322714ed30c40"
    return status

def createFolderName (folderName):
    if len(folderName) == 4:
        folderExactName = folderName[0][0]
        folderExactName += folderName[1][0]
        folderExactName += folderName[2][0]
        folderExactName += folderName[3]
    else:
        folderExactName = folderName[0][0]
        folderExactName += folderName[1][0]
        folderExactName += folderName[2]
    return folderExactName

def downloader(folderName, links, oidAktu, dataDodania):
    for link in links:
        fName = link['href'].split('/')[-1]
        pathDISK = folderName + '/' + fName
        pathJSON = folderName + '/' + fName
        if os.path.exists(pathDISK):
            continue
        linek = link['href']
        data = retryConnection(linek)
        if fName.split('.')[-1] == 'pdf':
            mime = 'application/pdf'
        else:
            mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        with open(pathDISK, 'wb') as file:
            file.write(data.content)
        createJsonFiles(pathJSON, 0, dataDodania, oidAktu, fName, 0, 0, mime)

def retryConnection(link):
    while True:
        try:
            conn = get(link)
        except requests.exceptions.RequestException:
            continue
        break
    return conn

def dataPublikacji(dane, iloscDanych):
    if iloscDanych == 4:
        dataP = re.findall('(?<=: ).*', dane[0].getText())
    elif iloscDanych == 3:
        dataP = re.findall('(?<=: ).*', dane[0].getText())
    elif iloscDanych == 1:
        dataP = ''
    data = dataP[0].split()[0].split('-')
    godzina = dataP[0].split()[2]
    dataP = data[2] + '-' + data[1] + '-' + data[0] + 'T' + godzina + ':00' + 'Z'
    return dataP

def dataModyfikacji(dane, iloscDanych):
    if iloscDanych == 4:
        dataM = re.findall('(?<=: ).*', dane[1].getText())
    elif iloscDanych == 3:
        dataM = re.findall('(?<=: ).*', dane[1].getText())
    elif iloscDanych == 1:
        dataM = ''

    data = dataM[0].split()[0].split('-')
    godzina = dataM[0].split()[2]
    dataM = data[2] + '-' + data[1] + '-' + data[0] + 'T' + godzina + ':00' + 'Z'
    return dataM

def WhoPub(dane, iloscDanych):
    if iloscDanych == 4:
        WhoPub1 = re.findall('(?<=: ).*', dane[3].getText())
    elif iloscDanych == 3:
        pom = re.findall('.*(?=: )', dane[2].getText())[0]
        if pom == 'Wprowadził':
            WhoPub1 = re.findall('(?<=: ).*', dane[2].getText())
        else:
            WhoPub1 = ' '
    elif iloscDanych == 1:
        WhoPub1 = re.findall('(?<=: ).*', dane[0].getText())

    WhoPub1 = WhoPub1[0]
    return WhoPub1

def WhoWyt(dane, iloscDanych):
    if iloscDanych == 4:
        WhoWyt = re.findall('(?<=: ).*', dane[2].getText())
    elif iloscDanych == 3:
        pom = re.findall('.*(?=: )', dane[2].getText())[0]
        if pom == 'Wytworzył':
            WhoWyt = re.findall('(?<=: ).*', dane[2].getText())
        else:
            WhoWyt = ' '
    elif iloscDanych == 1:
        WhoWyt = re.findall('(?<=: ).*', dane[0].getText())

    WhoWyt = WhoWyt[0]
    return WhoWyt

def start(LinkF):
    if exists('wyniki.json') == False:
        open("wyniki.json", "x")
    if exists('files.json') == False:
        open("files.json", "x")

    czyOstatni = 0

    with open("wyniki.json", "r", encoding='utf-8') as file:
        try:
            if os.path.getsize('wyniki.json') > 0:
                last_line = file.readlines()[-1][:-2]
            else:
                czyOstatni = 1
                last_line = 'none'
                print('Pusty plik')
        except OSError:
            print('Plik nie istnieje')

    mainLink = 'http://www.bip.uph.edu.pl/12768/12768/'
    main = retryConnection(mainLink)
    bs = BeautifulSoup(main.content, features='html.parser')

    state = 0
    print(state)
    #lista uchwał, zarządzeń, obwieszczeń
    for item in bs.find_all('div', class_='item')[1:-1]:
        if state == 0 and LinkF != 'http://www.bip.uph.edu.pl/' + item.find('a')['href']:
            continue
        else:
            state = 1
        pagination = 0;
        try:
            os.mkdir(createFolderName(item.find('a').getText().split()))
        except FileExistsError:
            print("Foldery " + item.find('a').getText().replace(' ','') + " juz istnieje");

        while True:
            pagination += 1
            link_general_sets_decree = 'http://www.bip.uph.edu.pl/' + item.find('a')['href'] + 'strona' + str(pagination) + '.html'
            page_general_sets_decree = retryConnection(link_general_sets_decree)

            bs_general_sets_decree = BeautifulSoup(page_general_sets_decree.content, features='html.parser')
            if bs_general_sets_decree.find('div', class_='module-documents').getText() != "W obecnej chwili nie dysponujemy żadnymi informacjami na wybrany temat.":
                RodzajAktu = item.find('a').getText().strip().split(' ')[0] + item.find('a').getText().strip().split(' ')[1]
                RodzajAktuFile = item.find('a').getText()
                for item2 in bs_general_sets_decree.find_all('div', class_='item'):
                    oid = bson.objectid.ObjectId()
                    przedmiotAktu = item2.find('div', class_='desc').getText().strip().replace('\r', "").replace('\n', '')
                    tytulAktu = item2.find('span', class_='title').getText()

                    print('Przedmiot aktu: ' + przedmiotAktu[:])

                    Status_akt = Akt_status(przedmiotAktu, tytulAktu)
                    print('Status aktu: ' + Status_akt)

                    Numer_rocznik_akt = Akt_numer_Rocznik(tytulAktu)
                    print('Numer rocznik aktu: ' + Numer_rocznik_akt)

                    Data_akt = Akt_date(tytulAktu)
                    print('Data wydania: ' + Data_akt)

                    Rodzaj_akt = Akt_Rodzaj(RodzajAktu)
                    print('RodzajAktu: ' + Rodzaj_akt)

                    #wnętrze uchwały
                    more = item2.find('div', class_='more')
                    link_decree_details = 'http://www.bip.uph.edu.pl/' + more.find('a')['href']
                    page_decree_details = retryConnection(link_decree_details)
                    bs_decree_details = BeautifulSoup(page_decree_details.content, features='html.parser')
                    links = bs_decree_details.find('div', class_='desc').find_all('a')
                    downloader(createFolderName(item.find('a').getText().split()), links, oid, Data_akt)


                    Publikacja = bs_decree_details.find('div', class_='publish-date').find_all('span')
                    dataPub = dataPublikacji(Publikacja, len(Publikacja))
                    dataMod = dataModyfikacji(Publikacja, len(Publikacja))
                    KtoPub = WhoPub(Publikacja, len(Publikacja))
                    KtoWyt = WhoWyt(Publikacja, len(Publikacja))
                    print(dataPub)
                    print(dataMod)
                    print(KtoPub)
                    print(KtoWyt)

                    if czyOstatni == 1:
                        createJsonAktyPrawne(oid, przedmiotAktu, Numer_rocznik_akt, Data_akt, Data_akt, "true", 0, Status_akt, Rodzaj_akt, '60d8b627cce322714ed30c41', "true", 0, 0, 0, "pl.edu.uph.rapu.model.AktPrawny", dataPub, dataMod, KtoPub, KtoWyt)

                    if last_line != 'none':
                        data_dict = json.loads(last_line, strict=False)
                        if data_dict['przedmiotAktu'] == przedmiotAktu:
                            czyOstatni = 1
                    else:
                        czyOstatni = 1


                    print('\n')
            else:
                break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        link = sys.argv[1]
        start(link)
    else:
        start('http://www.bip.uph.edu.pl/12768,30292/30292/')