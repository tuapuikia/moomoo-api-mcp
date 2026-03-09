# Product Guidelines

## Prose Style
- **Professional and Precise:** Documentation, logs, and user-facing messages must use formal, professional language suitable for a financial software product.
- **Clarity over Verbosity:** Strive for clear, concise explanations. Avoid jargon where possible, but maintain correct financial terminology (e.g., "K-lines", "Order Book").
- **Security-First Tone:** Emphasize security and safety in all instructions and warnings.

## Design Principles
- **Minimalist and Functional:** Interfaces and API responses should prioritize delivering data efficiently without unnecessary overhead.
- **Fail-Safe Defaults:** Operations should default to simulation or safe modes. Destructive or risky operations (like real trading) must require explicit opt-in and confirmation mechanisms.

## UX Principles
- **Transparency:** The system must clearly indicate whether it is operating in a REAL or SIMULATE environment.
- **Predictability:** Tools should behave consistently. Errors should return standardized, informative messages.
- **Robust Error Handling:** Surface API errors clearly to the AI agent or user, providing actionable guidance for resolution (e.g., "Moomoo OpenD not running on port 11111").