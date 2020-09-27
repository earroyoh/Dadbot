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

## Usual vane conversation

* greet
    - utter_greet
* ask_estado
    - utter_ask_que_te_cuentas
* mood_happy
    - utter_happy
* ask_actividad
    - utter_respond_actividad
* mood_affirm
    - utter_happy
    - utter_happy_proverbio
* mood_affirm
    - utter_happy
    - action_openweather_tiempo
* ask_actividad
    - utter_respond_actividad
* inform_estado{"actividad":"correr"}
    - slot{"actividad":"correr"}
    - utter_ask_que_te_cuentas
* goodbye
    - utter_goodbye

## New curious user
* ask_nombre
    - utter_respond_nombre
* greet
    - utter_greet
* ask_vivienda
    - utter_respond_vivienda
* inform_ciudad{"ciudad":"Getafe"}
    - slot{"ciudad":"Getafe"}
	- action_wikipedia_pregunta
    - utter_did_that_help
    - action_listen
* mood_affirm
    - utter_goodbye

## New curious user II

* ask_nombre
    - utter_respond_nombre
* greet
    - utter_greet
* ask_estado
    - utter_respond_estado
    - utter_ask_que_te_cuentas
* ask_deporte_bici
    - utter_respond_deporte_bici
* ask_ocupacion
    - utter_respond_ocupacion
* ask_gustos
    - slot{"actividad":"leer"}
    - utter_respond_gustos
* goodbye
    - utter_goodbye

## Help interest

* greet
    - utter_greet
* ask_help
    - utter_respond_help
* ask_help
    - utter_respond_help
    - utter_happy
* mood_happy
    - utter_happy
    - utter_ask_que_te_cuentas
* goodbye
    - utter_goodbye

## Usual vane conversation III

* greet
    - utter_greet
* inform_actividad
    - utter_happy
    - utter_respond_actividad
* mood_affirm
    - utter_happy
    - utter_happy_proverbio
* mood_affirm
    - utter_happy
    - utter_ask_que_te_cuentas
* goodbye
    - utter_happy
    - utter_goodbye
* goodbye

## Bad mood

* inform_estado
    - utter_ask_que_te_cuentas
* mood_unhappy
    - utter_unhappy
    - utter_unhappy_proverbio
* mood_unhappy
    - utter_did_that_help
* mood_affirm
    - utter_goodbye

## Informative conversation

* inform_estado
    - utter_ask_que_te_cuentas
* inform_actividad
    - utter_happy
    - utter_happy_proverbio
* mood_happy
    - utter_happy
    - utter_respond_actividad
* goodbye
    - utter_goodbye

## Usual vane conversation IV

* greet
    - utter_greet
* ask_actividad
    - utter_respond_actividad
* ask_razon
    - utter_respond_razon
* mood_happy
    - utter_ask_que_te_cuentas
* ask_comida
    - utter_respond_comida
* mood_affirm
    - utter_happy
    - utter_happy_proverbio
* goodbye
    - utter_goodbye

## Usual vane conversation V

* greet
    - utter_greet
    - utter_respond_cuenta_algo
* inform_actividad
    - utter_respond_actividad
    - utter_ask_que_te_cuentas
* inform_actividad
    - utter_happy
* goodbye
    - utter_goodbye

## Usual vane conveersation VI

* greet
    - utter_greet
    - utter_respond_cuenta_algo
* inform_actividad
    - utter_respond_actividad
    - utter_ask_que_te_cuentas
* inform_actividad
    - utter_happy
* goodbye
    - utter_goodbye
