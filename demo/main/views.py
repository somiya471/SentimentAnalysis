import json
import pickle

import PyPDF2
import spacy
import pandas as pd
from textstat.textstat import textstatistics,textstat

import fitz
import plotly
from django.http import HttpResponse
from django.shortcuts import render, redirect
from textblob import TextBlob
from google.transliteration import transliterate_text
from deep_translator import GoogleTranslator
from django.conf import settings
from django.core.mail import send_mail
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import re
from wordcloud import WordCloud, STOPWORDS
from collections import Counter
import matplotlib.pyplot as plt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


wc_data = []
input_df = None
fname = None
filename = 'saved_model.sav'
saved_classifier = pickle.load(open(filename, 'rb'))


def load_dataset(dataset):
    n_lis = []
    dataset.seek(0)
    with fitz.open(stream=dataset.read(), filetype="pdf") as doc:
        content = ""
        for page in doc:
            text = page.get_text().strip()
            content += text
    lis = content.split("\n")
    for li in lis:
        if len(li.strip()) > 15 or li not in lis:
            n_lis.append(li.strip())
    col = "Sentences"
    data = pd.DataFrame({col: n_lis})
    data.to_csv("demo.csv")
    user_df = pd.read_csv("demo.csv")
    return user_df


def clean_text(unformatted_text):
    unformatted_text = str(unformatted_text)
    unformatted_text = re.sub(r'@[A-Za-z0-9]+', '', unformatted_text)
    unformatted_text = re.sub(r'#', '', unformatted_text)
    unformatted_text = re.sub(r'&', '', unformatted_text)
    unformatted_text = re.sub(r"'", '', unformatted_text)
    unformatted_text = re.sub(r".", '', unformatted_text)
    unformatted_text = re.sub(r",", '', unformatted_text)
    unformatted_text = re.sub(r"@", '', unformatted_text)
    unformatted_text = re.sub(r"/", '', unformatted_text)
    unformatted_text = re.sub(r"-", '', unformatted_text)
    unformatted_text = re.sub(r'RT[\s]+', '', unformatted_text)
    unformatted_text = re.sub(r'https?:\/\/\S+', '', unformatted_text)
    return unformatted_text.lower()

def count_plot(x, y):
    fig = go.Figure()
    layout = go.Layout(
        title='Multiple Reviews Analysis',
        xaxis=dict(title='Category'),
        yaxis=dict(title='Count'),
        )
    fig.update_layout(dict1=layout, overwrite=True)
    fig.layout.template = "plotly_dark"
    fig.add_trace(go.Bar(name='Multi Reviews', x=x, y=y))
    graph1 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graph1


def pie_plot(count_positive, count_negative, count_neutral):
    df = pd.DataFrame([['Positive', 'Negative', 'Neutral'], [count_positive, count_negative, count_neutral]]).T
    df.columns = ['type', 'count']
    fig2 = px.pie(df, values='count', names='type', title='Overall Sentiment', hole=0.3)
    fig2.update_traces(marker=dict(colors=['green', 'red', 'blue']))
    fig2.layout.template = "plotly_dark"
    graph2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    return graph2

def word_cloud_plot(name):
    global wc_data

    STOPWORDS.update(["i", "i'm", "im", "it", "this", "will", "they", "it's", "for", "a", "the", "them", "to", "'", "."
                      "?", "/", "<", ">", "</", "/>","I"])
    wc_data = [data for data in wc_data if data not in STOPWORDS and len(data)>=5]
    word_could_dict = Counter(wc_data)
    wc = WordCloud().generate_from_frequencies(word_could_dict)
    fig3 = plt.figure(figsize=(20,10), facecolor='k')
    plt.imshow(wc)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(f'main/static/demo/{name}.png', facecolor='k', bbox_inches='tight')
    #graph3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    #return graph3

def sentiment_over_time_plot(date,date_present, input_df):
    if date == 'YES':
        line_df = input_df.groupby([date_present, 'sentiment']).size().unstack(fill_value=0)
        fig4 = px.line(line_df, x=line_df.index, y=line_df.columns[0:], markers=True,
                       color_discrete_sequence=['red', 'blue', 'green'])
        fig4.layout.template = "plotly_dark"
        graph4 = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
        return graph4

def sentiment_by_words(input_df, temp_df):
    global wc_data
    wc_data = [data for data in wc_data if data not in STOPWORDS and len(data) >= 5]
    word_could_dict = Counter(wc_data)
    most_common = word_could_dict.most_common(5)
    for i in range(len(most_common)):
        pos, neg, neu = 0, 0, 0
        for j in range(input_df.shape[0]):
            try:
                if most_common[i][0] in temp_df.iloc[j]:
                    if input_df.sentiment.iloc[j] == 'Positive':
                        pos += 1
                    elif input_df.sentiment.iloc[j] == 'Negative':
                        neg += 1
                    elif input_df.sentiment.iloc[j] == 'Neutral':
                        neu += 1
                else:
                    continue
            except:
                pass

        most_common[i] += (pos, neg, neu)
    word_df = pd.DataFrame(most_common, columns=['Word', '', 'Positive', 'Negative', 'Neutral'])

    fig5 = px.bar(word_df, y="Word", x=word_df.columns[2:], color_discrete_sequence=['green', 'red', 'blue'],
                  title="Sentiment Analysis By Word", orientation='h')
    fig5.layout.template = "plotly_dark"
    graph5 = json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)
    return graph5

def calculatesentiment(single_review):
    text = TextBlob(single_review)
    result = text.sentiment.polarity
    if 0 <= result < 0.5:
        transliterated_text = transliterate_text(single_review, lang_code='hi')
        eng_text = GoogleTranslator(source='auto', target='en').translate(transliterated_text)
        text = TextBlob(eng_text)
        result = text.sentiment.polarity
    return result


def predict(request):
    a = None
    if request.method == "POST":
        djtext = request.POST.get('text', 'default')
        result = calculatesentiment(djtext)
        if result >= 0.5:
            a = "positive"
        elif result < 0:
            a = "negative"
        else:
            a = "neutral"
        return render(request, "demo/index.html", {'a': a})
    return render(request, "demo/index.html", {'a': a})

# Create your views here.
def home(request):
    return render(request,"demo/index.html")
    #return HttpResponse("Hello Home")

def contact(request):
    return render(request,"demo/contact.html")

def aboutus(request):
    return render(request,"demo/aboutus.html")

def dashboard(request):
    return render(request,"demo/dashboard.html")

def submit(request):
    if request.method == "POST":
        nameget = request.POST.get('name','default')
        emailadd = request.POST.get('email','default')
        messageget = request.POST.get('message','default')
    subject = 'Message from '+nameget + 'Email address: '+ emailadd
    message = messageget
    email_from = settings.EMAIL_HOST_USER
    recipient = ['somiyapanikar@gmail.com',]
    send_mail(subject,message,email_from,recipient)
    return HttpResponse('Mail Sent Successfully')


def load_data(request):
    global wc_data,input_df, fname
    count_positive, count_negative, count_neutral = 0, 0, 0
    if request.method == "POST":
        try:
            csvget = request.FILES["csv_files"]
            fname = csvget.name
            user_dataframe = load_dataset(csvget)
            input_df = user_dataframe.copy()
            wc_data = []
        except:
            return render(request, "demo/dashboard.html")
        opt = "Sentences"
        if input_df is not None:
            input_df1 = input_df.head(5)
            data_html = input_df1.to_html()
            list_of_columns = list(input_df.columns)
            if opt:
                temp_df = input_df[opt]
                input_df['sentiment'] = ''
                input_df[opt] = input_df[opt].apply(clean_text)
                for i in range(temp_df.shape[0]):
                    wc_data += str(temp_df.iloc[i]).split()
                    text = TextBlob(str(temp_df.iloc[i]))
                    result = text.sentiment.polarity
                    if result >= 0.1:
                        count_positive += 1
                        text_sentiment = 'Positive'
                    elif result < 0:
                        count_negative += 1
                        text_sentiment = 'Negative'
                    else:
                        text_sentiment = "Neutral"
                        count_neutral += 1
                    input_df['sentiment'].iloc[i] = text_sentiment
                total = count_positive + count_negative + count_neutral
                x = ["Positive", "Negative", "Neutral"]
                y = [count_positive, count_negative, count_neutral]
                if count_positive == max(count_positive, count_negative, count_neutral):
                    review = """## The Sentiment is Positive !!"""
                elif count_negative == max(count_positive, count_negative, count_neutral):
                    review = """## The Sentiment is Negative !!"""
                else:
                    review = """## The Sentiment is Neutral"""
                graph1 = count_plot(x,y)
                graph3 = sentiment_by_words(input_df, temp_df)
                graph2 = pie_plot(count_positive, count_negative, count_neutral)
                word_cloud_plot(fname)
                context = {'loaded_data': data_html, 'review': review, 'graph1': graph1,
                           'graph2': graph2,'graph3': graph3, "name":fname}
                return render(request, "demo/dashboard.html", context)
            context = {'loaded_data': data_html}
            return render(request, "demo/dashboard.html", context)
        return render(request,"demo/dashboard.html")
    return render(request, "demo/dashboard.html")

def loginpage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_name = User.objects.get(username=username)

        if user_name is not None:
            user = authenticate(username=username, password=password)
            login(request, user)
            fname = user_name.first_name
            return render(request,"demo/index.html")

        else:
            return redirect("home")

    return render(request,"demo/login.html")

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        myuser = User.objects.create_user(username,email,password)
        myuser.first_name = fname
        myuser.last_name = lname

        myuser.save()

        return redirect('loginpage')
    return render(request,"demo/register.html")

def logoutpage(request):
    logout(request)
    return redirect('/')


def calculatesent(single_review):
    result = saved_classifier(single_review)
    if result == 0:
        transliterated_text = transliterate_text(single_review, lang_code='hi')
        eng_text = GoogleTranslator(source='auto', target='en').translate(transliterated_text)
        result = saved_classifier(eng_text)
    return result

def predictsentiment(request):
    a = None
    if request.method == "POST":
        djtext = request.POST.get('text', 'default')
        result = calculatesent(djtext)
        if result == 1:
            a = "positive"
        elif result == -1:
            a = "negative"
        else:
            a = "neutral"
        return render(request, "demo/index.html", {'a': a})
    return render(request, "demo/index.html", {'a': a})

