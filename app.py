import gzip
import os

from flask import Flask, request, jsonify, Response
import boto3

from openalex_taxicab.harvest import Harvester
from openalex_taxicab.http_cache import http_get
from openalex_taxicab.util import guess_mime_type

app = Flask(__name__)
app.json.sort_keys = False

r2_account_id = os.environ.get('R2_ACCOUNT_ID')
r2_access_key = os.environ.get('R2_ACCESS_KEY_ID')
r2_secret_key = os.environ.get('R2_SECRET_ACCESS_KEY')

if not all([r2_account_id, r2_access_key, r2_secret_key]):
    raise ValueError("R2 credentials not configured. Set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, and R2_SECRET_ACCESS_KEY environment variables.")

s3_client = boto3.client(
    's3',
    endpoint_url=f'https://{r2_account_id}.r2.cloudflarestorage.com',
    aws_access_key_id=r2_access_key,
    aws_secret_access_key=r2_secret_key,
    region_name='auto'  # R2 uses 'auto' as region
)
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

@app.route("/test-zyte", methods=['GET'])
def test_zyte():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    try:
        response = http_get(url)
        return jsonify({
            "status_code": response.status_code,
            "resolved_url": response.url,
            "content_preview": response.content[:5000],
            "content_type":guess_mime_type(response.content),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/taxicab/doi/<path:doi>", methods=['GET'])
def fetch_harvested_content_by_doi(doi):
    doi = str(doi)
    result = harvester.fetch_by_doi(doi)
    return jsonify(result)

@app.route("/taxicab/pmh/<path:pmh_id>", methods=['GET'])
def fetch_harvested_content_by_pmh_id(pmh_id):
    pmh_id = str(pmh_id)
    result = harvester.fetch_by_pmh_id(pmh_id)
    return jsonify(result)

@app.route("/taxicab/<uuid:harvest_id>", methods=['GET'])
def fetch_harvested_content(harvest_id):
    harvest_id = str(harvest_id)
    possible_buckets = [harvester.HTML_BUCKET, harvester.PDF_BUCKET, harvester.XML_BUCKET]

    for bucket in possible_buckets:
        s3_key_html = f"{harvest_id}.html.gz"
        s3_key_pdf = f"{harvest_id}.pdf"
        s3_key_xml = f"{harvest_id}.xml.gz"

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

        try:
            # try XML (gzipped)
            print(f"Trying to fetch XML from {bucket}/{s3_key_xml}")
            obj = s3_client.get_object(Bucket=bucket, Key=s3_key_xml)
            content = gzip.decompress(obj['Body'].read())
            content_type = "application/xml"
            return Response(
                content,
                content_type=content_type,
                headers={"Content-Disposition": f"attachment; filename={harvest_id}.xml"}
            )
        except s3_client.exceptions.NoSuchKey:
            pass  # if XML is not found, try the next bucket
        except Exception as e:
            return jsonify({"error": f"Error fetching XML: {str(e)}"}), 500

    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)