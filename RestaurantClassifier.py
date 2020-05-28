import pandas as pd
from sklearn import svm
from nltk import sent_tokenize, word_tokenize, pos_tag
from nltk.corpus import stopwords
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
import csv
from app import app

wordDict = {"can't": "can not", "don't": "do not", "i'll": "i will", "it's": "it is", "didn't": "did not",
            "could'nt": "could not", "you'll": "you will", "wasn't": "was not", "won't": "would not",
            "I'm": "I am"}


def remove_punctuation(input_text):
    input_text = re.sub(r'[^\w\s]', '', input_text)
    return input_text


noise_list = set(stopwords.words('english'))


def remove_noise(input_text):
    words = word_tokenize(input_text)
    noise_free_words = [word for word in words if word not in noise_list]
    noise_free_text = " ".join(noise_free_words)
    return noise_free_text


def sentence_tokenizer(text):
    sentences = sent_tokenize(text)
    return sentences


def word_tokenizer(text):
    words = word_tokenize(text)
    return words


def multipleReplace(text, wordDict):
    for key in wordDict:
        text = text.replace(key, wordDict[key])
    return text


def cleanedComment(text):
    try:
        text = text.lower()
    except:
        text = text
    try:
        text = multipleReplace(text, wordDict)
    except:
        text = text
    try:
        text = remove_punctuation(text)
    except:
        text = text
    try:
        text = remove_noise(text)
    except:
        text = text
    return text


def sentiment_process(data, test, classes, fileName):
    train_cleanedData = []
    for txt in data.iterrows():
        train_cleanedData.append(cleanedComment(txt[1]['Comment']))
    vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), stop_words='english')
    train_vectors = vectorizer.fit_transform(train_cleanedData)
    vocab = vectorizer.get_feature_names()

    test_cleanedData = []
    for txt in test.iterrows():
        if type(txt[1]['Comment']) in [float, int]:
            txt[1]['Comment'] = str(txt[1]['Comment'])
        test_cleanedData.append(cleanedComment(txt[1]['Comment']))
    test_vectors = vectorizer.transform(test_cleanedData)

    train_vectors = train_vectors.toarray()
    test_vectors = test_vectors.toarray()

    for cls in classes:
        print("Before Model")
        model = svm.SVC(kernel='linear')
        print(cls)
        model.fit(train_vectors, data[cls])
        print("After Model")
        prediction = model.predict(test_vectors)
        print("After Prediction")
        test[cls] = prediction
    test.to_csv("/home/repusight/data/classified_data/" + fileName, ',', encoding='utf-8', index=False, header=True)
    classifieddata = []
    with open("/home/repusight/data/classified_data/" + fileName) as f:
        classifieddata = [{k: v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]
    datatoinsert = []
    for a in classifieddata:
        if a['ReviewID'] == '':
            reviewid = a['ReviewID']
        else:
            try:
                reviewid = int(a['ReviewID'])
            except:
                reviewid = int(float(a['ReviewID']))
        datatoinsert.append(
            {'Hygiene': int(a['Hygiene']), 'Date': int(a['Date']), 'Rimg': a['Rimg'], 'Drinks': int(a['Drinks']),
             'Taste': int(a['Taste']), 'Replied': a['Replied'], 'icon': a['icon'], 'Rname': a['Rname'],
             'ReviewID': reviewid, 'Logo': a['Logo'], 'URL': a['URL'], 'Comforts': int(a['Comforts']),
             'Comment': a['Comment'], 'Service': int(a['Service']), 'Value': int(a['Value']),
             'Rating': float(a['Rating']), 'Entertainment': int(a['Entertainment']), 'Sentiment': int(a['Sentiment']),
             'Place': a['Place'], 'Ambience': int(a['Ambience']), 'Channel': a['Channel'], 'Name': a['Name'],
             'City': a['City'], 'Variety': int(a['Variety']), 'Hospitality': int(a['Hospitality']), 'State': a['State'],
             'Country': a['Country']})
    app.config['RESTAURANT_COLLECTION'].insert(datatoinsert)
    print(datatoinsert)


def restaurantClassifier(filter):
    try:

        classes = ["Sentiment", 'Taste', 'Variety', 'Drinks', 'Service', 'Value', 'Hygiene', 'Ambience', 'Hospitality',
                   'Comforts', 'Entertainment']

        path1 = filter["filePath"]

        fileName = path1.split("/")[-1]

        data = pd.read_csv(r"/home/repusight/PycharmProjects/crawlClassify/app/static/data/train_restaurant.csv")
        test = pd.read_csv(os.path.normpath(path1), delimiter="," ,encoding = "ISO-8859-1")

        fileName = fileName.replace(" ", "")
        sentiment_process(data, test, classes, fileName)
        print("Classified & Data Inserted")
        return "Classified & Data Inserted"
    except Exception as e:
        print(e)
        return "Something is wrong!"
