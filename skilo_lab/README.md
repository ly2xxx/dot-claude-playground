# Skilo Lab

Experimental space for testing Agent Skills validation and linting using Skilo CLI tool, and learning Rust.

## What is Skilo?

Skilo is a CLI tool for Agent Skills development that provides:
- **Validation** - Check skill structure and compliance
- **Formatting** - Auto-format SKILL.md files
- **Template generation** - Create skills from templates

## Installation

```bash
# Quick install
curl -sSfL https://raw.githubusercontent.com/manuelmauro/skilo/main/install.sh | sh

# Or from crates.io
cargo install skilo
```

## Quick Start

```bash
# Validate an existing skill
skilo validate test-skill/

# Format all SKILL.md files
skilo fmt .

# Check formatting without making changes
skilo fmt --check .
```

---

## 🦀 Rust Guide - Learn Rust in 45 Minutes!

New to Rust? This guide has everything you need to get started.

### 📁 Contents

```
rust-guide/
├── README.md              # Quick start & overview
├── hello_rust/           # Your first Rust program (2 min)
├── exercises/            # Hands-on practice (~30 min)
│   └── src/main.rs      # 8 exercises with solutions
├── crates_io_tour.md    # Exploring crates.io ecosystem
└── references.md        # Detailed topic references
```

### 🚀 Quick Start

1. **Install Rust:**
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Test your setup:**
   ```bash
   cd C:\code\dot-claude-playground\skilo_lab\rust-guide\hello_rust
   cargo run
   ```

3. **Run exercises:**
   ```bash
   cd C:\code\dot-claude-playground\skilo_lab\rust-guide\exercises
   cargo run
   ```

### 📚 What's Inside

| Section | Time | What You Learn |
|---------|------|----------------|
| hello_rust | 2 min | Basic syntax, println! |
| exercises 1-3 | 10 min | Variables, types, ownership |
| exercises 4-6 | 10 min | Structs, enums, error handling |
| exercises 7-8 | 10 min | Collections, iterators |
| crates_io_tour | 5 min | Ecosystem, popular crates |

### 🎯 Why Learn Rust?

- **Memory safe** without garbage collection
- **Zero-cost abstractions** - high-level features, low-level speed
- **Fearless concurrency** - data races impossible at compile time
- **Modern tooling** - cargo is best-in-class
- **Skilo is written in Rust** - understand how it works!

### 📖 Topics Covered

- Variables & mutability
- Data types (i32, f64, bool, String, &str)
- Functions & ownership
- Borrowing & references
- Structs & impl blocks
- Enums & pattern matching
- Result & Option
- Vectors & HashMaps
- Iterators
- Basic concurrency
- Cargo workflow
- crates.io ecosystem

---

## Testing Area

This directory also contains sample skills to test Skilo's validation capabilities:

### Skills to Test
- `good-skill/` - Properly structured skill
- `bad-skill/` - Various validation issues (bad name, short description)
- `complex-skill/` - Multi-resource skill with scripts/, references/, assets/
- `test-skill/` - Simple test case

### Test Scripts
- `test-skilo.ps1` - PowerShell script to run all tests
- `validation-rules.md` - Detailed documentation of validation rules

## Running Tests

Once Skilo is installed:

```powershell
cd C:\code\dot-claude-playground\skilo_lab
.\test-skilo.ps1
```

---

## Resources

### Rust Learning
- [The Book](https://doc.rust-lang.org/book/) - Official documentation
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/) - Learn by doing
- [Exercism Rust Track](https://exercism.org/tracks/rust) - Practice problems
- [Rustlings](https://github.com/rust-lang/rustlings) - Small exercises

### Skilo
- [Skilo GitHub](https://github.com/manuelmauro/skilo)
- [Agent Skills Spec](https://agentskills.io/specification)
- [Best Practices Guide](https://agentskills.io/skill-creation/best-practices)
