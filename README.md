
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
* [Deployment](#deployment)
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

![Diagram of the project](images/project_diagram.png)

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
In the following picture you can see an overview of the FastAPI documentation and it's available endpoints:
![Overview of the API endpoints](images/endpoint_docs_screenshot.png)  
  
In the following picture you see some example messages from a human telegram user and the answers given by the chat bot after interpreting the humans message and building a query to the database:

![Overview of the API endpoints](images/example_screenshot1.png)

![Overview of the API endpoints](images/example_screenshot2.png)

![Overview of the API endpoints](images/example_screenshot3.png)

## Quick Start 

### Requirements
Make sure that you have installed the following software on your local system:  
* Python v3.12
* DBeaver (optional, as GUI for the database)
* git (optional, for cloning the repository)


**Also you need to set up a telegram bot.** Therefore you simply write a telegram message with `/start` to @Botfather and follow the instructions as given by the BotFather. Make sure you **keep up the `TELEGRAM_BOT_TOKEN`** afterwards for the next step when it comes to configuration of environment variables.


### Installation


1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yhupe/whatsapp-data-hub.git](https://github.com/DEIN_USERNAME/whatsapp-data-hub.git)
    cd whatsapp-data-hub
    ```

2.  **Create and activate virtual environment** (if not happening autmatically):
**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```
**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration of environment variables (local):** 

    Create a `.env`-file in the root folder of your project and add the local environmental variables.

`DATABASE_URL = "postgresql://user:password@localhost:5432/mydatabase"` 

`TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"` # generate your own token via @botfather in telegram

`FASTAPI_BASE_URL = "http://localhost:8000"` 

`JWT_SECRET_KEY = "yKaU600z2xtGiakVcZWxhw8_DzyTX9V8WZkpFHnKnjU"` 

`ACCESS_TOKEN_EXPIRE_MINUTES = "30"`   

`OPENAI_API_KEY = "your_open_ai_API_key"` # add your own API key

`DOCS_USERNAME = "your_username"` # your own username to protect the FastAPI /docs in the browser

`DOCS_PASSWORD = "your_password"` # your own password to protect the FastAPI /docs in the browser

### Execution
**After installation is done and  `.env`-file is configured:**

1.  **Create database tables (one-time):**
    ```bash
    python create_tables.py
    ``` 

Make sure that your local PostgreSQL database is running and the `DATABASE_URL` in `.env` points to it.

2.  **Start the FastAPI-App:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The API is available under `http://localhost:8000`, the Swagger-UI under `http://localhost:8000/docs`.

3.  **Start the Telegram bot (in a separate local terminal):**

    ```bash
    PYTHONPATH=. python -m telegram_bot.bot
    ```

4.  **Process CRUD operations on the FastAPI and initiate the chat with your chat bot:**

Use a tool like postman or navigate to the Swagger UI docs with http://localhost:8000/docs. From here you can perform POST, UPDATE, DELETE and PATCH operations on the database tables `Employees` and `Products`.     

Further Information on the endpoints themself you can find in the Swagger UI documentation.   
  
After you have filled the tables with some life you can navigate to the telegram chat with the BotFather mentioned above, it has provided you with a link to open a chat with your chat bot. When you opened the chat, simply initiate the chat with clicking the `start`- button or sending /start. Then follow the instructions given by the chat bot, regarding verification and gaining full access to the bot. 

## Deployment

The project has been deployed on https://fly.io.

* **Live-Application:** The FastAPI-App is live available under: [https://whatsapp-data-hub.fly.dev/](https://whatsapp-data-hub.fly.dev/)
* **Providing process:** The procect can be deployed with `flyctl deploy` on Fly.io, where a Dockerfile is used to containerize the environment. The secrets or environmental variables are managed with `flyctl secrets`.
* **Monitoring:** Logs can be viewed with `flyctl logs`.



## Licence 

Dieses Projekt ist unter der [MIT License](LICENSE) lizenziert.

## Contact 


