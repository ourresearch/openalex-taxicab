## OpenAlex Taxicab


### Example usage:

```python
import boto3
from openalex_taxicab.harvest import Harvester


s3_client = boto3.client("s3")

if __name__ == "__main__":
    h = Harvester(s3=s3_client)
    result = h.harvest(url="https://doi.org/example_doi")
    print(result.to_dict())
```
