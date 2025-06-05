
# 📳 The Messenger Data Hub 

## Disclaimer
This is my final project MVP for my Software Engineering training programme.   
First of all - don't get confused by the repo name; my intention was to use the Meta Business (WhatsApp) API but then I found out that there exists something called Telegram. And compared to WhatsApp, it is totally free to use 😃 Thats why its called Whatsapp but in reality it is Telegram! 

## Overview
The Messenger Data Hub project basically consists of a backend of FastAPI endpoints, a relational database, a Telegram bot and a service layer to allow authenticated Telegram users to interact with a database.  
Thinking of a use case where let's say we work for a company. Different employees of the company may need quick and easy but still safe access to important information about products or services they sell or produce or information about business partners they work with.   

With my Messenger Data Hub, natural human language received by the Telegram bot is translated into an intent object, which then dynaically becomes utilized to build a database query, based on the raw message content sent by the Telegram user.   
  
## Functions

* __Intelligent querys:__ Ask in natural language for information about business partners, products or other employees
* __Safe authentication:__ Thanks to JWT, a magic link process makes sure that only verified employees get access . 
* __Database integration:__ Access to a PostgreSQL database to deliver the requested information.
* __Logging:__ All inbound messages and outbound system responses are logged for transparency and debugging reasons.

## Technology Stack

* __Languages:__
  * Python
  * HTML
  * CSS
* __bot framework:__ Telegram Bot API
* __web framework:__ FastAPI
* __database:__ PostgreSQL
* __database containerization:__ Docker
* __ORM:__ SQLAlchemy
* __AI:__ openAI
* __authentication:__ JWT 
* __dependency management:__ pip (requirements.txt)



