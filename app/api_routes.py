from flask import Blueprint, jsonify

api = Blueprint('api', __name__)

tours = [
    {"id": 1, "title": "Тур 1", "price": 1200.0},
    {"id": 2, "title": "Тур 2", "price": 1050.0},
]

@api.route('/tours', methods=['GET'])
def get_tours():
    return jsonify({"tours": tours})

@api.route('/tours/<int:tour_id>', methods=['GET'])
def get_tour(tour_id):
    tour = next((tour for tour in tours if tour["id"] == tour_id), None)
    if tour:
        return jsonify({"tour": tour})
    else:
        return jsonify({"error": "Тур не найден"}), 404