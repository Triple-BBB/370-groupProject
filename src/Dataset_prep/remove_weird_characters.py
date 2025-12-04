import pandas as pd

INPUT = "data/processed/processed_speeches/annotation_dataset_RHD_final.csv"
OUTPUT = "data/processed/processed_speeches/annotation_dataset_RHD_final.csv"

def strip_non_ascii(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    # keep ONLY ASCII characters
    return "".join(ch for ch in s if ord(ch) < 128)

def main():
    print("Loading annotation dataset...")
    df = pd.read_csv(INPUT, encoding="latin1")

    # Clean RON *and* DUMBLEDORE for Half-Blood Prince
    mask = (
        (df["movie"] == "half_blood_prince") &
        (df["character"].isin(["RON", "DUMBLEDORE"]))
    )

    print(f"Rows to clean (RON + DUMBLEDORE in HBP): {mask.sum()}")

    # Clean only those rows
    df.loc[mask, "text"] = df.loc[mask, "text"].apply(strip_non_ascii)

    # Save
    df.to_csv(OUTPUT, index=False, encoding="utf-8")
    print("\n✅ Saved cleaned dataset to:")
    print("   ", OUTPUT)
    print("Done.")

if __name__ == "__main__":
    main()
