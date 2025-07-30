# PR Reviewer Helper

A local CLI tool that automates personal code reviews by extracting GitHub PR metadata and generating readable diffs for ChatGPT analysis.

## Features

- Extract GitHub PR metadata using your credentials
- Generate diffs between PR branch and main branch
- Output formatted text files readable by ChatGPT
- Configurable via environment variables
- **Smart repository caching** - clones once, reuses and updates
- **Repository configuration** - set once in environment variables
- **Docker support** - portable and disposable execution

## Installation

### Option 1: Local Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (see Configuration section)

### Option 2: Docker Installation (Recommended)

1. Clone this repository
2. Set up environment variables (see Configuration section)
3. Build the Docker image:
   ```bash
   docker build -t local-pr-reviewer .
   ```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
GITHUB_REPOSITORY=owner/repo
```

### Getting a GitHub Token

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a new token with `repo` permissions
3. Copy the token to your `.env` file

### Repository Caching

The tool automatically caches repositories to avoid re-cloning:

- **Local**: `~/.pr_reviewer_cache/`
- **Docker**: `/cache` (persistent volume)

Repositories are updated automatically on each run.

## Usage

### Local Usage

```bash
python main.py <pr_number>
```

Examples:

```bash
# Basic usage
python main.py 123

# With custom output directory
python main.py 456 --output-dir ./reviews

# Include comments and review comments
python main.py 789 --include-comments --include-review-comments

# Skip diff generation for large PRs
python main.py 123 --skip-diff

# Clean cache and re-clone repository
python main.py 123 --clean-cache
```

### Docker Usage

#### Using the convenience script:

```bash
./docker-run.sh --pr 123
./docker-run.sh --pr 456 --output-dir ./reviews
./docker-run.sh --pr 789 --include-comments --include-review-comments
```

#### Direct Docker commands:

```bash
# Basic usage
docker run --rm -v ~/.pr_reviewer_cache:/cache -v $(pwd)/reviews:/app/output --env-file .env local-pr-reviewer --pr 123

# With all options
docker run --rm \
  -v ~/.pr_reviewer_cache:/cache \
  -v $(pwd)/reviews:/app/output \
  --env-file .env \
  local-pr-reviewer \
  --pr 123 \
  --output-dir /app/output \
  --include-comments \
  --include-review-comments
```

## Output

The tool generates a `.txt` file containing:

- PR metadata (title, description, author, etc.)
- Diff between PR branch and main branch
- Formatted for easy reading by ChatGPT

**Default Output Location**: `./reviews/` directory in the project root

## Repository Management

- **First run**: Repository is cloned to cache directory
- **Subsequent runs**: Repository is updated with latest changes
- **Cache cleanup**: Use `--clean-cache` to force re-cloning
- **Docker persistence**: Cache is preserved between container runs

## Docker Benefits

- **Portable**: Works on any OS with Docker
- **Isolated**: No local Python dependencies required
- **Disposable**: Clean environment for each run
- **Persistent**: Repository cache survives container restarts
- **Shareable**: Easy to share with colleagues

## Project Structure

```
pr-reviewer-helper/
├── main.py              # Main CLI entry point
├── config.py            # Configuration management
├── utils/
│   ├── github_api.py    # GitHub API interactions
│   ├── git_ops.py       # Git operations and diff generation
│   └── file_writer.py   # File output formatting
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker container definition
├── docker-compose.yml   # Docker Compose configuration
├── docker-run.sh        # Convenience script for Docker usage
├── .dockerignore        # Docker build exclusions
├── reviews/             # Default output directory for review files
└── README.md           # This file
```

## License

MIT
