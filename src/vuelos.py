#Streamlit permite crear intefases de usuario (UI), "st" es un diminutivo streamlite.
import streamlit as st
#Permite llamar a un modelo de chatbot de OpenAI.
from langchain.chat_models import ChatOpenAI
#Permite llamar a agentes de SQL que permite la coordinacion entre la plataforma de Streamlit, OpenAI y SQL
from langchain.agents import create_sql_agent
#Este toolkit de herramienta nos permite conectarnos a la base de datos habilitando todas las funcionalidades de la misma.
from langchain.agents.agent_toolkits import SQLDatabaseToolkit 
#Esto permite la conexion con la base de datos.
from langchain.sql_database import SQLDatabase 

#Esta liberia permite procesar imagenes.
from PIL import Image
#Permite almacenar la clave de acceso al OpenAI (API Key)
import key

#Permite colocar las credenciales para conectarse a la base de datos en PostgreSQL

db = SQLDatabase.from_uri("postgresql://usr_llm:usr_llm@localhost:5432/flights")

#Permite configurar la pestaña del Browser
st.set_page_config(
    page_title = "Vuelos",
    page_icon = "https://uxwing.com/wp-content/themes/uxwing/download/transportation-automotive/plane-icon.png"
)
#Permite configurar lo que se muestra en la parte izquierda del chatbot
with st.sidebar:  
    image = Image.open('../resource/Logo_UE.jpg')  
    st.image(image)  
    st.markdown(
    "<h1 style='text-align: center;'>Sistema de Generacion de Consultas SQL Basado en Peticiones en Lenguaje Natural a partir de un Chatbot</h1>",
    unsafe_allow_html=True
)
    image2 =  Image.open('../resource/logo_botSQL.jpg')  
    st.image(image2)
    st.markdown("Hecho por Balmore Brito")
    
#Esto permite configurar el mensaje del lado derecho del chatbot
msg_chatbot = """
        Soy un chatbot que te puede ayudar a realizar análisis de los datos de vuelo.
        
        ### Preguntas frecuentes
                
        - ¿Cuantos vuelos se realizaron en el mes actual?
        - ¿Cuantos vuelos se realizaron en el mes actual por cada destino?
        - Lo que desees:
"""
#Esto permite mostrar el mensaje inicial del chatbot y permite guardar en memoria el historial del chatbot. (Lista)
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content" : msg_chatbot}]
   

#Este permita mostrar el mensaje del chatbot. Permite pintar o escribir en el chatbot(intefaces UI)      
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
#Permite borrar el historial 
def clear_chat_history():
    st.session_state.messages = [{"role" : "assistant", "content": msg_chatbot}]

#Permite la entrada de la consulta en el chatbot.
def generate_response(question):
    #En esta linea se toman en consideracion 2 factores importantes: 1.) el modelo del LLM (OpenAI) y 2.) La temperatura (De 0 a 1), 0 es respuesta directa sin ser creativos
    # y 1 es lo maximo creativo en las respuesta.
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=key.api_openai, temperature = 0.5) 
    
    #El toolkit permita manipular la bases de datos
    toolkit = SQLDatabaseToolkit(db=db,llm=llm)
    #El agente permite coordinar y gestionar el proceso el lenguaje natural 
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
       #Permite mostrar el log si es "True"
        verbose=True,
        handle_parsing_errors=True
    ) 
    # Esta linea hace que el agente ejecute.
    question = "La respuesta debe ser en español." + question
    return agent_executor.run(question)

#Se asigna una funcion al boton especifico del sidebar.
st.sidebar.button('Limpiar historial de chat', on_click = clear_chat_history)

#Permite que valide el atributo
if key.api_openai:

    prompt = st.chat_input("Ingresa tu pregunta")
    if prompt:
        st.session_state.messages.append({"role": "user", "content":prompt})
        with st.chat_message("user"):
            st.write(prompt)

    # Generar una nueva respuesta si el último mensaje no es de un assistant, sino un user
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Esperando respuesta, dame unos segundos."):
                #Esta función toma un prompt como entrada y genera una respuesta basada en ese prompt.
                response = generate_response(prompt)
                # Este espacio en blanco podría usarse posteriormente para mostrar resultados, gráficos u otros elementos en la interfaz de usuario.
                placeholder = st.empty()
                #Esta variable se utilizará para almacenar la respuesta completa generada por el modelo.
                full_response = ''
                
                for item in response:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)

        message = {"role" : "assistant", "content" : full_response}
        st.session_state.messages.append(message) #Agrega elemento a la caché de mensajes de chat. 