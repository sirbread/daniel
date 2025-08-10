# Daniel

## What's Daniel?
Daniel is a communications interface which is connected to both Slack and Discord. It used Flask as a backend and allows for multiple people to send messages to both channels.

## Setting Up
In the root directory, run:
```python -m venv venv```

```./venv/Scripts/Activate.ps1```

```pip install -r requirements.txt```

```python main.py```

Then, open up a new terminal in ```daniel-slack``` and run:
```python -m venv venv```

```./venv/Scripts/Activate.ps1```

```pip install -r requirements.txt```

```python app.py```

This will start the Slack interface.

You'll also need a slack bot token (obtained by creating a new app) and a Discord bot token (obtained from creating a new app), and place them into their respective .env files.

Navigating to localhost:5008 will greet you with an interface to send the cross-platform messages.

![](https://hc-cdn.hel1.your-objectstorage.com/s/v3/084786d7d3d1cc4e10f1b2cf1d5714d5923d8756_image.png)