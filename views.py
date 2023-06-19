from flask import Blueprint, render_template, request, jsonify, url_for
from calculate import results, pr, de, sa, asset, team_results, kpi_present

views = Blueprint(__name__, "views")

@views.route("/")
def home():
    return render_template("index.html")

@views.route('score')
def score():
    return render_template("score_team.html", results=team_results, development=de, production=pr, sales=sa, asset=asset)

@views.route('round')
def round_circu():
    return render_template("score_round.html", kpi_present=kpi_present)

@views.route('goals')
def learning():
    return render_template('goals.html')
