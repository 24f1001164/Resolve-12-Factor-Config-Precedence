# Resolve-12-Factor-Config-Precedence
Deploy a FastAPI service that merges four configuration layers — defaults, environment-specific YAML, .env file, and OS-level environment variables — then applies CLI overrides passed as query parameters. The grader sends fresh random overrides on every check.
