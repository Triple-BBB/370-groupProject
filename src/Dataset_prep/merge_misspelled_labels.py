import pandas as pd

INPUT = "data/processed/processed_speeches/annotation_dataset_RHD_final.csv"
OUTPUT = "data/processed/processed_speeches/annotation_dataset_RHD_final.csv"

def main():
    print("Loading dataset...")
    df = pd.read_csv(INPUT, encoding="utf-8")

    # Count before fixing
    before = (df["annotation_label"] == "Infromative").sum()
    print(f"Found {before} occurrences of 'Infromative'")

    # Replace incorrect spelling
    df["annotation_label"] = df["annotation_label"].replace({
        "Infromative": "Informative"
    })

    # Count after fixing
    after = (df["annotation_label"] == "Infromative").sum()
    print(f"After correction: {after} remaining")

    # Save cleaned file (overwrite)
    df.to_csv(OUTPUT, index=False, encoding="utf-8")
    print("\n✅ Saved corrected dataset to:")
    print("   ", OUTPUT)

if __name__ == "__main__":
    main()
