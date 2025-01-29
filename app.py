from flask import Flask, request, jsonify
import boto3
from openalex_taxicab.harvest import Harvester

app = Flask(__name__)

s3_client = boto3.client("s3", region_name="us-east-1")
harvester = Harvester(s3=s3_client)

@app.route("/")
def index():
    return jsonify(
        {
            "version": "0.1",
            "msg": "Don't panic",
        }
    )


@app.route("/harvest", methods=['POST'])
def harvest_doi():
    try:
        # Get DOI from POST request
        data = request.get_json()

        if not data or 'doi' not in data:
            return jsonify({
                'error': 'Missing DOI in request body'
            }), 400

        doi = data['doi']

        if not doi.startswith('https://doi.org/'):
            doi = f'https://doi.org/{doi}'

        result = harvester.harvest(url=doi)

        result_dict = result.to_dict()
        result_dict.pop("content", None)

        return jsonify(result_dict)

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
