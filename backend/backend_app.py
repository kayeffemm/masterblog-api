from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Retrieve all posts with optional sorting.
    Read query parameters and validate sort field parameter and sort direction.
    If both are valid sort posts based on given parameters and return posts as JSON + status code 200
    :return: POSTS list as JSON
    """
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction', 'asc').lower()

    valid_sort_fields = ['title', 'content']
    if sort_field and sort_field not in valid_sort_fields:
        return jsonify({"error": f"Invalid sort field. Valid fields are: {valid_sort_fields}"}), 400

    if sort_direction not in ['asc', 'desc']:
        return jsonify({"error": "Invalid sort direction. Valid directions are: 'asc', 'desc'"}), 400

    sorted_posts = POSTS
    if sort_field:
        reverse = sort_direction == 'desc'
        sorted_posts = sorted(POSTS, key=lambda post: post[sort_field].lower(), reverse=reverse)

    return jsonify(sorted_posts), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search for posts by title or content.
    Read the query parameters and search for matches in POST list.
    If no matches are found, return empty list.
    If no query parameters are set return all posts.
    :return: All matching posts as JSON + status code 200
    """
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    matching_posts = [
        post for post in POSTS
        if (title_query in post["title"].lower() if title_query else True) and
           (content_query in post["content"].lower() if content_query else True)
    ]

    return jsonify(matching_posts), 200


@app.route('/api/posts', methods=['POST'])
def add_post():
    """
    Add a new post.
    Gets data from POST request, checks if any field is missing.
    If no field is missing create a new ID and the new Post.
    Then adds the new post to our POSTS list and returns the new post with status code 201
    :return: New Post + Status code 201
    """
    data = request.json

    missing_fields = [field for field in ("title", "content") if field not in data or not data[field]]
    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing_fields
        }), 400

    new_id = POSTS[-1]["id"] + 1 if POSTS else 1

    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"]
    }

    POSTS.append(new_post)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id: int):
    """
    Delete a post by post id.
    :param post_id: post ID as Integer
    :return: Error or Success message with status code
    """
    global POSTS

    post = next((post for post in POSTS if post['id'] == post_id), None)

    if post is None:
        return jsonify({'error': f"Post with id {post_id} not found."}), 404

    POSTS = [post for post in POSTS if post['id'] != post_id]

    return jsonify({'message': f"Post with id {post_id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Update an existing post.
    Parse the JSON data from the request, find the post with the given ID.
    If post is not found return error code 404.
    if post is present update its content with given JSON data and return updated post + status code 200
    :param post_id: post ID as Integer
    :return: Error or Success message with status code
    """
    data = request.json

    post = next((post for post in POSTS if post["id"] == post_id), None)

    if post is None:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    post["title"] = data.get("title", post["title"])
    post["content"] = data.get("content", post["content"])

    return jsonify(post), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
