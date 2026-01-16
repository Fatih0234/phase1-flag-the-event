# Phase 1 Prompts

This directory contains versioned prompts for bike relevance classification.

## Naming Convention

- Filenames: `v001.md`, `v002.md`, `v003.md`, etc.
- Use zero-padded 3-digit version numbers
- Always use `.md` extension for markdown format

## Adding New Prompts

1. Copy the most recent version:
   ```bash
   cp prompts/phase1/v001.md prompts/phase1/v002.md
   ```

2. Make your changes to the new version

3. Test the new prompt:
   ```bash
   python -m bikeclf.phase1.eval evaluate --prompt v002
   ```

4. Commit with descriptive message:
   ```bash
   git add prompts/phase1/v002.md
   git commit -m "Add v002: Improved evidence extraction for ambiguous cases"
   ```

## Usage

### List Available Prompts
```bash
python -m bikeclf.phase1.eval list-prompts
```

### Use Specific Version
```bash
python -m bikeclf.phase1.eval evaluate \
  --prompt v001 \
  --dataset bike_related_gold_dataset_A_to_F.csv
```

## Prompt Structure

Each prompt should include:

1. **Role Definition**: Who the model is (e.g., "Urban data analyst for Cologne")
2. **Task Description**: What the model needs to do (classify bike relevance)
3. **Decision Criteria**: Clear rules for TRUE/FALSE/UNCERTAIN
4. **Evidence Requirements**: What constitutes valid evidence
5. **Output Format**: JSON schema specification
6. **VETO Rule**: No inference beyond explicit evidence

## Best Practices

- **Be Explicit**: Avoid ambiguous language
- **Use Examples**: Include concrete examples when helpful
- **Test Incrementally**: Make small changes and test
- **Document Changes**: Explain what changed in git commit
- **Track Metrics**: Compare performance before/after changes

## Version History

- **v001**: Initial prompt with decision tree and VETO rule
