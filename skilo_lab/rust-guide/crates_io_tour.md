# Crates.io Tour

## Overview

[crates.io](https://crates.io) is Rust's package registry - like PyPI for Python or npm for JavaScript. As of 2025, it has **100,000+ crates**!

## Quick Stats

- 100,000+ crates
- 1.5 billion downloads
- Top crates used by millions of projects

## Top Crates by Category

### Web Frameworks
| Crate | Downloads | Description |
|-------|-----------|-------------|
| actix-web | 50M+ | High-performance web framework |
| axum | 30M+ | Ergonomic web framework |
| rocket | 25M+ | Easy-to-use web framework |
| warp | 20M+ | Web framework |

### Async Runtime
| Crate | Downloads | Description |
|-------|-----------|-------------|
| tokio | 150M+ | Async runtime for Rust |
| async-std | 20M+ | Async standard library |

### HTTP
| Crate | Downloads | Description |
|-------|-----------|-------------|
| reqwest | 100M+ | HTTP client |
| hyper | 80M+ | HTTP library |

### Serialization
| Crate | Downloads | Description |
|-------|-----------|-------------|
| serde | 500M+ | Serialization framework |
| serde_json | 400M+ | JSON support |
| toml | 80M+ | TOML config files |

### CLI
| Crate | Downloads | Description |
|-------|-----------|-------------|
| clap | 150M+ | CLI argument parser |
| anyhow | 100M+ | Error handling |
| thiserror | 80M+ | Error derive macros |
| structopt | 60M+ | Derive CLI args |

### Logging & Tracing
| Crate | Downloads | Description |
|-------|-----------|-------------|
| tracing | 80M+ | Structured logging |
| log | 100M+ | Logging facade |
| env_logger | 70M+ | Environment-based logger |

### Database
| Crate | Downloads | Description |
|-------|-----------|-------------|
| sqlx | 50M+ | Async database |
| diesel | 40M+ | ORM |
| rusqlite | 50M+ | SQLite bindings |
| redis | 30M+ | Redis client |

### Testing
| Crate | Downloads | Description |
|-------|-----------|-------------|
| mockall | 30M+ | Mocking framework |
| rstest | 15M+ | Parametrized tests |
| proptest | 10M+ | Property testing |

## Skilo's Dependencies

Let's look at what Skilo uses:

```toml
[dependencies]
clap = "4"           # CLI args
serde = { version = "1", features = ["derive"] }  # Serialization
toml = "0.8"         # TOML parsing
anyhow = "1"         # Error handling
comrak = "0.52"      # Markdown parsing
```

## How to Find Crates

### 1. Search crates.io
Visit https://crates.io and search for:
- "json" - JSON handling
- "http client" - API clients
- "cli" - Command-line tools
- "async" - Async programming

### 2. Check lib.rs
https://lib.rs ranks crates by:
- Downloads
- Stars
- Recent activity
- Quality scores

### 3. Awesome Rust
https://github.com/rust-unofficial/awesome-rust

## Using a Crate

### 1. Find it on crates.io
Search for "reqwest" → https://crates.io/crates/reqwest

### 2. Add to Cargo.toml
```toml
[dependencies]
reqwest = "0.12"
```

### 3. Import and use
```rust
use reqwest;

#[tokio::main]
async fn main() -> Result<(), reqwest::Error> {
    let response = reqwest::get("https://httpbin.org/get").await?;
    println!("Status: {}", response.status());
    Ok(())
}
```

### 4. Build and run
```bash
cargo build
cargo run
```

Cargo automatically:
- Downloads crate
- Downloads its dependencies
- Compiles everything
- Pins versions in Cargo.lock

## Version Semver

```toml
# Use exact version
reqwest = "0.12.0"

# Use 0.12.x (any patch)
reqwest = "0.12.0"

# Use 0.x (any 0.x.x)
reqwest = "0.12"

# Any version
reqwest = "*"

# Git dependency
reqwest = { git = "https://github.com/seanmonstar/reqwest" }

# Local path
mylib = { path = "../mylib" }
```

## Features

Many crates have optional features:

```toml
tokio = { version = "1", features = ["full", "tracing"] }
serde = { version = "1", features = ["derive"] }
reqwest = { version = "0.12", features = ["json"] }
```

## Best Practices

1. **Check activity** - Last update date, GitHub issues
2. **Check downloads** - More = more battle-tested
3. **Check stars** - Community approval
4. **Check docs** - docs.rs should be clean
5. **Check MSRV** - Minimum Supported Rust Version

## Example: Adding to a Project

```bash
# Create project
cargo new my_cli
cd my_cli

# Add dependency (auto-edits Cargo.toml)
cargo add clap --features derive
cargo add anyhow
cargo add serde --features derive
cargo add toml
```

Now you have a CLI project with:
- clap for arguments
- anyhow for errors
- serde for serialization
- toml for config

## Skilo's Architecture (from source)

```
skilo/
├── src/
│   ├── main.rs       # Entry point, CLI setup
│   ├── commands/     # CLI subcommands
│   │   ├── new.rs
│   │   ├── validate.rs
│   │   └── fmt.rs
│   ├── skills/       # Skill handling
│   │   ├── mod.rs
│   │   └── skill.rs
│   ├── validation/   # Validation logic
│   └── utils/        # Helpers
├── Cargo.toml
└── tests/
```

Reading Skilo's source is a great way to learn Rust project structure!

## Practice Exercise

1. Create a new project: `cargo new crate_tour`
2. Add dependencies:
   ```bash
   cargo add serde_json
   cargo add clap --features derive
   cargo add thiserror
   cargo add log env_logger
   ```
3. Build and run: `cargo run`
4. Check what was added to Cargo.toml
5. Explore docs.rs for each crate

This gives you a production-ready CLI scaffold!
