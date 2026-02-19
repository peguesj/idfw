import Config

# We don't run a server during test. If one is required,
# you can enable the server option below.
config :wiki, WikiWeb.Endpoint,
  http: [ip: {127, 0, 0, 1}, port: 4002],
  secret_key_base: "zAL7AH6DAmBk8Khj2RNiv170ph+0ugaeMTO0A2XbsNIM1VcI3MGsM0fIHtVgWX27",
  server: false

# Print only warnings and errors during test
config :logger, level: :warning

# Initialize plugs at runtime for faster test compilation
config :phoenix, :plug_init_mode, :runtime

# Enable helpful, but potentially expensive runtime checks
config :phoenix_live_view,
  enable_expensive_runtime_checks: true

# Sort query params output of verified routes for robust url comparisons
config :phoenix,
  sort_verified_routes_query_params: true
