use serde_json::Value;
use std::env;
use std::fs;
use std::path::Path;

fn sizeof_value(v: &Value) -> usize {
    match v {
        Value::Object(map) => map
            .iter()
            .map(|(k, v)| k.len() + sizeof_value(v))
            .sum(),
        Value::Array(arr) => arr.iter().map(sizeof_value).sum(),
        Value::String(s) => s.len(),
        _ => 8, // number, bool, null
    }
}

fn walk(v: &Value, path: &str, depth: usize, max_depth: usize) {
    if depth > max_depth {
        return;
    }

    let s = sizeof_value(v);
    println!("{:10}  {}", s, path);

    match v {
        Value::Object(map) if depth < max_depth => {
            for (k, val) in map {
                let sub = format!("{}.{}", path, k);
                walk(val, &sub, depth + 1, max_depth);
            }
        }
        Value::Array(arr) if depth < max_depth => {
            for (i, val) in arr.iter().enumerate() {
                let sub = format!("{}[{}]", path, i);
                walk(val, &sub, depth + 1, max_depth);
            }
        }
        _ => {}
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} file.json [max_depth]", args[0]);
        std::process::exit(1);
    }

    let file = Path::new(&args[1]);
    let depth: usize = args.get(2).and_then(|d| d.parse().ok()).unwrap_or(8);

    let data = fs::read_to_string(file).expect("read file");
    let v: Value = serde_json::from_str(&data).expect("parse JSON");

    walk(&v, "root", 0, depth);
}
