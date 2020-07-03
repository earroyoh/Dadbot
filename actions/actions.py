from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet

import requests
import html2text
import json
import random

class WikipediaAction(Action):
    def name(self):
        return "action_wikipedia_pregunta"

    def run(self, dispatcher, tracker, domain):
        message_str = json.dumps(tracker.latest_message)
        message = json.loads(message_str)
        intent = message['intent']['name']
        if (message['entities']) == '':
            value = 'None'
        else:
            entity = message['entities'][0]['entity']
            value = message['entities'][0]['value']

        if intent == 'inform_pregunta' and value != 'None':
            pregunta = value

            r = requests.get("https://es.wikipedia.org/w/api.php?action=query&list=search&srprop=snippet&format=json&origin=*&utf8=&srsearch={}".format(pregunta))
            response = r.json()
            response = response["query"]["search"][0]["snippet"]
            response = response.replace('<span class=\"searchmatch\">',"").replace('</span>',"")
            response = response.split('.')[0] + "."
                
            dispatcher.utter_message(text="Dice la Wikipedia: " + format(response))

        else:
            flip = random.random()
            if flip > 0.5: 
                dispatcher.utter_message(text="No entiendo lo que me dices")
            else:
                dispatcher.utter_message(text="No sé lo que me quieres decir")
        return []
    
class WeatherAction(Action):
    def name(self):
        return "action_openweather_tiempo"
     
    def run(self, dispatcher, tracker, domain):
        ciudad = tracker.get_slot("ciudad")
        if (format(ciudad) == "None"): 
             ciudad = "Getafe" ## Initialization
             text = "Aquí en Getafe "
        else:
             text = ""
        
        # OpenWeatherMap API
        query = ciudad + ',es&lang=es&units=metric&appid=<YOUR OPENWEATHERMAP API KEY>'
        r = requests.get('https://api.openweathermap.org/data/2.5/weather?q={}'.format(query))
        response = r.json()
        #print(response)
        cielo = response["weather"][0]["description"]
        #print(cielo)
        temperatura = int(response["main"]["temp"])
        #print(temperatura)
        
        dispatcher.utter_message(text = text + format(cielo) + " y una temperatura de " + format(temperatura) + " grados.")
        return []

class NewsAction(Action):
    def name(self):
        return "action_ultimas_noticias"

    def run(self, dispatcher, tracker, domain):

        # RTVE JSON latest news
        r = requests.get("http://www.rtve.es/api/noticias.json")
        response = r.json()
        response = response["page"]["items"][0]["longTitle"]
        response = html2text.html2text(response).replace('*',"").replace('\n', "")
        response = response.split('.')[0] + "."

        dispatcher.utter_message(text="Estas son las últimas noticias: " + format(response))
        return []

