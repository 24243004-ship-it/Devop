
from flask import Flask, request, render_template_string
from datetime import datetime, date

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Python Calendar Picker</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: #eef2ff;
            color: #1e293b;
            margin: 0;
            padding: 25px;
        }

        h1 {
            text-align: center;
            color: #4338ca;
        }

        .pipeline {
            max-width: 750px;
            margin: 20px auto;
            padding: 16px;
            background: #e0e7ff;
            border-radius: 10px;
            text-align: center;
            line-height: 2;
        }

        .card {
            max-width: 450px;
            margin: 25px auto;
            padding: 28px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 20px #00000012;
        }

        label {
            display: block;
            margin: 15px 0 8px;
            font-weight: bold;
        }

        input[type="date"] {
            width: 100%;
            padding: 13px;
            font-size: 16px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
        }

        button {
            width: 100%;
            padding: 13px;
            margin-top: 18px;
            border: none;
            border-radius: 8px;
            background: #4f46e5;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }

        button:hover {
            background: #3730a3;
        }

        .result {
            margin-top: 22px;
            padding: 18px;
            background: #dcfce7;
            border-left: 5px solid #16a34a;
            border-radius: 8px;
            overflow-wrap: anywhere;
        }

        .error {
            margin-top: 20px;
            padding: 13px;
            color: #991b1b;
            background: #fee2e2;
            border-radius: 8px;
        }

        .calendar-icon {
            font-size: 42px;
            text-align: center;
        }

        .hint {
            color: #64748b;
            font-size: 13px;
        }
    </style>
</head>

<body>
    <h1>Calendar Picker App</h1>

    <div class="pipeline">
        <b>CALENDAR PIPELINE</b><br>
        Open Calendar → Select Date → Validate Date
        → Display Selected Date
    </div>

    <div class="card">
        <div class="calendar-icon">📅</div>
        <h2>Select a Date</h2>

        <form method="POST">
            <label for="selected_date">Choose your date</label>

            <input
                type="date"
                id="selected_date"
                name="selected_date"
                value="{{ selected_date }}"
                required
            >

            <p class="hint">
                Select a date using your browser's calendar picker.
            </p>

            <button type="submit">Display Date</button>
        </form>

        {% if display_date %}
            <div class="result">
                <h3>Selected Date</h3>
                <p><b>{{ display_date }}</b></p>
                <p>Day: {{ day_name }}</p>
                <p>Month: {{ month_name }}</p>
                <p>Year: {{ year }}</p>
            </div>
        {% endif %}

        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    selected_date = date.today().isoformat()
    display_date = ""
    day_name = ""
    month_name = ""
    year = ""
    error = ""

    if request.method == "POST":
        selected_date = request.form.get("selected_date", "").strip()

        if not selected_date:
            error = "Please select a date."

        else:
            try:
                parsed_date = datetime.strptime(
                    selected_date, "%Y-%m-%d"
                ).date()

                # Reject dates that are not in the exact expected format.
                if parsed_date.isoformat() != selected_date:
                    raise ValueError("Invalid date format")

                display_date = parsed_date.strftime("%d %B %Y")
                day_name = parsed_date.strftime("%A")
                month_name = parsed_date.strftime("%B")
                year = parsed_date.year

            except ValueError:
                error = "Invalid date. Please select a valid date."
                selected_date = ""

    return render_template_string(
        HTML,
        selected_date=selected_date,
        display_date=display_date,
        day_name=day_name,
        month_name=month_name,
        year=year,
        error=error
    )


if __name__ == "__main__":
    print("Calendar Picker App started successfully!")
    print("Open http://127.0.0.1:5000 in your browser.")
    app.run(debug=False)
