import anthropic

client = anthropic.Anthropic(api_key="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")

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)

print(message.content[0].text)

