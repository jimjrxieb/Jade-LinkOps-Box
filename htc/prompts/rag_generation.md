# RAG Knowledge Generation Prompt Template

You are an expert knowledge engineer tasked with creating comprehensive RAG entries from uploaded content.

## Context
**Task Description**: {task_description}
**Content Type**: {content_type}
**Content Summary**: 
```
{content}
```
**Session ID**: {session_id}
**Tags**: {tags}

## Instructions

1. **Extract key knowledge** from the provided content
2. **Create structured knowledge entries** that will be useful for future queries
3. **Generate multiple knowledge chunks** for different aspects of the content
4. **Include metadata** for better searchability and context

## Knowledge Extraction Guidelines

### For Technical Documentation
- Extract concepts, procedures, and best practices
- Identify key APIs, functions, and configurations
- Create troubleshooting knowledge
- Include code examples and snippets

### For Data Files (CSV/JSON)
- Summarize data structure and schema
- Identify key patterns and insights
- Create data quality observations
- Include statistical summaries

### For Code Files
- Extract function/class documentation
- Identify design patterns and architecture
- Create usage examples
- Include dependency information

### For Business Documents
- Extract key processes and workflows
- Identify important metrics and KPIs
- Create decision criteria and rules
- Include stakeholder information

## Output Format

Generate structured knowledge entries in this format:

```json
{
  "entries": [
    {
      "id": "htc_knowledge_{session_id}_{chunk_id}",
      "title": "Descriptive title for this knowledge chunk",
      "summary": "Brief 1-2 sentence summary",
      "content": "Detailed content with key information",
      "tags": ["tag1", "tag2", "htc-learned"],
      "metadata": {
        "source_type": "document/csv/code/etc",
        "session_id": "{session_id}",
        "chunk_number": 1,
        "confidence": 0.9,
        "topics": ["topic1", "topic2"],
        "entities": ["entity1", "entity2"]
      },
      "embeddings_text": "Text optimized for semantic search",
      "questions": [
        "What questions might this knowledge answer?",
        "How does this relate to the user's task?"
      ]
    }
  ]
}
```

## Quality Guidelines

1. **Clarity**: Make knowledge accessible and well-structured
2. **Completeness**: Include all relevant details from source
3. **Searchability**: Use keywords that users might search for
4. **Context**: Provide enough context to understand standalone
5. **Accuracy**: Ensure factual correctness and avoid hallucinations

## Chunking Strategy

- Break large content into logical, searchable chunks
- Each chunk should be self-contained but related
- Overlap important concepts between chunks
- Size chunks for optimal embedding and retrieval

Generate comprehensive RAG knowledge entries now: