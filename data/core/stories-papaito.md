## happy path               <!-- name of the story - just for debugging -->
* greet
  - utter_greet
* mood_happy               <!-- user utterance, in format intent[entities] -->
  - utter_happy
* mood_affirm
  - utter_ask_que_te_cuentas

## sad path 1               <!-- this is already the start of the next story -->
* greet
  - utter_greet             <!-- action the bot should execute -->
* mood_unhappy
  - utter_ask_que_te_cuentas
* mood_unhappy
  - utter_unhappy_proverbio
  - utter_did_that_help
* mood_affirm
  - utter_happy
  - utter_respond_cuenta_algo

## sad path 2
* greet
  - utter_greet
* mood_unhappy
  - utter_ask_que_te_cuentas
* mood_unhappy
  - utter_unhappy_proverbio
  - utter_did_that_help
* mood_deny
  - utter_goodbye

## sad path 3
* greet
  - utter_greet
* mood_unhappy
  - utter_unhappy_proverbio
  - utter_did_that_help
* mood_affirm
  - utter_happy

## in good mood
* mood_happy
  - utter_respond_cuenta_algo
  - utter_ask_que_te_cuentas

## in bad mood
* mood_unhappy
  - utter_respond_cuenta_algo
  - utter_ask_que_te_cuentas

## Famous Question
* inform_pregunta{"famoso":"Messi"}
  - action_wikipedia_pregunta

## Meal question
* inform_pregunta{"plato":"sopa de ajo"}
  - action_wikipedia_pregunta

## City question
* inform_pregunta{"pais":"España"}
  - action_wikipedia_pregunta

## Something question
* inform_pregunta{"cosa":"violín"}
  - action_wikipedia_pregunta

## Activity interest 
* inform_estado{"actividad":"correr"}
  - action_openweather_tiempo

## City weather interest 
* inform_ciudad{"ciudad":"Getafe"}
  - action_openweather_tiempo

## Gustos plato
* ask_gustos{"plato":"pisto"}
  - utter_respond_gustos{"plato":"pisto"}

## Sport likes
* ask_gustos{"deporte":"fútbol"}
  - utter_respond_gustos{"deporte":"fútbol"}

## Latest news
* ask_ultimas_noticias
  - action_ultimas_noticias

## strange user
* mood_affirm
  - utter_happy
  - utter_happy_proverbio
* mood_unhappy
  - utter_unhappy_proverbio
* mood_affirm
  - utter_unclear

## say goodbye
* goodbye
  - utter_goodbye

## respond nombre
* ask_nombre
  - utter_respond_nombre

## respond pais
* ask_pais
  - utter_respond_pais

## respond vivienda
* ask_vivienda
  - utter_respond_vivienda

## respond deporte bici
* ask_deporte_bici
  - utter_respond_deporte_bici

## respond deporte futbol
* ask_deporte_futbol
  - utter_respond_deporte_futbol

## respond comida
* ask_comida
  - utter_respond_comida

## respond actividad
* ask_actividad
  - utter_respond_actividad

## respond estado
* ask_estado
  - utter_respond_estado

## respond help
* ask_help
  - utter_respond_help

## respond ocupacion
* ask_ocupacion
  - utter_respond_ocupacion

## fallback
- utter_unclear
