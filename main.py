#!/usr/bin/env python

import uuid
import random

import flask
from flask import Flask, render_template, request, redirect, url_for
from google.cloud import firestore


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


def add_word(room_name, word):
  """Add word into collection."""
  if word:
    db = firestore.Client()
    room_ref = db.collection("rooms").document(room_name)
    # TODO: Should document ID be different from word?
    doc_ref = room_ref.collection("charades_words").document(word)
    doc_ref.set({"word" : word})

def get_random_word(room_name):
  """Get random word fromt the previously added ones."""
  db = firestore.Client()
  room_ref = db.collection("rooms").document(room_name)
  collection_ref = room_ref.collection("charades_words")
  word_refs = collection_ref.stream()
  word_refs = list(word_refs)

  if not word_refs:
    return "No more words left :(", 0

  random_word_ref = random.choice(word_refs)
  random_word = random_word_ref.id
  # Delete the chosen word so it doesn"t get drawn again.
  collection_ref.document(random_word).delete()

  num_words_left = len(word_refs) - 1
  return random_word, num_words_left


@app.route("/")
def index():
  return render_template("index.html",
                         new_room_url = url_for("new_room"))

@app.route("/room/", methods=["GET", "POST"])
def new_room():
  if "room_name" in request.values:
    room_name = request.values["room_name"]
  else:
    # Create a random name.
    room_name = uuid.uuid4()
  return redirect(url_for("charades", room_name=room_name))

@app.route("/room/<room_name>", methods=["GET", "POST"])
def charades(room_name):
  if "add_word" in request.values:
    add_word(room_name, request.values["add_word"])

  random_word = ""
  num_words_left = None
  if "get_random_word" in request.values:
    random_word, num_words_left = get_random_word(room_name)

  return render_template("charades.html",
                         room_url = url_for("charades", room_name = room_name, _external = True),
                         random_word  = random_word,
                         num_words_left = num_words_left)


if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)
