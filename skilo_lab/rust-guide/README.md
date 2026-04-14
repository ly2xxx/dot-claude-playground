# Rust Essentials - 45 Minute Guide

A practical introduction to Rust for developers familiar with Python/JavaScript.

## Quick Start

### 1. Install Rust
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### 2. Test Your Setup
```bash
cd C:\code\dot-claude-playground\skilo_lab\rust-guide\hello_rust
cargo run
```

Expected output:
```
Hello, Rust!
Welcome to the 45-minute Rust guide!
Hello, World!
10 + 20 = 30
```

## What's Inside

```
rust-guide/
├── README.md              # This file - Quick reference
├── hello_rust/           # Your first program (2 min)
│   └── src/main.rs
├── exercises/            # Hands-on practice (~30 min)
│   ├── Cargo.toml
│   └── src/main.rs      # 8 exercises
├── crates_io_tour.md     # Exploring crates.io
├── project_examples/     # Sample project structures
└── references.md        # Detailed topic references
```

## Learning Path

| Time | Topic | Do This |
|------|-------|---------|
| 0-5 min | Setup | Install Rust, run hello_rust |
| 5-15 min | Basics | Variables, types, functions |
| 15-25 min | Ownership | Move, borrow, lifetimes |
| 25-35 min | Structs/Traits | Build something with methods |
| 35-45 min | Error handling | Result, Option, ? operator |

## Running Exercises

```bash
cd C:\code\dot-claude-playground\skilo_lab\rust-guide\exercises
cargo run
```

This runs 8 exercises covering:
1. Variables & mutability
2. Data types
3. Ownership
4. Structs
5. Enums & Match
6. Option & Result
7. Collections (Vec, HashMap)
8. Iterators

## Key Concepts Summary

### Ownership Rules
- Each value has ONE owner
- When owner goes out of scope, value is dropped
- You can have EITHER one mutable reference OR many immutable references

### Syntax Quick Ref
```rust
let x = 5;              // immutable
let mut y = 5;          // mutable
fn foo(x: &str) -> i32 { x.len() as i32 }  // references, return type
```

### Error Handling
```rust
fn might_fail() -> Result<T, E> { ... }
// or
fn might_fail() -> Option<T> { ... }
```

## Essential Commands

```bash
cargo new my_project    # Create project
cargo build             # Compile
cargo run              # Build and run
cargo test             # Run tests
cargo check            # Type check (fast!)
cargo add crate_name  # Add dependency
cargo update          # Update dependencies
```

## Why Rust Matters for Skilo

Skilo uses:
- **clap** - CLI argument parsing
- **serde** - Config/file serialization
- **toml** - TOML config parsing
- Custom parsers for SKILL.md

Understanding these patterns helps you read and contribute to Skilo's source code!

## Next Steps

1. **Rust by Example** - doc.rust-lang.org/rust-by-example
2. **Exercism Rust Track** - exercism.org/tracks/rust
3. **The Book** - doc.rust-lang.org/book
4. **Rustlings** - github.com/rust-lang/rustlings

## Need Help?

- 📖 **The Book**: doc.rust-lang.org/book
- 💬 **Discord**: discord.gg/rust-lang
- ❓ **Forum**: users.rust-lang.org
- 🐦 **Twitter**: @rustlang
