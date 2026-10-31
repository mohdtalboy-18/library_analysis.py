
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Project paths
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "library_loans_sample.csv"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)


def load_data():
    """Load and prepare library loan data."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "library_loans_sample.csv not found. "
            "Keep the CSV file in the project folder."
        )

    df = pd.read_csv(DATA_FILE)

    required_columns = [
        "loan_id",
        "borrow_date",
        "due_date",
        "return_date",
        "book_id",
        "title",
        "category",
        "borrower_type"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Convert date columns
    for col in ["borrow_date", "due_date", "return_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Calculate days late
    df["days_late"] = (
        df["return_date"] - df["due_date"]
    ).dt.days.clip(lower=0)

    df["is_late"] = df["days_late"].gt(0).fillna(False)

    # Extract month of borrowing
    df["borrow_month"] = (
        df["borrow_date"].dt.to_period("M").astype("string")
    )

    return df


def show_basic_summary(df):
    """Display basic dataset information."""

    print("\n===== LIBRARY DATA SUMMARY =====")
    print("Total loan records:", len(df))
    print("Unique book titles:", df["title"].nunique())
    print("Book categories:", df["category"].nunique())

    print("\nMissing values:")
    print(df.isna().sum())

    print("\nDuplicate loan IDs:", df["loan_id"].duplicated().sum())


def analyze_popular_books(df):
    """Rank the most borrowed book titles."""

    book_counts = df["title"].value_counts()

    print("\n===== MOST BORROWED BOOKS =====")
    print(book_counts)

    book_counts.to_csv(OUTPUT_DIR / "book_rankings.csv")

    ax = book_counts.plot(
        kind="bar",
        figsize=(10, 5)
    )

    ax.set_title("Most Borrowed Book Titles")
    ax.set_xlabel("Book Title")
    ax.set_ylabel("Number of Loans")

    plt.xticks(rotation=40, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "popular_books.png")
    plt.show()
    plt.close()


def analyze_categories(df):
    """Analyze borrowing by book category."""

    category_counts = df["category"].value_counts()

    print("\n===== CATEGORY ANALYSIS =====")
    print(category_counts)

    category_counts.to_csv(OUTPUT_DIR / "category_rankings.csv")

    ax = category_counts.plot(
        kind="bar",
        figsize=(8, 5)
    )

    ax.set_title("Book Loans by Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of Loans")

    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "category_analysis.png")
    plt.show()
    plt.close()


def analyze_monthly_circulation(df):
    """Analyze borrowing activity month by month."""

    monthly_counts = (
        df.dropna(subset=["borrow_month"])
        .groupby("borrow_month")
        .size()
        .sort_index()
    )

    print("\n===== MONTHLY CIRCULATION =====")
    print(monthly_counts)

    monthly_counts.to_csv(OUTPUT_DIR / "monthly_circulation.csv")

    ax = monthly_counts.plot(
        kind="line",
        marker="o",
        figsize=(9, 5)
    )

    ax.set_title("Monthly Book Circulation")
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Loans")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "monthly_circulation.png")
    plt.show()
    plt.close()

    if not monthly_counts.empty:
        print("Highest circulation month:", monthly_counts.idxmax())


def analyze_late_returns(df):
    """Calculate late-return rates using valid due and return dates."""

    returned = df.dropna(
        subset=["due_date", "return_date"]
    ).copy()

    total_returned = len(returned)
    late_returns = int(returned["is_late"].sum())

    late_rate = (
        late_returns / total_returned * 100
        if total_returned > 0 else 0
    )

    print("\n===== LATE RETURN ANALYSIS =====")
    print("Records with due and return dates:", total_returned)
    print("Late returns:", late_returns)
    print(f"Late-return rate: {late_rate:.2f}%")

    if returned.empty:
        print("No valid returned records available.")
        return

    category_late = returned.groupby("category").agg(
        total_returns=("loan_id", "count"),
        late_returns=("is_late", "sum"),
        average_days_late=("days_late", "mean")
    )

    category_late["late_rate_percent"] = (
        category_late["late_returns"]
        / category_late["total_returns"] * 100
    ).round(2)

    category_late["average_days_late"] = (
        category_late["average_days_late"].round(2)
    )

    print("\nLate returns by category:")
    print(category_late)

    category_late.to_csv(
        OUTPUT_DIR / "late_return_analysis.csv"
    )

    ax = category_late["late_rate_percent"].plot(
        kind="bar",
        figsize=(8, 5)
    )

    ax.set_title("Late-Return Rate by Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Late Returns (%)")

    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "late_return_analysis.png")
    plt.show()
    plt.close()


def analyze_borrowers(df):
    """Compare student and faculty borrowing."""

    borrower_counts = df["borrower_type"].value_counts()

    print("\n===== BORROWER ANALYSIS =====")
    print(borrower_counts)

    borrower_counts.to_csv(
        OUTPUT_DIR / "borrower_analysis.csv"
    )

    if borrower_counts.empty:
        return

    borrower_counts.plot(
        kind="pie",
        autopct="%1.1f%%",
        figsize=(6, 6)
    )

    plt.title("Loans by Borrower Type")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "borrower_analysis.png")
    plt.show()
    plt.close()


def main():
    """Run the complete library analysis."""

    try:
        df = load_data()

        show_basic_summary(df)
        analyze_popular_books(df)
        analyze_categories(df)
        analyze_monthly_circulation(df)
        analyze_late_returns(df)
        analyze_borrowers(df)

        # Save cleaned dataset
        df.to_csv(
            OUTPUT_DIR / "cleaned_library_data.csv",
            index=False
        )

        print("\n===== PROJECT COMPLETED =====")
        print("Check the outputs folder for charts and CSV reports.")

    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
        print("Error:", error)


if __name__ == "__main__":
    main()
