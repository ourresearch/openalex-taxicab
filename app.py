import gzip

from flask import Flask, request, jsonify, Response
import boto3

from openalex_taxicab.harvest import Harvester

app = Flask(__name__)
app.json.sort_keys = False

s3_client = boto3.client("s3", region_name="us-east-1")
harvester = Harvester(s3=s3_client)

@app.route("/")
def index():
    metadata = harvester.metadata()
    return jsonify(metadata)


@app.route("/taxicab", methods=['POST'])
def harvest_content():
    data = request.get_json()

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

    status_code = 201 if result['id'] else 200
    return jsonify(result), status_code


@app.route("/taxicab/<uuid:harvest_id>", methods=['GET'])
def fetch_harvested_content(harvest_id):
    harvest_id = str(harvest_id)
    possible_buckets = [harvester.HTML_BUCKET, harvester.PDF_BUCKET]

    for bucket in possible_buckets:
        s3_key_html = f"{harvest_id}.html.gz"
        s3_key_pdf = f"{harvest_id}.pdf"

        try:
            # try HTML (gzipped)
            obj = s3_client.get_object(Bucket=bucket, Key=s3_key_html)
            content = gzip.decompress(obj['Body'].read())
            content_type = "text/html"
            return Response(
                content,
                content_type=content_type,
                headers={"Content-Disposition": f"inline; filename={harvest_id}.html"}
            )

        except s3_client.exceptions.NoSuchKey:
            pass  # continue to check for PDF
        except Exception as e:
            return jsonify({"error": f"Error fetching HTML: {str(e)}"}), 500

        try:
            # try PDF
            obj = s3_client.get_object(Bucket=bucket, Key=s3_key_pdf)
            content = obj['Body'].read()
            content_type = "application/pdf"
            return Response(
                content,
                content_type=content_type,
                headers={"Content-Disposition": f"attachment; filename={harvest_id}.pdf"}
            )

        except s3_client.exceptions.NoSuchKey:
            pass  # if PDF is not found, try the next bucket
        except Exception as e:
            return jsonify({"error": f"Error fetching PDF: {str(e)}"}), 500

    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)