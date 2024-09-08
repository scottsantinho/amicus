import os
import replicate

# Set the API token
os.environ["REPLICATE_API_TOKEN"] = "r8_c6r9g8dIYQikvaKmlzldfU2fE56FlqB4SbQjd"

# Run a model
output = replicate.run(
    "meta/meta-llama-3-70b-instruct",
    input={"prompt": "Hello, how are you?"}
)
print(output)