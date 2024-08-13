from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# Mock database
items = []

@app.route('/items', methods=['POST'])
def create_item():
    if not request.json or 'name' not in request.json:
        abort(400)  # Bad request
    item = {
        'id': len(items) + 1,
        'name': request.json['name']
    }
    items.append(item)
    return jsonify({'item': item}), 201


@app.route('/items', methods=['GET'])
def get_items():
    return jsonify({'items': items})

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if item is None:
        abort(404)  # Not found
    return jsonify({'item': item})

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if item is None:
        abort(404)
    if not request.json or 'name' not in request.json:
        abort(400)
    item['name'] = request.json['name']
    return jsonify({'item': item})

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if item is None:
        abort(404)
    items.remove(item)
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True)
