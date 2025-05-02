## OpenAlex Taxicab


REST API to store harvested data in S3.

### Development

Create an .env file with the zyte API key and S3 credentials. Then run:

```bash
docker compose up
```

Test zyte with: http://0.0.0.0:8080/test-zyte?url=https://doi.org/10.1016/j.aftran.2024.100020

### Deploy

Simply commit changes and push to github. The app will be automatically deployed to AWS using Github Actions.