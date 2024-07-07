from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def render_board_html(cell_states: List[List[CellState]]):
    html = "<table>"
    for i, row in enumerate(cell_states):
        html += "<tr>"
        for j, cell in enumerate(row):
            # TODO - replace with actual HTML
            html += f'<td><form method="post" action="/move">'
            html += f'<input type="hidden" name="row" value="{i}">'
            html += f'<input type="hidden" name="col" value="{j}">'
            html += f'<input type="submit" value="{cell or " "}">'
            html += '</form></td>'
        html += "</tr>"
    html += "</table>"
    return html

@app.route('/')
def index():
    board_state = game.get_board_state()
    board_html = render_board_html(board_state.cell_states)
    return render_template('index.html', board=board_html)

@app.route('/move', methods=['POST'])
def move():
    row = int(request.form['row'])
    col = int(request.form['col'])
    game.make_move(row, col)  # Assuming this method exists in your GameOrchestrator
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
    