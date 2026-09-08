`opentelemetry()`, `clickhouse()`, `loki()`, `bigquery()`, `pubsub()` destinations: Fixed a crash
in the container image when the destination's host name does not resolve.

c-ares 1.34.8 can lose the DNS query that follows a search domain step, so the lookup never
completes and gRPC aborts the process when it gives up on it. The image now ships c-ares with the
upstream fix applied.
