import pandas as pd
import argparse

def analyze(file_path):
    df = pd.read_csv(file_path)
    # Perform complex logic that is hard to prompt
    roi = (df['revenue'] - df['cost']) / df['cost']
    print(f"Average ROI: {roi.mean():.2%}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    analyze(args.input)