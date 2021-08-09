import sys

from googlesearch import search
from AzureFunctions import translate_text
from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient
from msrest.authentication import CognitiveServicesCredentials
import webbrowser
import aiml
import urllib.request
import json

from nltk.inference.resolution import Clause
from tensorflow import keras
import numpy as np

model = keras.models.load_model('my_model.h5')

# Create a Kernel object. No string encoding (all I/O is unicode)
kern = aiml.Kernel()
kern.setTextEncoding(None)
kern.bootstrap(learnFiles="xmlFiles/Chatbot.xml")
#######################################################
#  Initialise Knowledgebase.
#######################################################
import pandas

from nltk.sem import Expression
from nltk.inference import ResolutionProver

# Getting the services from Azure AI
cog_key = '7f98fd1fe47a44ea9fa532ac6dec0a78'
cog_endpoint = 'https://cognitiveservicesstage4.cognitiveservices.azure.com/'
cog_region = 'uksouth'



read_expr = Expression.fromstring
kb=[]
data = pandas.read_csv('kb.csv', header=None)
[kb.append(read_expr(row)) for row in data[0]]
#Check for contradiction before continue running the program
contradict = Clause(data).is_tautology()
if contradict:
    #If it contradicts it stops the program
    sys.exit("Error Message")



#######################################################
# Welcome user
#######################################################
print("Welcome to this chat bot. Please feel free to ask questions from me!")

#Quiz here
questions = ["What are the stages called that show how a caterpillar turns into a butterfly?",
         "Where are dogs sweat gland located?",
         "True or False... All cows are females",
         ]

answer_choices = ["a)Life Cycle\nb)Process\nc)Growing up\nd)Life Steps\n:",
              "a)Tail\nb)Nose\nc)Paws\nd)Neck\n:",
              ":",
              ]
correct_choices = [{"a", "Life Cycle"},
               {"c", "Paws"},
               {"false", "f"},
               ]
answers = ["Is called Life Cycle",
       "Dog sweats gland are located at paws",
       "",
       ]


def quiz():
    score = 0
    for question, choices, correct_choice, answer in zip(questions, answer_choices, correct_choices, answers):
        print(question)
        user_answer = input(choices).lower()
        if user_answer in correct_choice:
            print("Correct")
            score += 1
        else:
            print("Incorrect", answer)
    print(score, "out of", len(questions), "that is", float(score / len(questions)) * 100, "%")

#######################################################
# Main loop
#######################################################
while True:
    #get user input
    try:
        reviewListB4Trans = []
        inputUser = input("> ")
        reviewText = inputUser
        review = {"id" : "Document", "text" : reviewText}
        reviewListB4Trans.append(review)
        # Get a client for your text analytics cognitive service resource
        text_analytics_client = TextAnalyticsClient(endpoint=cog_endpoint,
                                                    credentials=CognitiveServicesCredentials(cog_key))
        language_analysis = text_analytics_client.detect_language(documents=reviewListB4Trans)
        for review_num in range(len(reviewListB4Trans)):
            # print the review id
            print(reviewListB4Trans[review_num]['id'])

            # Get the language details for this review
            lang = language_analysis.documents[review_num].detected_languages[0]
            print(' - Language: {}\n - Code: {}\n - Score: {}\n'.format(lang.name, lang.iso6391_name, lang.score))

            # Add the detected language code to the collection of reviews (so we can do further analysis)
            reviewListB4Trans[review_num]["language"] = lang.iso6391_name
            text_to_translate = reviewText
            detectedLang = lang.iso6391_name
            print(detectedLang)
            translation = translate_text(cog_region, cog_key, text_to_translate, to_lang='en-US', from_lang=detectedLang)
            userInput = translation
            print('{} -> {}'.format(text_to_translate, translation))

    except (KeyboardInterrupt, EOFError) as e:
        print("Bye!")
        break
    #pre-process user input and determine response agent (if needed)
    responseAgent = 'aiml'
    #activate selected response agent
    if responseAgent == 'aiml':
        answer = kern.respond(userInput)
        # Translate output to user by detecting user language
        translation = translate_text(cog_region, cog_key, answer, to_lang=detectedLang, from_lang='en')
        print(translation)
    #post-process the answer for commands
    if answer[0] == '#':
        params = answer[1:].split('$')
        cmd = int(params[0])
        if cmd == 0:
            print(params[1])
            break
        elif cmd == 1: # google search result
            try:
                result = search(userInput, num_results=5)
                for i in result:
                    print(i, end = '\n')
                #print(result) #Strucutre this nicer 
                print("Do you want to open the link?")
            except:
                print("Sorry, I do not know that. Be more specific!")
        elif cmd == 2: # google search result
            try:
                for i in result:
                    print(i, end = '\n')
                print("Which one would you like to open? Only 0-5")
            except:
                print("Sorry, I do not know that. Be more specific!")
        elif cmd == 3: # google search result
            try:
                userInput = int(userInput)
                webbrowser.open(result[userInput]) 
                print("Link is opened what else can I do for you?")
            except:
                print("Sorry, I do not know that. Be more specific!")
        elif cmd == 4:
            try:
                query = str(input('Define Word? '))
                url = 'http://api.urbandictionary.com/v0/define?term=%s' % (query)

                response = urllib.request.urlopen(url)
                data = json.loads(response.read())
                definition = data['list'][0]['definition']

                print (query + ': ' + definition)


            except:
                print("Sorry, I do not know that. Be more specific!")
        elif cmd == 5: # Using trained model to ask what each image is
            try:
                imageFileName = input("What image?")
                
                from keras.preprocessing import image
                test_image = image.load_img(imageFileName, target_size = (128, 128))
                test_image = image.img_to_array(test_image)
                test_image = np.expand_dims(test_image, axis = 0)
                result = model.predict_classes(test_image)
                ask_question = print('Would you like to do a quiz? 1 = yes, 2 = no')

                if result == [0]:
                        print('butterfly')
                        print('  ')
                        print('Fun fact:')
                        print('Butterfly use their feet to taste')
                        ask_question
                        #Make it a quiz for each type of animal
                elif result == [1]: # fun fact of each animal
                    print('cat')
                    print('  ')
                    print('Fun fact:')
                    print('Cat have flexible bodies and teeth adapted for haunting small animals')
                    ask_question
                elif result == [2]:
                    print('chicken')
                    print('  ')
                    print('Fun fact:')
                    print('Chicken can show empathy')
                    ask_question
                elif result == [3]:
                    print('cow')
                    print('  ')
                    print('Fun fact:')
                    print('Cow can sleep while they are standing')
                    ask_question
                elif result == [4]:
                    print('dog')
                    print('  ')
                    print('Fun Fact:')
                    print('Three dogs survived the Titanic sinking')
                    ask_question
                elif result == [5]:
                    print('elephant')
                    print('  ')
                    print('Fun Fact:')
                    print('They communicate through vibrations')
                    ask_question
                elif result == [6]:
                    print('horse')
                    print('  ')
                    print('Fun Fact:')
                    print('Horse can not vomit')
                    ask_question
                elif result == [7]:
                    print('sheep')
                    print('  ')
                    print('Fun Fact:')
                    print('Sheep have great memories')
                    ask_question
                elif result == [8]:
                    print('spider')
                    print('  ')
                    print('Fun Fact:')
                    print('Jumping spiders can jump up to 50x their own length')
                    ask_question
                elif result == [9]:
                    print('squirrel')
                    print('  ')
                    print('Fun Fact:')
                    print('Squirrels can find food buried beanth a foot of snow')
                    ask_question
                else:
                    print('cant predict')

            except:
                print("Sorry, I do not know that. Be more specific!")
        elif cmd == 6: # Quiz functions 
            try:
                quiz()
            except:
                print("Sorry, I do not know that. Be more specific!")

        elif cmd == 7:  # if input pattern is "I know that * of *"
            ans = object, subject = params[1].split(' is ')
            expr = read_expr(subject + '(' + object + ')')
            #This line checks for contradiction with Clause
            contradictAns = Clause(ans).is_tautology()
            if contradictAns: # If expr contradicts with contradictAns
                # If expr contradict with the file
                print("Could not add cause of contradiction")
            else:
                # If expr does not contradict
                kb.append(expr)
                print('OK, I will remember that', object, 'is', subject)
        elif cmd == 8:  # if the input pattern is "check that * is *"
            ans = object, subject = params[1].split(' is ')
            expr = read_expr(subject + '(' + object + ')')
            answer = ResolutionProver().prove(expr, kb, verbose=True)
            contradictFact = Clause(ans).is_tautology()
            if answer and not contradictFact:
                #If answer is true
                print('Correct.')
            elif not answer and not contradictFact:
                # If answer is false
                print('Incorrect')

            else:
                # Any other error
                print('Theres some error with input')
        elif cmd == 99:
            print("I did not get that, please try again.")
    else:
        print(answer)