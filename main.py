# -*- coding: utf-8 -*-
import json
import serverstats
from flask_frozen import Freezer
from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")
def index():
    characterdata = serverstats.get_powerscore_ranking(3, 606)
    date = '2022-11-11'
    characternames = []
    powerscore_history = []
    for char in characterdata:
        characternames.append(char.name)
        powerscore_history.append(serverstats.get_powerscore_history(char.name))

    return render_template("ranking.html", characternames=characternames, powerscore_history=powerscore_history)


if __name__ == '__main__':
    serverstats.get_powerscore_ranking(3, 606)  # baixar o ranking diário
    freezer = Freezer(app)
    freezer.freeze()
    #app.run(host='localhost', port=5000, debug=True)
