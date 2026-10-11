
from flask import Flask, request, render_template_string
import requests
import os

app = Flask(__name__)

OMDB_API_KEY = os.getenv("OMDB_API_KEY", "")

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>BMI Calculator & Movie Search</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            margin: 0;
            padding: 25px;
            color: #1e293b;
        }

        h1 {
            text-align: center;
            color: #1d4ed8;
        }

        .container {
            display: flex;
            flex-wrap: wrap;
            gap: 25px;
            justify-content: center;
        }

        .card {
            background: white;
            padding: 25px;
            border-radius: 14px;
            width: 380px;
            max-width: 100%;
            box-sizing: border-box;
            box-shadow: 0 5px 18px #00000012;
        }

        h2 {
            color: #2563eb;
        }

        input {
            width: 100%;
            padding: 12px;
            margin: 8px 0 15px;
            border: 1px solid #cbd5e1;
            border-radius: 7px;
            box-sizing: border-box;
        }

        button {
            width: 100%;
            background: #2563eb;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 7px;
            cursor: pointer;
            font-size: 16px;
        }

        button:hover {
            background: #1d4ed8;
        }

        .result {
            background: #eff6ff;
            padding: 15px;
            margin-top: 18px;
            border-radius: 8px;
            overflow-wrap: anywhere;
        }

        .movie-poster {
            width: 150px;
            max-width: 100%;
            border-radius: 8px;
        }

        .pipeline {
            text-align: center;
            background: white;
            margin: 25px auto;
            padding: 15px;
            max-width: 800px;
            border-radius: 10px;
            line-height: 2;
        }

        .note {
            color: #64748b;
            font-size: 13px;
        }
    </style>
</head>

<body>
    <h1>BMI Calculator & Movie Search</h1>

    <div class="pipeline">
        <b>PROJECT PIPELINE</b><br>
        User Input → Validation → Processing → Result Display
    </div>

    <div class="container">

        <div class="card">
            <h2>BMI Calculator</h2>

            <form method="POST" action="/bmi">
                <label>Weight (kg)</label>
                <input type="number" name="weight"
                       step="any" min="0.1" max="500"
                       placeholder="Example: 65" required>

                <label>Height (cm)</label>
                <input type="number" name="height"
                       step="any" min="30" max="300"
                       placeholder="Example: 170" required>

                <button type="submit">Calculate BMI</button>
            </form>

            {% if bmi is not none %}
            <div class="result">
                <h3>BMI: {{ bmi }}</h3>
                <p>Category: <b>{{ category }}</b></p>
            </div>
            {% endif %}

            {% if bmi_error %}
            <div class="result">{{ bmi_error }}</div>
            {% endif %}

            <p class="note">
                Adult BMI categories are general screening guidelines,
                not a medical diagnosis.
            </p>
        </div>

        <div class="card">
            <h2>Online Movie Search</h2>

            <form method="POST" action="/movie">
                <label>Movie Name</label>
                <input type="text" name="movie"
                       placeholder="Example: Interstellar" required>

                <button type="submit">Search Movie</button>
            </form>

            {% if movie %}
            <div class="result">
                <h3>{{ movie.Title }} ({{ movie.Year }})</h3>

                {% if movie.Poster and movie.Poster != "N/A" %}
                <img class="movie-poster"
                     src="{{ movie.Poster }}" alt="Movie poster">
                {% endif %}

                <p><b>Genre:</b> {{ movie.Genre }}</p>
                <p><b>Director:</b> {{ movie.Director }}</p>
                <p><b>Actors:</b> {{ movie.Actors }}</p>
                <p><b>IMDb Rating:</b> {{ movie.imdbRating }}</p>
                <p><b>Plot:</b> {{ movie.Plot }}</p>
            </div>
            {% endif %}

            {% if movie_error %}
            <div class="result">{{ movie_error }}</div>
            {% endif %}

            {% if not api_configured %}
            <p class="note">
                Movie search needs an OMDb API key.
                Configure OMDB_API_KEY before searching.
            </p>
            {% endif %}
        </div>

    </div>
</body>
</html>
"""


def page(bmi=None, category=None, bmi_error=None,
         movie=None, movie_error=None):
    return render_template_string(
        HTML,
        bmi=bmi,
        category=category,
        bmi_error=bmi_error,
        movie=movie,
        movie_error=movie_error,
        api_configured=bool(OMDB_API_KEY)
    )


@app.route("/")
def home():
    return page()


@app.route("/bmi", methods=["POST"])
def calculate_bmi():
    try:
        weight = float(request.form.get("weight", ""))
        height = float(request.form.get("height", ""))

        if not (0.1 <= weight <= 500):
            return page(bmi_error="Enter a valid weight between 0.1 and 500 kg.")

        if not (30 <= height <= 300):
            return page(bmi_error="Enter a valid height between 30 and 300 cm.")

        height_m = height / 100
        bmi_value = weight / (height_m ** 2)
        bmi_value = round(bmi_value, 2)

        if bmi_value < 18.5:
            category = "Underweight"
        elif bmi_value < 25:
            category = "Normal weight"
        elif bmi_value < 30:
            category = "Overweight"
        else:
            category = "Obesity range"

        return page(bmi=bmi_value, category=category)

    except (ValueError, TypeError):
        return page(bmi_error="Please enter valid numeric values.")


@app.route("/movie", methods=["POST"])
def search_movie():
    movie_name = request.form.get("movie", "").strip()

    if not movie_name:
        return page(movie_error="Please enter a movie name.")

    if not OMDB_API_KEY:
        return page(
            movie_error="API key missing. Set the OMDB_API_KEY environment variable."
        )

    try:
        response = requests.get(
            "https://www.omdbapi.com/",
            params={
                "apikey": OMDB_API_KEY,
                "t": movie_name,
                "plot": "full"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "True":
            return page(movie=data)

        return page(
            movie_error=data.get("Error", "Movie not found.")
        )

    except requests.RequestException:
        return page(
            movie_error="Could not connect to the movie service. Check your internet."
        )


if __name__ == "__main__":
    print("BMI Calculator and Movie Search is starting...")
    print("Open http://127.0.0.1:5000 in your browser.")
    app.run(debug=True)