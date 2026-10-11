
from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Python Dictionary App</title>
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
            color: #2563eb;
        }

        .container {
            max-width: 650px;
            margin: 25px auto;
            background: white;
            padding: 25px;
            border-radius: 14px;
            box-shadow: 0 5px 18px #00000012;
        }

        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0 15px;
            border: 1px solid #cbd5e1;
            border-radius: 7px;
            box-sizing: border-box;
        }

        button {
            width: 100%;
            padding: 12px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 7px;
            cursor: pointer;
        }

        .result {
            margin-top: 20px;
            padding: 18px;
            background: #eff6ff;
            border-left: 5px solid #2563eb;
            border-radius: 8px;
        }

        .pipeline {
            text-align: center;
            background: #f1f5f9;
            padding: 15px;
            line-height: 2;
            border-radius: 8px;
        }

        .error {
            color: #b91c1c;
            margin-top: 15px;
        }
    </style>
</head>

<body>
    <h1>Python Dictionary App</h1>

    <div class="container">
        <div class="pipeline">
            <b>Pipeline</b><br>
            Search Word → Validate → Fetch Meaning → Display Results
        </div>

        <form method="POST">
            <label>Enter an English word</label>
            <input type="text" name="word"
                   value="{{ word }}"
                   placeholder="Example: beautiful" required>
            <button type="submit">Search Meaning</button>
        </form>

        {% if meanings %}
        <div class="result">
            <h2>{{ meanings["word"] }}</h2>

            {% if meanings["phonetic"] %}
                <p>Pronunciation: {{ meanings["phonetic"] }}</p>
            {% endif %}

            {% for meaning_group in meanings["definitions"] %}
                <h3>{{ meaning_group["part"] }}</h3>

                <ol>
                    {% for definition in meaning_group["definitions"] %}
                        <li>
                            {{ definition["meaning"] }}

                            {% if definition["example"] %}
                                <br>
                                <i>Example: {{ definition["example"] }}</i>
                            {% endif %}
                        </li>
                    {% endfor %}
                </ol>
            {% endfor %}
        </div>
        {% endif %}

        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
"""


def get_meanings(word):
    url = (
        "https://api.dictionaryapi.dev/api/v2/entries/en/"
        + requests.utils.quote(word)
    )

    response = requests.get(url, timeout=10)

    if response.status_code == 404:
        return None

    response.raise_for_status()
    data = response.json()

    if not isinstance(data, list) or not data:
        return None

    entry = data[0]

    result = {
        "word": entry.get("word", word),
        "phonetic": entry.get("phonetic", ""),
        "definitions": []
    }

    for meaning in entry.get("meanings", []):
        group = {
            "part": meaning.get("partOfSpeech", "Meaning"),
            "definitions": []
        }

        for definition in meaning.get("definitions", []):
            group["definitions"].append({
                "meaning": definition.get(
                    "definition", "Meaning unavailable"
                ),
                "example": definition.get("example", "")
            })

        if group["definitions"]:
            result["definitions"].append(group)

    return result


@app.route("/", methods=["GET", "POST"])
def home():
    word = ""
    meanings = None
    error = ""

    if request.method == "POST":
        word = request.form.get("word", "").strip()

        if not word:
            error = "Please enter a word."

        elif len(word) > 80:
            error = "Please enter a shorter word."

        else:
            try:
                meanings = get_meanings(word)

                if meanings is None:
                    error = "Word not found. Check the spelling."

            except requests.Timeout:
                error = "Request timed out. Please try again."

            except requests.RequestException:
                error = "Internet connection error. Please try again."

            except (ValueError, TypeError, KeyError, IndexError):
                error = "Unable to process the dictionary result."

    return render_template_string(
        HTML,
        word=word,
        meanings=meanings,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)