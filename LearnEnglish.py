import requests
import re
from datetime import date
from bs4 import BeautifulSoup
import random
import sys



def ScrapEnglishWordOfTheDay(date):
    response = requests.get('https://www.merriam-webster.com/word-of-the-day/'+str(date))

    if response:
        # print('Success!')
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'html.parser')

        # WORD -> title
        title = soup.title.text
        WordRegex = r"(Word of the Day:)(\s)(\S+)"
        m = re.search(WordRegex, title)
        NewWord = m.group(3)

        # PART OF SPEECH -> span z class="main-attr"
        NewPartOfSpeech = soup.find("span", {"class": "main-attr"})

        # TRANSKRYPT -> span z class="word-syllables"
        NewTranscript = soup.find("span", {"class": "word-syllables"})

        #Definition
        NewDefinition = ScrapEnglishDefinition(NewWord.lower())
        #scrap from original
        if (NewDefinition == "Not found"):
            NewDefinition = soup.find("div", {"class": "wod-definition-container"})
            NewDefinition = NewDefinition.find('p').text

        #< div class ="wod-definition-container" >
        result = str(NewWord + " # " + NewPartOfSpeech.text.strip() + " # " + NewTranscript.text.strip() + " # "+ NewDefinition)
        return result

    else:
        print('A connection error to "merriam-webster" has occurred.')
        print(response.status_code)
        return None


def ScrapEnglishDefinition(word):
    # (dictionary.cambridge)
    response2 = requests.get('https://dictionary.cambridge.org/dictionary/english/'+word)
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
            #every < div class ="ddef_h" >
            #Addition = soup2.find("div", {"class": "ddef_h"})
            #Addition = Addition.text.strip()
            #print(Addition)
            tmp=""
            addition_results = [Addition.text.strip() for Addition in soup2.find_all("div", {"class": "ddef_h"})]
            for i in range(len(addition_results)):
                tmp += str(i+1) + ". " + addition_results[i]

            return str(tmp)
        else:
            return str(m2.group(1))
        ####################################################################

    else:
        print('A connection error to "dictionary.cambridge" has occurred.')
        print(response2.status_code)
        return "not found"

def ScrapEnglishWordOfTheToday():
    return ScrapEnglishWordOfTheDay(str(date.today()))

def LessThanTen(x):
    if (x < 10):
        x = "0" + str(x)
        return str(x)
    else:
        return str(x)


def GenerateRandomDate():
    days30 = ["04","06","09","11"]
    days31 = ["01","03","05","07","08","10","12"]
    randomYear = str(random.randrange(2007, 2020, 1))
    randomMonth = random.randrange(1, 12, 1)
    randomMonth = LessThanTen(randomMonth)

    if (randomMonth == "02"):
        randomDay = random.randrange(1, 28, 1)
        randomDay = LessThanTen(randomDay)

    elif (randomMonth in days30):
        randomDay = random.randrange(1, 30, 1)
        randomDay = LessThanTen(randomDay)
    elif (randomMonth in days31):
        randomDay = random.randrange(1, 31, 1)
        randomDay = LessThanTen(randomDay)

    result = randomYear + "-" + randomMonth + "-" + randomDay
    print (result)
    return result

def ScrapRandomEnglishWordOfTheDay():
    return ScrapEnglishWordOfTheDay(GenerateRandomDate())

def UpdateEnglishDictionary(x):
    f = open("EnglishDictionary.txt", "a+", encoding="utf-8")
    f.write(x + "\n")
    f.close()
    print("Updated, new word: "+x)

def ClearDictionary(x):
    f = open(x + "Dictionary.txt", "w", encoding="utf-8")
    f.write("")
    f.close()

def MakeFullArray(x):
    fullArray = []
    f = open(x + "Dictionary.txt", "r", encoding="utf-8")
    for x in f:
        x = x.split()
        tmpDef = ""
        for i in range(6,len(x)):
            if i == len(x)-1 and x[i] == ".":
                break
            else:
                tmpDef += x[i] + " "
        fullArray.append([x[0],x[2],x[4],tmpDef])
    f.close()
    return fullArray

def GenerateOneQuestion():

    FullArray = MakeFullArray("English")
    UsedDefinitions = []
    randomWord = random.randrange(0, len(FullArray), 1)
    OneQuestion = [FullArray[randomWord][0] + " (" + FullArray[randomWord][1] + ") [" + FullArray[randomWord][2] + "]"]
    anwsers = ["A. ", "B. ","C. ","D. "]
    correct = random.randrange(0, 3, 1)
    anwsers[correct] += FullArray[randomWord][3]
    UsedDefinitions.append(FullArray[randomWord][3])
    for i in range(0,4):
        if (i != correct):
            while (True):
                randomDefinition = random.randrange(0, len(FullArray), 1)
                if (FullArray[randomDefinition][3] not in UsedDefinitions and FullArray[randomWord][1] == FullArray[randomDefinition][1]):
                    anwsers[i] += FullArray[randomDefinition][3]
                    UsedDefinitions.append(FullArray[randomDefinition][3])
                    break

    OneQuestion.append(anwsers)
    OneQuestion.append(chr(65 + correct))
    return OneQuestion

def AskOneQuestion():
    question = GenerateOneQuestion()
    print(question[0] + "\n")
    for i in range (0,4):
        print (question[1][i])

    while(True):
        print()
        answer = input("Your Anwser (letter): ")
        if ( answer == question[2]):
            print("Correct \n")
            break
        else:
            print("Wrong")

def GenerateTest(x):
    for i in range(x):
        AskOneQuestion()


if __name__ == '__main__':

    version = "LeanEnglish v1.0 by ElusiveFox (github_link)"
    banner = """
                                                                                          
 __                       _____         _ _     _      _          _ _ _ _____ _____ ____  
|  |   ___ ___ ___ ___   |   __|___ ___| |_|___| |_   | |_ _ _   | | | |     |_   _|    \\ 
|  |__| -_| .'|  _|   |  |   __|   | . | | |_ -|   |  | . | | |  | | | |  |  | | | |  |  |
|_____|___|__,|_| |_|_|  |_____|_|_|_  |_|_|___|_|_|  |___|_  |  |_____|_____| |_| |____/ 
                                   |___|                  |___|                                    
    """
    if (len(sys.argv) == 1 or sys.argv[1] == "-h"):
        print(banner)
        print("LeanEnglish by WOTD v1.0 by ElusiveFox (github_link) \nUsage: python3 LearnEnglish.py [Options] \n")
        print("""GENERAL:
  -h: prints out help 
  -t: prints out today's WOTD
  -v: prints out version
  -g <number>: generate a test of random words from the dictionary""")
        print("""DICTIONARY:
  --add-today: adds today's WOTD to the dictionary
  --add-random <number>: adds random WOTD to the dictionary
  -clear: clears out dictionary
        """)
    elif (len(sys.argv) == 2 or len(sys.argv) == 3):
        if(sys.argv[1] == "-v"):
            print(version)
        elif (sys.argv[1] == "-t"):
            print(ScrapEnglishWordOfTheToday())
        elif (sys.argv[1] == "--add-today"):
            UpdateEnglishDictionary(ScrapEnglishWordOfTheToday())
        elif (sys.argv[1] == "--clear-dictionary"):
            ClearDictionary("English")
        elif (sys.argv[1] == "--add-random"):
            for i in range (int(sys.argv[2])):
                UpdateEnglishDictionary(ScrapRandomEnglishWordOfTheDay())
        elif (sys.argv[1] == "-g"):
            GenerateTest(int(sys.argv[2]))
        else:
            print ("LearnEnglish.py: unrecognized option " + sys.argv[1])

    #print("This is the name of the script: ", sys.argv[0])
    #print("Number of arguments: ", len(sys.argv))
    #print("The arguments are: ", str(sys.argv))
    #print(GenerateOneQuestion())
    #GenerateTest(3)
    #ClearDictionary("English")
    #UpdateEnglishDictionary(ScrapEnglishWordOfTheToday())
    #for i in range(1,9):
    #     UpdateEnglishDictionary((ScrapEnglishWordOfTheDay("2020-01-2"+str(i))))
    #for i in range(1, 9):
    #    UpdateEnglishDictionary((ScrapEnglishWordOfTheDay("2020-01-1" + str(i))))
    #for i in range(1, 9):
    #    UpdateEnglishDictionary((ScrapEnglishWordOfTheDay("2019-04-1" + str(i))))
    # for i in range (100):
    #     UpdateEnglishDictionary(ScrapRandomEnglishWordOfTheDay())





###################### OPTIMALIZATION ##########################################
#start_time = time.time()
# <some instruction>
#print("--- %s seconds ---" % (time.time() - start_time))
######################  To Do ##################################################
# wyjątki
# 1 - no internet connection
# 2 - no file dict.txt
################################################################################




