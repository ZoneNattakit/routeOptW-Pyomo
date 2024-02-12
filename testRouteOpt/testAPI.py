from flask import Flask, render_template, request
import datetime
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_input', methods=['POST'])
def process_input():
    num_customers = int(request.form['num_customers'])
    num_vehicles = int(request.form['num_vehicles'])
    num_goods = int(request.form['num_goods'])

    time_windows = {}
    for i in range(1, num_customers + 1):
        start_hour = int(request.form[f'start_hour_{i}'])
        start_minute = int(request.form[f'start_minute_{i}'])
        end_hour = int(request.form[f'end_hour_{i}'])
        end_minute = int(request.form[f'end_minute_{i}'])

        time_windows[i] = {
            'customer_ID': i,
            'start': {'hour': start_hour, 'minute': start_minute},
            'end': {'hour': end_hour, 'minute': end_minute}
        }

    input_data = {
        "num_customers": num_customers,
        "num_vehicles": num_vehicles,
        "num_goods": num_goods,
        "time_for_sent": time_windows
    }

    with open('customersAPI.log', 'a') as json_file:
        json.dump(input_data, json_file)
        json_file.write('\n')

    return "Data processed successfully!"

if __name__ == '__main__':
    app.run(debug=True)
