
from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

API_URL = "https://www.themealdb.com/api/json/v1/1/search.php"

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Recipe Finder</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 25px;
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            color: #1e293b;
        }

        h1 {
            text-align: center;
            color: #15803d;
        }

        .container {
            max-width: 1000px;
            margin: auto;
        }

        .search-box {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px #00000010;
        }

        .pipeline {
            background: #dcfce7;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            line-height: 2;
            margin-bottom: 20px;
        }

        input {
            width: 100%;
            padding: 13px;
            border: 1px solid #cbd5e1;
            border-radius: 7px;
            margin: 10px 0;
            font-size: 16px;
        }

        button {
            width: 100%;
            padding: 13px;
            background: #15803d;
            color: white;
            border: none;
            border-radius: 7px;
            cursor: pointer;
            font-size: 16px;
        }

        button:hover {
            background: #166534;
        }

        .recipes {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 25px;
        }

        .recipe {
            background: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 15px #00000010;
            overflow-wrap: anywhere;
        }

        .recipe img {
            width: 100%;
            border-radius: 8px;
        }

        .recipe h2 {
            color: #15803d;
        }

        .recipe a {
            color: #15803d;
            font-weight: bold;
        }

        .message {
            background: white;
            padding: 18px;
            margin-top: 20px;
            border-radius: 8px;
        }

        .small {
            color: #64748b;
            font-size: 13px;
        }
    </style>
</head>

<body>
    <div class="container">
        <h1>Recipe Finder</h1>

        <div class="search-box">
            <div class="pipeline">
                <b>RECIPE SEARCH PIPELINE</b><br>
                Enter Ingredient or Dish → Validate Input
                → Fetch Recipes Online → Display Results
            </div>

            <form method="POST">
                <label><b>Search by dish name</b></label>
                <input
                    type="text"
                    name="dish"
                    placeholder="Example: chicken, pasta, curry"
                    value="{{ dish }}"
                    maxlength="100"
                    required
                >
                <button type="submit">Search Recipes</button>
            </form>

            <p class="small">
                Live recipe results require an internet connection.
            </p>
        </div>

        {% if recipes %}
            <h2>Recipe Results ({{ recipes|length }})</h2>

            <div class="recipes">
                {% for recipe in recipes %}
                    <div class="recipe">
                        {% if recipe["image"] %}
                            <img src="{{ recipe['image'] }}"
                                 alt="Recipe image"
                                 loading="lazy">
                        {% endif %}

                        <h2>{{ recipe["name"] }}</h2>

                        <p>
                            <b>Category:</b>
                            {{ recipe["category"] or "Not available" }}
                        </p>

                        <p>
                            <b>Area:</b>
                            {{ recipe["area"] or "Not available" }}
                        </p>

                        <h3>Ingredients</h3>
                        <ul>
                            {% for ingredient in recipe["ingredients"] %}
                                <li>{{ ingredient }}</li>
                            {% endfor %}
                        </ul>

                        <h3>Instructions</h3>
                        <p>{{ recipe["instructions"] }}</p>

                        {% if recipe["video"] %}
                            <p>
                                <a href="{{ recipe['video'] }}"
                                   target="_blank"
                                   rel="noopener noreferrer">
                                   Watch Recipe Video
                                </a>
                            </p>
                        {% endif %}
                    </div>
                {% endfor %}
            </div>
        {% endif %}

        {% if error %}
            <div class="message">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""


def search_recipes(dish):
    response = requests.get(
        API_URL,
        params={"s": dish},
        timeout=15
    )

    response.raise_for_status()
    data = response.json()

    meals = data.get("meals")

    if not isinstance(meals, list):
        return []

    recipes = []

    for meal in meals:
        ingredients = []

        for number in range(1, 21):
            ingredient = meal.get("strIngredient" + str(number))
            measure = meal.get("strMeasure" + str(number))

            if ingredient and ingredient.strip():
                text = ingredient.strip()

                if measure and measure.strip():
                    text = measure.strip() + " " + text

                ingredients.append(text)

        recipes.append({
            "name": meal.get("strMeal") or "Unknown recipe",
            "category": meal.get("strCategory") or "",
            "area": meal.get("strArea") or "",
            "image": meal.get("strMealThumb") or "",
            "ingredients": ingredients,
            "instructions": (
                meal.get("strInstructions")
                or "Instructions are not available."
            ),
            "video": meal.get("strYoutube") or ""
        })

    return recipes


@app.route("/", methods=["GET", "POST"])
def home():
    dish = ""
    recipes = []
    error = ""

    if request.method == "POST":
        dish = request.form.get("dish", "").strip()

        if not dish:
            error = "Please enter a dish name."

        elif len(dish) > 100:
            error = "Please enter a shorter dish name."

        else:
            try:
                recipes = search_recipes(dish)

                if not recipes:
                    error = (
                        "No recipes found. Try chicken, pasta, "
                        "rice, curry, or beef."
                    )

            except requests.Timeout:
                error = "The request timed out. Please try again."

            except requests.RequestException:
                error = (
                    "Unable to connect to the recipe service. "
                    "Check your internet and try again."
                )

            except (ValueError, TypeError, AttributeError):
                error = (
                    "The recipe service returned an unexpected result. "
                    "Please try again."
                )

    return render_template_string(
        HTML,
        dish=dish,
        recipes=recipes,
        error=error
    )


if __name__ == "__main__":
    print("Recipe Finder is starting...")
    print("Open http://127.0.0.1:5000 in your browser.")
    app.run(debug=False)