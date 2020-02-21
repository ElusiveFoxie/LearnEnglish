import datetime
import random
import re
import sys

import requests
from bs4 import BeautifulSoup


def ScrapEnglishWordOfTheDay(date):
    response = requests.get('https://www.merriam-webster.com/word-of-the-day/' + str(date))

    if response:
        # print('Success!')
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'html.parser')

        # WORD -> H1 tag
        NewWord = soup.find('h1').text.capitalize()

        # PART OF SPEECH -> span z class="main-attr"
        NewPartOfSpeech = soup.find("span", {"class": "main-attr"})

        # TRANSKRYPT -> span z class="word-syllables"
        NewTranscript = soup.find("span", {"class": "word-syllables"})

        # Definition
        NewDefinition = ScrapEnglishDefinition(NewWord.lower())
        # scrap from original
        if (NewDefinition == "Not found"):
            NewDefinition = soup.find("div", {"class": "wod-definition-container"})
            NewDefinition = NewDefinition.find('p').text

        # < div class ="wod-definition-container" >
        result = str(
            NewWord + " # " + NewPartOfSpeech.text.strip() + " # " + NewTranscript.text.strip() + " # " + NewDefinition)
        return result

    else:
        print('A connection error to "merriam-webster" has occurred.')
        print(response.status_code)
        return None


def ScrapEnglishDefinition(word):
    # (dictionary.cambridge)
    response2 = requests.get('https://dictionary.cambridge.org/dictionary/english/' + word)
    if response2:
        html_doc2 = response2.text
        soup2 = BeautifulSoup(html_doc2, 'html.parser')

        #################  SLOWER ###########################################
        # tmp = ""
        # addition_results = [Addition.text.strip() for Addition in soup2.find_all("div", {"class": "ddef_h"})]
        # for i in range(len(addition_results)):
        #     tmp += str(i + 1) + ". " + addition_results[i]+" "
        # if (tmp == ""):
        #     return "Not found"
        # else:
        #     return str(tmp)
        #####################################################################

        #################  FASTER     #######################################
        # <meta name="description" content="debonair definition: (especially of men) attractive, confident, and carefully dressed: . Learn more." />
        NewDefinition = soup2.find("meta", {"name": "description"})
        m2 = re.search(r"content=\".+definition:(.+) Learn more", str(NewDefinition))
        if (m2 == None):
            return "Not found"
        elif (str(m2.group(1)).endswith('….')):
            # every < div class ="ddef_h" >
            # Addition = soup2.find("div", {"class": "ddef_h"})
            # Addition = Addition.text.strip()
            # print(Addition)
            tmp = ""
            addition_results = [Addition.text.strip() for Addition in soup2.find_all("div", {"class": "ddef_h"})]
            for i in range(len(addition_results)):
                tmp += str(i + 1) + ". " + addition_results[i]

            return str(tmp)
        else:
            return str(m2.group(1))
        ####################################################################

    else:
        print('A connection error to "dictionary.cambridge" has occurred.')
        print(response2.status_code)
        return "not found"


def ScrapEnglishWordOfTheToday():
    return ScrapEnglishWordOfTheDay(str(datetime.date.today()))


def scrapAllFrom(dateFrom):
    now = datetime.date.today()
    dateFrom = dateFrom.split("-")
    dateFrom = datetime.date(int(dateFrom[0]), int(dateFrom[1]), int(dateFrom[2]))
    delta = now - dateFrom
    for i in range(delta.days + 1):
        day = dateFrom + datetime.timedelta(days=i)
        UpdateEnglishDictionary(ScrapEnglishWordOfTheDay(day))


def random_date(start, end):
    delta = end - start
    int_delta = delta.days
    random_days = random.randrange(int_delta)
    return start + datetime.timedelta(days=random_days)


def GenerateRandomDate():
    d1 = datetime.datetime.strptime('2007-01-01', '%Y-%m-%d')
    d2 = datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d')
    return (str(random_date(d1, d2)).replace(" 00:00:00", ""))


def ScrapRandomEnglishWordOfTheDay():
    return ScrapEnglishWordOfTheDay(GenerateRandomDate())


def UpdateEnglishDictionary(x):
    with open('EnglishDictionary.txt', "a+", encoding="utf-8") as f:
        f.write(x + "\n")
        print("Updated, new word: " + x)


def ClearDictionary():
    with open('EnglishDictionary.txt', "w", encoding="utf-8") as f:
        f.write("")
        print("Dictionary cleared !")


def showAll():
    with open('EnglishDictionary.txt', "r", encoding="utf-8") as f:
        for x in f:
            print(x)


def MakeFullArray(x):
    fullArray = []
    f = open(x + "Dictionary.txt", "r", encoding="utf-8")
    for x in f:
        x = x.split()
        tmpDef = ""
        for i in range(6, len(x)):
            if i == len(x) - 1 and x[i] == ".":
                break
            else:
                tmpDef += x[i] + " "
        fullArray.append([x[0], x[2], x[4], tmpDef])
    f.close()
    return fullArray


def GenerateOneQuestion():
    FullArray = MakeFullArray("English")
    UsedDefinitions = []
    randomWord = random.randrange(0, len(FullArray), 1)
    OneQuestion = [FullArray[randomWord][0] + " (" + FullArray[randomWord][1] + ") [" + FullArray[randomWord][2] + "]"]
    anwsers = ["A. ", "B. ", "C. ", "D. "]
    correct = random.randrange(0, 3, 1)
    anwsers[correct] += FullArray[randomWord][3]
    UsedDefinitions.append(FullArray[randomWord][3])
    for i in range(0, 4):
        if (i != correct):
            while (True):
                randomDefinition = random.randrange(0, len(FullArray), 1)
                if (FullArray[randomDefinition][3] not in UsedDefinitions and FullArray[randomWord][1] ==
                        FullArray[randomDefinition][1]):
                    anwsers[i] += FullArray[randomDefinition][3]
                    UsedDefinitions.append(FullArray[randomDefinition][3])
                    break

    OneQuestion.append(anwsers)
    OneQuestion.append(chr(65 + correct))
    return OneQuestion


def AskOneQuestion():
    question = GenerateOneQuestion()
    print(question[0] + "\n")
    for i in range(0, 4):
        print(question[1][i])

    while (True):
        print()
        answer = input("Your Anwser (letter): ")
        if (answer == question[2]):
            print("Correct \n")
            break
        else:
            print("Wrong")


def GenerateTest(x):
    for i in range(x):
        AskOneQuestion()


if __name__ == '__main__':
    version = "LeanEnglish v1.0 by ElusiveFox, matisec (https://github.com/ElusiveFoxie/LearnEnglish)"
    banner = """                                                                                   
 __                       _____         _ _     _      _          _ _ _ _____ _____ ____  
|  |   ___ ___ ___ ___   |   __|___ ___| |_|___| |_   | |_ _ _   | | | |     |_   _|    \\ 
|  |__| -_| .'|  _|   |  |   __|   | . | | |_ -|   |  | . | | |  | | | |  |  | | | |  |  |
|_____|___|__,|_| |_|_|  |_____|_|_|_  |_|_|___|_|_|  |___|_  |  |_____|_____| |_| |____/ 
                                   |___|                  |___|                                    
    """
    if (len(sys.argv) == 1 or sys.argv[1] == "-h"):
        print(banner)
        print(
            "LeanEnglish by WOTD v1.0 by ElusiveFox, matisec (https://github.com/ElusiveFoxie/LearnEnglish) \nUsage: python3 LearnEnglish.py [Options] \n")
        print("""GENERAL:
  -h: prints out help 
  -t: prints out today's WOTD
  -v: prints out version
  -g <number>: generate a test of random words from the dictionary""")
        print("""DICTIONARY:
  --add-today: adds today's WOTD to the dictionary
  --add-from <date format: yyyy:mm:dd>: adds all words from specified date
  --add-random <number>: adds random WOTD to the dictionary
  --show-all: shows content of EnglishDictionary.txt
  -clear: clears out dictionary
        """)
    elif (len(sys.argv) == 2 or len(sys.argv) == 3):
        if (sys.argv[1] == "-v"):
            print(version)
        elif (sys.argv[1] == "-t"):
            print(ScrapEnglishWordOfTheToday())
        elif (sys.argv[1] == "--add-today"):
            UpdateEnglishDictionary(ScrapEnglishWordOfTheToday())
        elif (sys.argv[1] == "-clear"):
            ClearDictionary()
        elif (sys.argv[1] == "--add-random"):
            for i in range(int(sys.argv[2])):
                UpdateEnglishDictionary(ScrapRandomEnglishWordOfTheDay())
        elif (sys.argv[1] == "--add-from"):
            scrapAllFrom(str(sys.argv[2]))
        elif (sys.argv[1] == "-g"):
            GenerateTest(int(sys.argv[2]))
        elif (sys.argv[1] == "--show-all"):
            showAll()
        else:
            print("LearnEnglish.py: unrecognized option " + sys.argv[1])

    # print("This is the name of the script: ", sys.argv[0])
    # print("Number of arguments: ", len(sys.argv))
    # print("The arguments are: ", str(sys.argv))
    # print(GenerateOneQuestion())
    # GenerateTest(3)
    # ClearDictionary("English")
    # UpdateEnglishDictionary(ScrapEnglishWordOfTheToday())
    # for i in range(1,9):
    #     UpdateEnglishDictionary((ScrapEnglishWordOfTheDay("2020-01-2"+str(i))))
    # for i in range(1, 9):
    #    UpdateEnglishDictionary((ScrapEnglishWordOfTheDay("2020-01-1" + str(i))))
    # for i in range(1, 9):
    #    UpdateEnglishDictionary((ScrapEnglishWordOfTheDay("2019-04-1" + str(i))))
    # for i in range (100):
    #     UpdateEnglishDictionary(ScrapRandomEnglishWordOfTheDay())

###################### OPTIMALIZATION ##########################################
# start_time = time.time()
# <some instruction>
# print("--- %s seconds ---" % (time.time() - start_time))
######################  To Do ##################################################
# -weekly: generate test from words added from this week
# --add-week: adds words from this week
# --show-all:
# wyjątki
# 1 - no internet connection
# 2 - no file dict.txt
################################################################################
