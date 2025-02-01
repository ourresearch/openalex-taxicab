from flask import Flask, request, jsonify
import boto3

from openalex_taxicab.harvest import Harvester

app = Flask(__name__)

s3_client = boto3.client("s3", region_name="us-east-1")
harvester = Harvester(s3=s3_client)

@app.route("/")
def index():
    return jsonify({
        "version": "0.1",
        "msg": "Content harvesting service is running"
    })


@app.route("/harvest", methods=['POST'])
def harvest_content():
    data = request.get_json()

    # Check for required fields
    required_fields = ['native_id', 'native_id_namespace', 'url']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({
            'error': f'Missing required fields in request body: {", ".join(missing_fields)}'
        }), 400

    # fetch content
    result = harvester.harvest(
        url=data['url'],
        native_id=data['native_id'],
        native_id_namespace=data['native_id_namespace']
    )

    # return response without the content field
    return jsonify({
        'id': result['id'],
        'url': result['url'],
        'resolved_url': result['resolved_url'],
        'content_type': result['content_type'],
        'code': result['code'],
        'created_date': result['created_date'],
        'is_soft_block': result['is_soft_block'],
        'native_id': result['native_id'],
        'native_id_namespace': result['native_id_namespace']
    })

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=8080, debug=True)