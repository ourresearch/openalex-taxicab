## OpenAlex Taxicab


### Example usage:

Set environment variables:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `CRAWLERA_KEY`
- `STATIC_IP_PROXY`
- `ZYTE_API_KEY`

Run with python

```python
import boto3
from openalex_taxicab.harvest import Harvester

s3_client = boto3.client("s3")

h = Harvester(s3=s3_client)
result = h.harvest(url="https://doi.org/example_doi")
print(result.to_dict())
```
