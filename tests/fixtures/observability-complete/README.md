# Project with Complete Observability

## Logging Setup

The application uses Python's standard logging module with custom configuration in `logging.conf`.

### Debug Mode

Set `DEBUG=true` in your environment variables to enable debug-level logging.

### Health Check

Access the health endpoint at `/health` to check application status.

## Monitoring

Prometheus metrics are exposed at `/metrics` endpoint. See `prometheus.yml` for scrape configuration.

## Observability Features

- Request logging for all API endpoints
- Performance metrics tracking
- Health check endpoint
- Distributed tracing support
