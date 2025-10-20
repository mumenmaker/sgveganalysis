# Enhancement Delay Configuration

## Overview
The enhance command includes a configurable delay between page requests to avoid throttling and CAPTCHA issues from HappyCow.

## Configuration

### Environment Variable
Set the `ENHANCE_DELAY_BETWEEN_PAGES` environment variable in your `.env` file:

```bash
# Enhancement Configuration
ENHANCE_DELAY_BETWEEN_PAGES=3  # Delay between page requests in seconds
```

### Default Value
- **Default**: 3 seconds
- **Recommended Range**: 2-5 seconds
- **Minimum**: 1 second (not recommended)
- **Maximum**: 10 seconds (for very slow connections)

## Usage Examples

### Standard Enhancement (3s delay)
```bash
python main.py enhance --limit 10
```

### Custom Delay via Environment
```bash
# Set in .env file
ENHANCE_DELAY_BETWEEN_PAGES=5

# Then run enhance
python main.py enhance --limit 5
```

### Single Restaurant Enhancement
```bash
python main.py enhance --id 500
```

## Why This Delay?

1. **Avoid Throttling**: HappyCow may throttle requests that come too quickly
2. **Prevent CAPTCHA**: Reduces likelihood of triggering CAPTCHA challenges
3. **Respectful Scraping**: Shows consideration for the website's resources
4. **Reliability**: Reduces chance of requests being blocked or failed

## Timing Impact

- **3 seconds delay**: ~3 minutes for 60 restaurants
- **5 seconds delay**: ~5 minutes for 60 restaurants
- **No delay**: Risk of throttling/CAPTCHA

## Troubleshooting

### If you get CAPTCHA challenges:
- Increase `ENHANCE_DELAY_BETWEEN_PAGES` to 5-7 seconds
- Consider running smaller batches with `--limit`

### If enhancement is too slow:
- Decrease `ENHANCE_DELAY_BETWEEN_PAGES` to 2 seconds (minimum recommended)
- Use `--start-id` to resume from specific points

### If requests are being blocked:
- Increase delay to 5-10 seconds
- Run smaller batches (--limit 10-20)
- Consider running during off-peak hours
