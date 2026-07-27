from __future__ import annotations

import random

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs, sir.",
    "I would tell you a UDP joke, but you might not get it, sir.",
    "There are 10 types of people in the world: those who understand binary and those who don't, sir.",
    "Why do Java developers wear glasses? Because they don't see sharp, sir.",
    "I told my computer I needed a break, and now it won't stop sending me KitKat ads, sir.",
    "Why was the robot so tired? It had a hard drive, sir.",
    "An SQL query walks into a bar, walks up to two tables and asks: can I join you, sir?",
    "Why did the AI go to therapy? Too many deep learning issues, sir.",
]

QUOTES = [
    "Sometimes you gotta run before you can walk. - Tony Stark",
    "The best way to predict the future is to create it, sir.",
    "Genius is one percent inspiration and ninety-nine percent perspiration, sir.",
    "It is not the mountain we conquer, but ourselves, sir.",
    "The only way to do great work is to love what you do, sir.",
    "Do or do not. There is no try, sir.",
    "I am Iron Man's mind, and you are its user, sir. Let's build something remarkable.",
    "Success is not final, failure is not fatal: it is the courage to continue that counts, sir.",
]


def random_joke() -> str:
    return random.choice(JOKES)


def random_quote() -> str:
    return random.choice(QUOTES)
