from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    SlotSet,
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
    FollowupAction,
)

import requests
import html2text
import json
import random
import logging
import os
import openai

logger = logging.getLogger(__name__)

class WikipediaAction(Action):
    def name(self):
        return "action_wikipedia_pregunta"

    def run(self, dispatcher, tracker, domain):

        intent = tracker.latest_message["intent"].get("name")
        logger.info(intent)
        try:
            entity = tracker.latest_message["entities"][0]["entity"] 
        except:
            entity = "cosa"
        logger.info(entity)
        value = next(tracker.get_latest_entity_values(entity), None)
        logger.info(value)

        if value != None:
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
             text = "Aquí en Getafe hay "
        else:
             text = "En " + ciudad + " hay "
        
        # OpenWeatherMap API - Pseudonimo API key
        query = ciudad + ',es&lang=es&units=metric&appid=52b049e3be4e6efd8cff05a01210b266'
        r = requests.get('https://api.openweathermap.org/data/2.5/weather?q={}'.format(query))
        response = r.json()
        #print(response)
        cielo = response["weather"][0]["description"]
        #print(cielo)
        temperatura = int(response["main"]["temp"])
        #print(temperatura)
        
        dispatcher.utter_message(text = text + format(cielo) + " y una temperatura de " + format(temperatura) + " grados")
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

class GPTs(Action):
    def name(self):
        return "action_GPTs"

    def run(self, dispatcher, tracker, domain):
        stop = "\nHumano: IA:"

        messages=[
            {"role": "system", "content": "Eres un asistente virtual que das conversación de manera breve, tranquila y distendida."},
            {"role": "user", "content": tracker.latest_message["text"] + """},
            {"role": "assistant", "content": """}
        ]

        openai.api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("model")
        openai_response = openai.chat.completions.create(model=model, max_tokens=150, messages=messages, stop=stop, temperature=0.4, top_p=1, frequency_penalty=0.0, presence_penalty=0.6)
        response = openai_response['choices'][0]['message']['content'].split("\n")[0]

        dispatcher.utter_message(text=format(response))
        return [SlotSet("GPT", "true")]
    