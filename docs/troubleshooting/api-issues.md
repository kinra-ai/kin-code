# API Issues

Solutions for provider and API problems.

## Authentication Errors

### "Invalid API key"

The API key is incorrect or expired.

**Solutions:**
1. Verify key is correct (no extra spaces)
2. Regenerate key from provider dashboard
3. Check key hasn't expired
4. Ensure key has required permissions

### "API key not found"

Key is not configured.

**Solutions:**
1. Run `kin --setup`
2. Set environment variable
3. Add to `~/.kin-code/.env`

## Rate Limits

### "Rate limit exceeded"

Too many requests in a short time.

**Solutions:**
1. Wait a few minutes
2. Reduce request frequency
3. Upgrade API plan
4. Try a different model

### "Quota exceeded"

Monthly quota exhausted.

**Solutions:**
1. Check usage dashboard
2. Wait for quota reset
3. Upgrade API plan
4. Use a different provider

## Connection Errors

### "Connection timeout"

Can't reach the API server.

**Solutions:**
1. Check internet connection
2. Verify API endpoint is correct
3. Check for service outages
4. Try again later

### "SSL certificate error"

Certificate validation failed.

**Solutions:**
1. Update SSL certificates
2. Check system time is correct
3. Update Python/requests library

## Model Errors

### "Model not found"

Specified model doesn't exist.

**Solutions:**
1. Check model name spelling
2. Verify model is available in your region
3. Check API key has access to model
4. Use a different model

### "Context length exceeded"

Input too long for the model.

**Solutions:**
1. Use `/compact` to reduce history
2. Start a new session
3. Use a model with larger context

## Provider-Specific Issues

### OpenAI

- Check status: https://status.openai.com
- Verify organization ID if applicable

### Anthropic

- Check status: https://status.anthropic.com
- Verify API version compatibility

### OpenRouter

- Check individual model status
- Verify credits available

## Debugging

### Check API Response

Use `--output json` to see full response:

```bash
kin --prompt "test" --output json
```

### Verify Configuration

```bash
kin --setup
```

## Related

- [API Keys](../getting-started/api-keys.md)
- [Models](../configuration/models.md)
- [Common Issues](common-issues.md)
