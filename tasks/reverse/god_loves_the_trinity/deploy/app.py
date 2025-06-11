from flask import Flask, render_template_string, request, send_file
from datetime import datetime
import os
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Свято-Троицкая Канцелярия</title>
    <style>
        body {
            font-family: 'Times New Roman', Georgia, serif;
            max-width: 700px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f0e6;
            color: #3a2c0a;
            background-image: 
                linear-gradient(rgba(210, 180, 140, 0.2) 1px, transparent 1px),
                linear-gradient(90deg, rgba(210, 180, 140, 0.2) 1px, transparent 1px);
            background-size: 20px 20px;
        }
        .container {
            background: #fff8f0;
            padding: 30px;
            border: 3px double #5e2d15;
            box-shadow: 0 0 10px rgba(94, 45, 21, 0.2);
            position: relative;
            overflow: hidden;
        }
        .container:before {
            content: "";
            position: absolute;
            top: 0;
            right: 0;
            width: 100px;
            height: 100px;
            background: 
                linear-gradient(45deg, transparent 45%, #5e2d15 45%, #5e2d15 55%, transparent 55%),
                linear-gradient(-45deg, transparent 45%, #5e2d15 45%, #5e2d15 55%, transparent 55%);
            background-size: 20px 20px;
            opacity: 0.1;
        }
        h1 {
            color: #5e2d15;
            text-align: center;
            font-size: 2em;
            margin-bottom: 25px;
            letter-spacing: 1px;
            font-weight: normal;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.1);
            position: relative;
        }
        h1:after {
            content: "✠";
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.5em;
            opacity: 0.3;
        }
        label {
            display: block;
            margin-top: 20px;
            font-weight: bold;
            color: #5e2d15;
            font-size: 1em;
            position: relative;
            padding-left: 25px;
        }
        label:before {
            content: "⋮";
            position: absolute;
            left: 0;
            top: 0;
            color: #8b4513;
        }
        input {
            width: 100%;
            padding: 10px;
            margin: 8px 0 20px;
            border: 1px solid #a67c52;
            background: rgba(255, 255, 255, 0.7);
            font-size: 1em;
            box-shadow: inset 2px 2px 3px rgba(0,0,0,0.1);
            font-family: inherit;
        }
        button {
            background: linear-gradient(to bottom, #8b4513, #5e2d15);
            color: #f8f1e0;
            padding: 12px;
            border: none;
            cursor: pointer;
            font-size: 1.1em;
            width: 100%;
            margin-top: 20px;
            letter-spacing: 1px;
            text-transform: uppercase;
            position: relative;
            overflow: hidden;
            transition: all 0.3s;
        }
        button:hover {
            background: linear-gradient(to bottom, #a0522d, #6b3e1a);
        }
        button:after {
            content: "☦";
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            opacity: 0.5;
        }
        .result {
            margin-top: 25px;
            padding: 15px;
            border-left: 4px solid;
            font-size: 1.1em;
            line-height: 1.5;
            background: rgba(255, 255, 255, 0.7);
        }
        .success {
            border-color: #2e8b57;
            color: #1f5c3a;
        }
        .error {
            border-color: #c62828;
            color: #8e1c1c;
        }
        .form-header {
            text-align: center;
            margin-bottom: 30px;
            font-style: italic;
            color: #5e2d15;
            position: relative;
        }
        .form-header:before,
        .form-header:after {
            content: "✝";
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            opacity: 0.3;
        }
        .form-header:before {
            left: 10px;
        }
        .form-header:after {
            right: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Молитвенный сундук Петра 1</h1>
        <div class="form-header">
            Во имя Отца, и Сына, и Святаго Духа
        </div>
        
        <form method="POST">
            <label for="master_name">Символ веры:</label>
            <input type="text" id="master_name" name="master_name" required placeholder="Первое таинство">
            
            <label for="ship_name">Царская воля:</label>
            <input type="text" id="ship_name" name="ship_name" required placeholder="Второе таинство">
            
            <label for="permit">Дух преобразований:</label>
            <input type="text" id="permit" name="permit" required placeholder="Третье таинство">
            
            <button type="submit">Испросить благословение</button>
        </form>
        
        {% if message %}
            <div class="result {{ message_class }}">{{ message|safe }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

MAX_LEN = 64

def func_l0(c, i): return c ^ (i * 3)
def func_l1(c, i): return (c + i) & 0xFF

def func_l2(c, i): return (c << 1) ^ i
def func_l3(c, i): return (c - i * 2) & 0xFF

def func_l4(c, i): return (c ^ 0x55) + i
def func_l5(c, i): return (c + 13) ^ (i * 4)

def func_p0(c, i): return (c ^ 0x33) + (i * 2)
def func_p1(c, i): return (c - i) ^ 0x77

def func_p2(c, i): return (c * 2) + i
def func_p3(c, i): return (c ^ (i * 5)) & 0xFF

def func_p4(c, i): return ((c + i * 3) ^ 0xAA)
def func_p5(c, i): return ((c ^ 0x11) + (i << 1))

login_mod_funcs = [
    [func_l0, func_l1],
    [func_l2, func_l3],
    [func_l4, func_l5],
    [func_l0, func_l2],
    [func_l1, func_l3],
    [func_l4, func_l0]
]

pass_mod_funcs = [
    [func_p0, func_l1],
    [func_l2, func_p3],
    [func_p4, func_l5],
    [func_p0, func_l2],
    [func_l1, func_p3],
    [func_p4, func_l0]
]

def modkey_index(i):
    return i % 3

def modulate(input_str, modkey, funcs):
    out = [0] * 6
    for i in range(6):
        bit_index = modkey_index(i)
        bit = 1 if modkey[bit_index] == '1' else 0
        c = ord(input_str[i]) if i < len(input_str) else 0
        out[i] = funcs[i][bit](c, i)
    return out

def check_match(a, b):
    delta = 0
    for ai, bi in zip(a, b):
        delta |= ai ^ bi
    return delta == 0


@app.route('/', methods=['GET', 'POST'])
def keygen():
    message = ""
    message_class = ""
    
    if request.method == 'POST':
        master_name = request.form.get('master_name', '').strip()
        ship_name = request.form.get('ship_name', '').strip()
        permit = request.form.get('permit', '').strip().upper()
        
        if not master_name or not ship_name or not permit:
            message = "Все поля должны быть заполнены!"
            message_class = "error"
        else:
            if modulate(master_name, permit, login_mod_funcs) == modulate(ship_name, permit, pass_mod_funcs):
                if os.path.exists("peter_greet.jpg"):
                    return send_file(
                        "peter_greet.jpg",
                        mimetype='image/jpg',
                        as_attachment=True,
                        download_name=f"peter_greet.jpg"
                    )
                else:
                    message = "Царская печать утеряна!"
                    message_class = "error"
            else:
                message = "Удйи отсюда, окаянный!"
                message_class = "error"


    return render_template_string(HTML_TEMPLATE, message=message, message_class=message_class)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)