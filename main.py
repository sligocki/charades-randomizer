#!/usr/bin/env python

import random

from flask import Flask, render_template, request
from google.cloud import firestore


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


def add_word(word):
  """Add word into collection."""
  db = firestore.Client()
  # TODO: Should document ID be different from word?
  doc_ref = db.collection("charades_words").document(word)
  doc_ref.set({"word" : word})

def get_random_word():
  """Get random word fromt the previously added ones."""
  db = firestore.Client()
  collection_ref = db.collection("charades_words")
  word_refs = collection_ref.stream()
  word_refs = list(word_refs)

  if not len(word_refs):
    return "No more words left :("

  random_word_ref = random.choice(word_refs)
  random_word = random_word_ref.id
  # Delete the chosen word so it doesn't get drawn again.
  collection_ref.document(random_word).delete()
  return random_word

@app.route('/')
def main():
  if 'add_word' in request.values:
    add_word(request.values['add_word'])

  random_word = ""
  if 'get_random_word' in request.values:
    random_word = get_random_word()

  return render_template('charades.html',
                         random_word  = random_word)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
