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
        "msg": "Content harvesting service"
    })

@app.route("/harvest", methods=['POST'])
def harvest_content():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({
                'error': 'Missing URL in request body'
            }), 400

        url = data['url']
        result = harvester.harvest(url=url)

        return jsonify({
            'id': result.id,
            'url': result.url,
            'resolved_url': result.resolved_url,
            'content_type': result.content_type,
            'code': result.code,
            'created_date': result.created_date
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)