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
virtualenv -p python3.10 [environment name]
```

2. Use this command to install packages

```
pip install -r requirements.txt
```

3. create a .env file with the following (add to .gitignore)

```
client_id = "YOUR ID HERE"
client_secret = "YOUR SECRET HERE"

secret_key = "GENERATE A PASSWORD"
secret_config = 'SOME NAME'
```

4. Start the flask server
