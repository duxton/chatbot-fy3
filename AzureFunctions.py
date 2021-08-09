# Import files from folder to be detected
import os
# Read the reviews in the /data/reviews folder
reviews_folder = os.path.join('xmlFiles')

# Create a collection of reviews with id (file name) and text (contents) properties
reviews = []
for file_name in os.listdir(reviews_folder):
    review_text = open(os.path.join(reviews_folder, file_name)).read()
    review = {"id": file_name, "text": review_text}
    reviews.append(review)
#
# for review_num in range(len(reviews)):
#     # print the review text
#     print('{}\n{}\n'.format(reviews[review_num]['id'], reviews[review_num]['text']))

# Getting the services from Azure AI
cog_key = '7f98fd1fe47a44ea9fa532ac6dec0a78'
cog_endpoint = 'https://cognitiveservicesstage4.cognitiveservices.azure.com/'
cog_region = 'uksouth'

print('Ready to use cognitive services at {} using key {}'.format(cog_endpoint, cog_key))

#Detect language from Azure AI services
from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient
from msrest.authentication import CognitiveServicesCredentials

# Get a client for your text analytics cognitive service resource
text_analytics_client = TextAnalyticsClient(endpoint=cog_endpoint,
                                            credentials=CognitiveServicesCredentials(cog_key))


# Analyze the reviews you read from the /data/reviews folder earlier
language_analysis = text_analytics_client.detect_language(documents=reviews)

# print detected language details for each review
for review_num in range(len(reviews)):
    # print the review id
    print(reviews[review_num]['id'])

    # Get the language details for this review
    lang = language_analysis.documents[review_num].detected_languages[0]
    print(' - Language: {}\n - Code: {}\n - Score: {}\n'.format(lang.name, lang.iso6391_name, lang.score))

    # Add the detected language code to the collection of reviews (so we can do further analysis)
    reviews[review_num]["language"] = lang.iso6391_name

# Extract key phrases from XML files
# # Use the client and reviews you created in the previous code cell to get key phrases

# key_phrase_analysis = text_analytics_client.key_phrases(documents=reviews)
#
# # print key phrases for each review
# for review_num in range(len(reviews)):
#     # print the review id
#     print(reviews[review_num]['id'])
#
#     # Get the key phrases in this review
#     print('\nKey Phrases:')
#     key_phrases = key_phrase_analysis.documents[review_num].key_phrases
#     # Print each key phrase
#     for key_phrase in key_phrases:
#         print('\t', key_phrase)
#     print('\n')

# Translate
# Create a function that makes a REST request to the Text Translation service
def translate_text(cog_region, cog_key, text, to_lang='zh-CN', from_lang='en'):
    import requests, uuid, json

    # Create the URL for the Text Translator service REST request
    path = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0'
    params = '&from={}&to={}'.format(from_lang, to_lang)
    constructed_url = path + params

    # Prepare the request headers with Cognitive Services resource key and region
    headers = {
        'Ocp-Apim-Subscription-Key': cog_key,
        'Ocp-Apim-Subscription-Region':cog_region,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # Add the text to be translated to the body
    body = [{
        'text': text
    }]

    # Get the translation
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    return response[0]["translations"][0]["text"]


# Translate key phrases only
# for key_phrase in key_phrases:
#     translation = translate_text(cog_region, cog_key, key_phrase, to_lang='zh-CN', from_lang='en')
#     print('{} -> {}'.format(key_phrase,translation))

# for review_num in range(len(reviews)):
#     translation = translate_text(cog_region, cog_key, review_text, to_lang='zh-CN', from_lang='en')
#     print('{} -> {}'.format(review_text, translation))