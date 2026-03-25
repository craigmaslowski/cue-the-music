# Coding Standards — AI Agents

## Structure

1. Each agent lives in its own folder under `agents/`. No monolithic agents folder with everything in one place.
2. An agent is decomposed into separate concerns — not a single file. At minimum: agent definition/orchestration, prompt templates, tool registration, and configuration are separate modules.
3. Shared agent infrastructure (LLM factories, base classes, common utilities) lives in dedicated `infrastructure/` folder. Agents import from these — they do not duplicate common setup.

## Tools

4. Tools that are usable by multiple agents live in a shared `tools/` folder. An agent only owns a tool in its own folder if that tool has no use outside of that specific agent.
5. Tool definitions are self-contained — each tool has its own file with its implementation, input/output schemas, and description.

## Prompts

6. Prompts are never raw inline strings in agent code. Prompts live in template files or dedicated prompt modules with builder functions that assemble the final prompt. Agent orchestration code calls prompt builders, it does not construct prompts.

## Configuration

7. Agent configuration (model selection, temperature, token limits, retry logic) is externalized — not hardcoded. Configuration is easily swappable per environment or use case without code changes.

## Testing

8. Three levels of testing are required: unit tests for individual tools, integration tests for full agent runs, and custom eval suites that validate agent output quality.

## Performance

9. Agents must be designed for execution speed. Minimize unnecessary LLM round-trips. Prefer parallel tool execution where tools are independent. Structure agent graphs to avoid sequential steps that could be concurrent.

## Anti-patterns

10. No single-file agents. No hardcoded prompts. No hardcoded model configuration. No tools defined inline in the agent orchestration code.
