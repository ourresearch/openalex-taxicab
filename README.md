## OpenAlex Taxicab


### Example usage:

```python
import os

import boto3
from openalex_http import http_cache
from openalex_taxicab.harvest import Harvester


s3_client = boto3.client("s3")
http_cache.initialize({
    "CRAWLERA_KEY": os.getenv("CRAWLERA_KEY"),
    "STATIC_IP_PROXY": os.getenv("STATIC_IP_PROXY"),
    "ZYTE_API_KEY": os.getenv("ZYTE_API_KEY"),
})

if __name__ == "__main__":
    h = Harvester(s3=s3_client)
    result = h.harvest(url="https://doi.org/example_doi")
    print(result.to_dict())
```
