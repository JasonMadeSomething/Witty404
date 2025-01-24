# Witty404

Witty404 is a serverless application that generates witty 404 error messages for non-existent pages. It uses AWS Lambda for processing, MongoDB Atlas for caching responses, and the OpenAI API for generating clever messages. The application is designed for seamless integration with web applications, providing a humorous touch to standard 404 pages.

---

## Features
- **Dynamic 404 Messages**: Generates witty and context-aware error messages.
- **Serverless Architecture**: Built using AWS Lambda and API Gateway for scalability and cost efficiency.
- **Caching with MongoDB Atlas**: Caches responses to minimize API calls and reduce latency.
- **OpenAI Integration**: Leverages GPT models to craft creative and engaging error messages.
- **Configurable API Key**: Protects access to the API using AWS API Gateway's API Key feature.

---

## Architecture
- **Frontend**: Any web app or client can call the Witty404 API to fetch a witty error message for a specific URL.
- **Backend**: Python-based AWS Lambda function.
- **Database**: MongoDB Atlas for caching responses.
- **Cloud Services**:
  - AWS Lambda: Runs the core logic.
  - API Gateway: Handles API requests.
  - SSM Parameter Store: Securely stores MongoDB URI and OpenAI API key.
  - CloudWatch: Logs and monitors application performance.

---

## Prerequisites
- AWS Account
- MongoDB Atlas Cluster
- OpenAI API Key
- AWS CLI and SAM CLI installed locally

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/JasonMadeSomething/Witty404.git
cd Witty404
```

### 2. Set Up MongoDB Atlas
1. Create a MongoDB Atlas cluster.
2. Add your current IP or NAT Gateway IP to the access list.
3. Create a database named `404wit` and a collection named `cache`.

### 3. Set Up Environment Variables
Store sensitive variables in AWS SSM Parameter Store:
```bash
aws ssm put-parameter \
    --name "/Witty404/MONGO_URI" \
    --value "<your-mongodb-uri>" \
    --type "SecureString"

aws ssm put-parameter \
    --name "/Witty404/OPENAI_API_KEY" \
    --value "<your-openai-api-key>" \
    --type "SecureString"
```

### 4. Build and Deploy with SAM
```bash
sam build
sam deploy --guided
```
Follow the prompts to configure the stack.

---

## Usage

### API Endpoint
After deployment, note the API endpoint from the output.

### Making a Request
Send a POST request to the API with the URL to be evaluated:
```bash
curl -X POST https://<your-api-endpoint>/Prod/witty-text \
    -H "Content-Type: application/json" \
    -H "x-api-key: <your-api-key>" \
    -d '{"url": "https://example.com/non-existent-page"}'
```

### Response
```json
{
  "wittyText": "Oops! Looks like you've found a missing page. It's probably off on an adventure!"
}
```

---

## Local Testing

### Running Locally with SAM
1. Create an `events/event.json` file:
   ```json
   {
     "body": "{\"url\": \"https://example.com/non-existent-page\"}"
   }
   ```
2. Invoke the function locally:
   ```bash
   sam local invoke -e events/event.json
   ```

---

## Future Improvements
- Implement a NAT instance for more secure MongoDB access.
- Add customizable prompts for different error message styles.
- Enhance logging and monitoring with AWS X-Ray.

---

## Troubleshooting

### Common Issues
- **500 Internal Server Error**:
  - Check CloudWatch Logs for detailed errors.
  - Ensure SSM parameters are correctly configured.

- **MongoDB Connection Fails**:
  - Verify MongoDB URI is accessible from the Lambda function.
  - Confirm the IP whitelist in MongoDB Atlas includes the Lambda's NAT Gateway or public IP.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgments
- [AWS SAM](https://aws.amazon.com/serverless/sam/)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [OpenAI](https://openai.com)

---

Feel free to contribute to Witty404! Fork the repository, submit a PR, or file an issue. 😊

