# CS411-Team5: Head-To-Head

## What it do

Web application that allows you to compare your "Spotify Wrapped" (Spotify API) with your friends all year round (compare your stat's "head to head.").

## How do

Current tech stack choice:

- React.js
- Flask
- MySQL (Or some kind of SQL)

Planned API's:

- Spotify
- OpenAI DALL·E

## Installation

1. Use virtualenv to create a environment and start it (perferrably python3.9+)
```
virtualenv -p python3.10 environmentName
```

2. Start the virtual environment in terminal, you're always going to work within this environment
```
Mac/Linux:
source environmentName/bin/activate

Windows cmd:
environmentName\Scripts\activate
```

3. Use this command to install packages
```
pip install -r requirements.txt
```

4. create a .env file with the following (add to .gitignore)
```
client_id = "YOUR ID HERE"
client_secret = "YOUR SECRET HERE"

secret_key = "GENERATE A PASSWORD"
secret_config = 'SOME NAME'
```

5. Start the flask server with command "flask run"
