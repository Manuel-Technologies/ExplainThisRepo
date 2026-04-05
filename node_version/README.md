# ExplainThisRepo (Node Launcher)

This is not the core implementation.

This package is a thin Node.js launcher for the real CLI, which is written in Python and bundled as native binaries.

## Architecture

ExplainThisRepo now has a split architecture:

- Python → core logic (analysis, prompts, providers, output)
- PyInstaller → builds native binaries
- Node → launcher only (distribution via npm)

Node does **NOT**:
- fetch repositories
- read files
- generate prompts
- call LLMs
- detect stacks
- manage config

All execution happens inside the bundled Python binary.

## What this package does

- Detects the current platform (Windows, macOS, Linux)
- Selects the correct prebuilt binary
- Executes it with the provided CLI arguments

That’s it.

## Installation

```bash
npm install -g explainthisrepo
```

## Usage
```bash
explainthisrepo owner/repo
```

All flags and behavior are handled by the Python core.

Examples:

```bash
explainthisrepo owner/repo
explainthisrepo owner/repo --quick
explainthisrepo owner/repo --simple
explainthisrepo owner/repo --detailed
explainthisrepo owner/repo --stack
explainthisrepo .
explainthisrepo . --quick
explainthisrepo . --simple
explainthisrepo . --detailed
explainthisrepo . --stack
explainthisrepo ./path/to/directory
explainthisrepo ./path/to/directory --quick
explainthisrepo ./path/to/directory --simple
explainthisrepo ./path/to/directory --detailed
explainthisrepo ./path/to/directory --stack
explainthisrepo owner/repo --llm gemini
explainthisrepo owner/repo --llm openai
explainthisrepo owner/repo --llm ollama
explainthisrepo owner/repo --llm anthropic
explainthisrepo owner/repo --llm openrouter
explainthisrepo owner/repo --llm groq
explainthisrepo --doctor
explainthisrepo --version
```

## Development

You should **NOT** add logic here.

If you need to change behavior: → modify the Python core (`explain_this_repo/`) → rebuild binaries via [PyInstaller](https://pyinstaller.org/en/stable/)

### Build

```bash
npm run build
```

### Local test

```bash
node dist/cli.js facebook/react
```

### Files
`dist/cli.js` → launcher entrypoint

`dist/native/` → platform-specific binaries

`_legacy/` → old Node implementation (unused)


## Important

This [npm package](https://www.npmjs.com/package/explainthisrepo) exists for distribution only.

The real product lives in [Python](https://github.com/calchiwo/ExplainThisRepo/blob/main/explain_this_repo/cli.py) implementation.