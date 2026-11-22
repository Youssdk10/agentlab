# Model providers

## Primary: local Qwen3 via Ollama
- Free, runs on my machine, no data leaves it.

## Fallback: Groq (checked 2026-11-21)
- **Model used:** `openai/gpt-oss-20b`. The model `llama-3.3-70b-versatile` returned a 404 on my key, so it is no longer available to me.
- **Rate limits (Groq console, Limits page for my account, model `openai/gpt-oss-20b`, checked 2026-11-21):**
  - Requests: 30 per minute, 1,000 per day
  - Tokens: 8,000 per minute, 200,000 per day
- **Cost of one call with my 6 tool schemas:** about 625 tokens. Later calls in a run resend the conversation, so they cost more.
- **What this means:** the daily token cap is the tightest limit. At roughly 1,000 tokens per call (estimate), about 200 calls a day. A full scenario pass may need two days. The run script must pause when rate limited and count tokens.
- **Tool calling:** worked. The model called `get_order` with `{"order_id":101}`. Arguments arrive as a JSON string, not a dict.
- **Credit card:** not required.
- **Data use (Groq's own terms, read on ___):** https://groq.com/terms-of-use (link). - **Data use (Groq's own documents, read 2026-11-21):**
  - Training: Groq Services Agreement, section 4.2 (last modified June 22, 2026): Groq may not use inputs or outputs to train or fine-tune models unless the customer gives permission.
  - Retention: "Your Data" docs page: inference requests are not retained by default. Inputs and outputs may be logged temporarily only to troubleshoot failures or investigate abuse, up to 30 days. Zero Data Retention can be enabled in console Data Controls.
  - Location: retained data is stored in the United States.
  - Caveat: Beta Services are treated differently (section 3.6). Checked on Groq's models page whether gpt-oss-20b is labelled preview: ___
  - Links: console.groq.com/docs/legal/services-agreement and console.groq.com/docs/your-data
- **Rule:** only made-up data. Never send real customer, employer or personal data.
- **API key:** stored in `.env`, never committed.

## Considered and rejected
- OpenRouter: free tier is 50 requests/day, too low for a full scenario pass.
- Google AI Studio and Mistral free tiers: per OpenRouter's comparison, they use prompts for training.