// ============================================
// RUST ESSENTIALS - PRACTICAL EXERCISES
// ============================================
// Time: ~30 minutes
// Run with: cargo run --example exercise_01
// ============================================

// --------------------------------------------
// EXERCISE 1: Variables and Functions
// --------------------------------------------
// Goal: Understand immutability by default

fn exercise_01() {
    println!("\n=== Exercise 1: Variables ===");
    
    // TODO 1: Create an immutable variable `age` = 25
    // TODO 2: Create a mutable variable `score` = 100
    // TODO 3: Try to change `age` - what error do you get?
    // TODO 4: Change `score` and print it
    
    let age = 25;
    let mut score = 100;
    
    println!("Age: {} (immutable)", age);
    score = 150;
    println!("Score: {} (mutated)", score);
}

// --------------------------------------------
// EXERCISE 2: Data Types
// --------------------------------------------
fn exercise_02() {
    println!("\n=== Exercise 2: Data Types ===");
    
    // Scalar types
    let integer: i32 = -42;
    let float: f64 = 3.14159;
    let boolean: bool = true;
    let character: char = 'R';
    
    println!("Integer: {}", integer);
    println!("Float: {}", float);
    println!("Boolean: {}", boolean);
    println!("Character: {}", character);
    
    // Array
    let arr: [i32; 3] = [1, 2, 3];
    println!("Array: {:?}", arr);
    
    // Tuple
    let tuple = (500, 6.4, 1);
    println!("Tuple: {:?}", tuple);
    println!("Tuple.0: {}", tuple.0);
}

// --------------------------------------------
// EXERCISE 3: Ownership
// --------------------------------------------
fn exercise_03() {
    println!("\n=== Exercise 3: Ownership ===");
    
    let s1 = String::from("hello");
    let s2 = s1; // s1 is MOVED to s2
    
    // println!("s1: {}", s1); // ERROR: s1 is invalid!
    println!("s2: {}", s2); // This works
    
    // Borrowing instead of moving
    let s3 = String::from("world");
    let s4 = &s3;
    println!("s3 (borrowed): {}", s3);
    println!("s4 (borrow): {}", s4);
}

// --------------------------------------------
// EXERCISE 4: Structs
// --------------------------------------------
struct User {
    username: String,
    email: String,
    active: bool,
}

impl User {
    fn new(username: String, email: String) -> User {
        User {
            username,
            email,
            active: true,
        }
    }
    
    fn display(&self) {
        println!("User: {} <{}> - {}", 
            self.username, self.email, 
            if self.active { "Active" } else { "Inactive" });
    }
}

fn exercise_04() {
    println!("\n=== Exercise 4: Structs ===");
    
    let user = User::new(
        String::from("alice"),
        String::from("alice@example.com")
    );
    user.display();
}

// --------------------------------------------
// EXERCISE 5: Enums and Match
// --------------------------------------------
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(i32, i32, i32),
}

fn process_message(msg: Message) {
    match msg {
        Message::Quit => println!("Quit!"),
        Message::Move { x, y } => println!("Move to ({}, {})", x, y),
        Message::Write(text) => println!("Write: {}", text),
        Message::ChangeColor(r, g, b) => println!("Color: rgb({},{},{})", r, g, b),
    }
}

fn exercise_05() {
    println!("\n=== Exercise 5: Enums & Match ===");
    
    process_message(Message::Quit);
    process_message(Message::Move { x: 10, y: 20 });
    process_message(Message::Write(String::from("Hello!")));
    process_message(Message::ChangeColor(255, 0, 0));
}

// --------------------------------------------
// EXERCISE 6: Option and Result
// --------------------------------------------
fn divide(a: f64, b: f64) -> Option<f64> {
    if b == 0.0 {
        None
    } else {
        Some(a / b)
    }
}

fn read_number(s: &str) -> Result<i32, std::num::ParseIntError> {
    s.parse::<i32>()
}

fn exercise_06() {
    println!("\n=== Exercise 6: Option & Result ===");
    
    // Option
    let result = divide(10.0, 2.0);
    match result {
        Some(val) => println!("10 / 2 = {}", val),
        None => println!("Division by zero!"),
    }
    
    // Result
    match read_number("42") {
        Ok(n) => println!("Parsed: {}", n),
        Err(e) => println!("Error: {}", e),
    }
    
    // Using unwrap_or
    let bad = read_number("not a number").unwrap_or(-1);
    println!("Fallback: {}", bad);
}

// --------------------------------------------
// EXERCISE 7: Collections
// --------------------------------------------
fn exercise_07() {
    println!("\n=== Exercise 7: Collections ===");
    
    // Vector
    let mut v = vec![1, 2, 3];
    v.push(4);
    println!("Vector: {:?}", v);
    
    // HashMap
    use std::collections::HashMap;
    let mut scores = HashMap::new();
    scores.insert("Alice", 100);
    scores.insert("Bob", 85);
    
    if let Some(score) = scores.get("Alice") {
        println!("Alice's score: {}", score);
    }
}

// --------------------------------------------
// EXERCISE 8: Iterators
// --------------------------------------------
fn exercise_08() {
    println!("\n=== Exercise 8: Iterators ===");
    
    let numbers = vec![1, 2, 3, 4, 5];
    
    // Map
    let doubled: Vec<i32> = numbers.iter().map(|x| x * 2).collect();
    println!("Doubled: {:?}", doubled);
    
    // Filter
    let evens: Vec<&i32> = numbers.iter().filter(|x| *x % 2 == 0).collect();
    println!("Evens: {:?}", evens);
    
    // Chain
    let sum: i32 = numbers.iter().filter(|&&x| x > 2).sum();
    println!("Sum of > 2: {}", sum);
}

// --------------------------------------------
// MAIN - Run all exercises
// --------------------------------------------
fn main() {
    println!("╔══════════════════════════════════════╗");
    println!("║   RUST ESSENTIALS - EXERCISES       ║");
    println!("╚══════════════════════════════════════╝");
    
    exercise_01();
    exercise_02();
    exercise_03();
    exercise_04();
    exercise_05();
    exercise_06();
    exercise_07();
    exercise_08();
    
    println!("\n✅ All exercises completed!");
}
