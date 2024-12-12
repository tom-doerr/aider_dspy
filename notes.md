# Aider Implementation Notes

## Context Management & Summarization

### Current Implementation
- Uses weak model (e.g., claude-3-5-haiku) for summarization and commit messages
- Default summarization limit: 1024 tokens
- Recursive summarization with depth parameter (max depth=3)
- Context size limit isn't strictly enforced due to depth=0 check
- Manual triggers: `/summarize` or `/force-summary` commands
- Configurable via `--max-chat-history-tokens`

### Issues Identified
- Context window can exceed set maximum due to summarization logic
- depth=0 check bypasses token limits on first pass
- No aggressive summarization option
- Limited configuration options during chat session

### Potential Improvements
1. Remove depth=0 special case to always enforce token limit
2. Add aggressive summarization option
3. Add runtime configuration command
4. Better monitoring/warnings for context limits

## Caching System

### Current State
- Main prompt caching disabled (CACHE = None in sendchat.py)
- Cache implementation exists but inactive
- Would use JSON-encoded request parameters as key
- Separate active caching for repo maps
- Cache invalidation issues with read-only files

### Repo Map Caching
- Controlled by map_refresh setting:
  - "auto" - includes mentioned files/identifiers
  - "always" - no caching
  - "files" - only invalidate on file changes
  - "manual" - only refresh on command
- Cache key includes:
  - chat_fnames
  - other_fnames
  - max_map_tokens
  - (in auto mode) mentioned_fnames/idents

### Improvements Needed
1. Enable main prompt caching
2. Adjust repo map cache key generation
3. More aggressive caching for read-only files
4. Better cache invalidation strategy

## DSPy Integration

### Current System
- Prompts stored as strings in prompts.py
- System prompts part of Coder classes
- Uses litellm for chat completion
- Handles streaming responses

### Integration Requirements
1. New DSPy Components Needed:
   - DSPy chat backend
   - Signature definitions
   - Module implementations
   - Template management
   - Compatibility layer

2. Key Features to Support:
   - Streaming responses
   - Message format conversion
   - Function calling
   - Existing aider features

3. Migration Strategy:
   - Support both backends
   - Gradual transition
   - Configuration through settings
   - Fallback mechanisms

### Implementation Considerations
- Streaming support depends on DSPy capabilities
- Message format conversion needed
- Function calling compatibility
- Maintaining existing features
- Configuration system integration

### Configuration
- Model settings via yaml
- Backend selection
- Module configuration
- Template management
- Compatibility settings

## Commands and Usage

### Current Commands
- `/summarize` - Force summarization
- `/tokens` - Check token usage
- `/map_refresh` - Force repo map refresh

### Monitoring
- Token usage tracking
- Context window size
- Cache hit/miss rates
- Model performance metrics

## Future Work
1. Context Management
   - Stricter token limits
   - Better summarization strategies
   - More configuration options

2. Caching
   - Enable prompt caching
   - Improve cache key generation
   - Better invalidation strategies

3. DSPy Integration
   - Implement backend
   - Add signatures/modules
   - Ensure compatibility
   - Support streaming

4. General Improvements
   - Better monitoring
   - More configuration options
   - Enhanced error handling
   - Performance optimization
