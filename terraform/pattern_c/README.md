# Pattern C: Workflow (Multi-Process)

## How to Call the API

After deployment, get the API endpoint from Terraform output:

```bash
terraform output api_endpoint
```

### Health Check
```bash
curl https://YOUR_API_ENDPOINT/health
```

### Chat Endpoint
```bash
curl -X POST https://YOUR_API_ENDPOINT/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Book tomorrow at 3pm"}'
```

## How to See the Logs

### AWS Console
1. Go to https://console.aws.amazon.com/cloudwatch/
2. Navigate to: Logs → Log groups
3. Find: `/aws/lambda/ai-patterns-pattern-c`

### AWS CLI (Recommended)
```bash
# Tail logs in real-time
aws logs tail /aws/lambda/ai-patterns-pattern-c --follow

# View last 1 hour
aws logs tail /aws/lambda/ai-patterns-pattern-c --since 1h

# Filter for errors only
aws logs tail /aws/lambda/ai-patterns-pattern-c --follow --filter-pattern "ERROR"
```
