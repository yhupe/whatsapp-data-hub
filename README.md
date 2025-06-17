
# 📳 The Messenger Data Hub 

Process your data in a database via FastAPI and have authenticated access to it through Telegram!

## Content

* [Disclaimer](#disclaimer)
* [Overview](#overview)
    * [Bird's eye view](#birds-eye-view)
* [Motivation and Problem](#motivation-and-problem)
* [Highlights](#highlights)
* [Technology Stack](#technology-stack)
* [Usage and Examples](#usage-and-examples)
* [Quick Start](#quick-start)
    * [Requirements](#requirements)
    * [Installation](#installation)
    * [Execution](#execution)
* [Tests](#tests)
* [Licence](#licence)
* [Contact](#contact)

## Disclaimer
This is my final project MVP for my Software Engineering Training Programme 2024/2025.  

First of all - don't get confused by the repo name; my intention was to use the Meta Business (WhatsApp) API or a third party product like Twilio but then I found out that there exists something mighty called Telegram. Compared to WhatsApp, Telegram is totally free to use and it didn't took me hours to get even started by reading through meters of documentation 😃 Thats why its called Whatsapp but in reality it is Telegram - now you know! 

## Overview
The Messenger Data Hub project basically consists of a backend of FastAPI endpoints, a relational database, a Telegram bot and a service layer to allow authenticated Telegram users to interact with a database.    

With my Messenger Data Hub, __natural human language__ received by the Telegram bot __is translated__ into an intent object __by the help of AI__, which then dynamically becomes utilized to build a database query __in SQL language__, based on the raw message content sent by the Telegram user.  

With the already mentioned FastAPI endpoints and Swagger UI documentation, the database can be handled in many ways with focus on __CRUD__ (create, read, update, delete) __operations__.  

### Bird's eye view 
This is a diagram to help understand what is going on by one look:

## Motivation and Problem
__Here's how I came up with my MVP idea:__  
  
As I decided to focus on __Backend Software Engineering__, one of the project requirements was it not build a dedicated frontend. So I started thinking about utilizing a messenger application as my frontend.    

__And that's the reason:__ 
For me personally, practical examples and visuals are very helpful to understand things easier and quicker. I wanted to build something as my MVP where I still can show people what I did instead of just showing lines and lines of code and nobody really get's the sequence and dependencies. 


__Thinking of a use case__ where let's say we work for a company, doesn't really matter where. Different employees of the company may need quick and easy but still safe access to more or less important information about products or services they sell or produce or information about business partners they work with - or any other information that can be stored in a database.  

Of course, __this does not limit the project to business-only application__, you can fill the database tables with what ever you want, even for your very own private use where you just want to be able to retreive personal data through your phone!

## Highlights

* __Intelligent querys:__ Ask in natural language for information about business partners, products or other employees
* __Safe authentication:__ Thanks to JWT, a magic link process makes sure that only verified employees get access. 
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

## Usage and Examples

## Quick Start 

### Requirements

### Installation

### Execution

## Tests

## Licence 

## Contact 


