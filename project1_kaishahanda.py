# Name: Kaisha Handa
# Student ID: 72778485
# Email: kaishah@umich.edu
# Collaborators: None
# GenAI Use: Used ChatGPT to find debugging strategies and implement the way that some functions needed to be set up, as well as the 
# Dataset: Sample Superstore Dataset

import csv
from typing import List, Dict, Tuple

DATA_FILENAME = "SampleSuperstore.csv"

def _to_float(x: str) -> float:
    try:
        return float(str(x).strip())
    except Exception:
        return 0.0

from decimal import Decimal, ROUND_HALF_UP, getcontext
getcontext().prec = 16

def _round2(x: float) -> float:
    return float(Decimal(str(x)).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP))

def _round3(x: float) -> float:
    return float(Decimal(str(x)).quantize(Decimal("0.000"), rounding=ROUND_HALF_UP))

def read_csv_file(filename: str) -> List[Dict[str, str]]:
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
    return data

def calculate_avg_profit_margin_by_region(data: List[Dict[str, str]]) -> Dict[str, float]:
    region_totals: Dict[str, Dict[str, float]] = {}
    for row in data:
        region = row.get("Region", "").strip()
        sales = _to_float(row.get("Sales", 0))
        profit = _to_float(row.get("Profit", 0))
        if region == "":
            continue
        if region not in region_totals:
            region_totals[region] = {"sales": 0.0, "profit": 0.0}
        region_totals[region]["sales"] += sales
        region_totals[region]["profit"] += profit
    result: Dict[str, float] = {}
    for region, totals in region_totals.items():
        total_sales = totals["sales"]
        total_profit = totals["profit"]
        if total_sales <= 0:
            result[region] = 0.0
        else:
            result[region] = _round2((total_profit / total_sales) * 100.0)
    return result


def calculate_sales_and_avg_discount_by_category(data: List[Dict[str, str]]) -> Dict[str, Tuple[float, float]]:
    by_cat: Dict[str, Dict[str, float | list]] = {}
    for row in data:
        category = row.get("Category", "").strip()
        if category == "":
            continue
        sales = _to_float(row.get("Sales", 0))
        discount = _to_float(row.get("Discount", 0))
        if category not in by_cat:
            by_cat[category] = {"total_sales": 0.0, "discounts": []}
        by_cat[category]["total_sales"] += sales
        by_cat[category]["discounts"].append(discount)
    result: Dict[str, Tuple[float, float]] = {}
    for cat, agg in by_cat.items():
        discounts = agg["discounts"]
        avg_disc = (sum(discounts) / len(discounts)) if discounts else 0.0
        result[cat] = (_round2(agg["total_sales"]), _round3(avg_disc))
    return result

def write_results_txt(mapping: Dict[str, object], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        for k, v in mapping.items():
            f.write(f"{k}: {v}\n")

def write_category_stats_csv(mapping: Dict[str, Tuple[float, float]], filename: str) -> None:
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Category", "TotalSales", "AvgDiscount"])
        for cat, (total_sales, avg_disc) in mapping.items():
            writer.writerow([cat, total_sales, avg_disc])

def test_calculate_avg_profit_margin_by_region_general_two_regions():
    data = [
        {"Region": "East", "Sales": "100", "Profit": "20"},
        {"Region": "East", "Sales": "300", "Profit": "30"},
        {"Region": "West", "Sales": "200", "Profit": "40"},
    ]
    got = calculate_avg_profit_margin_by_region(data)
    assert got["East"] == 12.5 and got["West"] == 20.0

def test_calculate_avg_profit_margin_by_region_edge_zero_sales():
    data = [{"Region": "North", "Sales": "0", "Profit": "10"}]
    got = calculate_avg_profit_margin_by_region(data)
    assert got["North"] == 0.0

def test_calculate_avg_profit_margin_by_region_edge_negative_profit():
    data = [
        {"Region": "South", "Sales": "100", "Profit": "-25"},
        {"Region": "South", "Sales": "100", "Profit": "5"},
    ]
    got = calculate_avg_profit_margin_by_region(data)
    assert got["South"] == -10.0

def test_calculate_avg_profit_margin_by_region_edge_messy_strings():
    data = [
        {"Region": "Central", "Sales": " 250.0 ", "Profit": " 25 "},
        {"Region": "Central", "Sales": "250", "Profit": "25.0"},
    ]
    got = calculate_avg_profit_margin_by_region(data)
    assert got["Central"] == 10.0

def test_calculate_sales_and_avg_discount_by_category_general_two_cats():
    data = [
        {"Category": "Furniture", "Sales": "100", "Discount": "0.1"},
        {"Category": "Furniture", "Sales": "300", "Discount": "0.0"},
        {"Category": "Technology", "Sales": "50", "Discount": "0.2"},
    ]
    got = calculate_sales_and_avg_discount_by_category(data)
    assert got["Furniture"] == (400.0, 0.05)
    assert got["Technology"] == (50.0, 0.2)

def test_calculate_sales_and_avg_discount_by_category_edge_blank_category():
    data = [
        {"Category": " ", "Sales": "100", "Discount": "0.3"},
        {"Category": "Office Supplies", "Sales": "100", "Discount": "0.0"},
    ]
    got = calculate_sales_and_avg_discount_by_category(data)
    assert "Office Supplies" in got and " " not in got
    assert got["Office Supplies"] == (100.0, 0.0)

def test_calculate_sales_and_avg_discount_by_category_edge_rounding():
    data = [
        {"Category": "Tech", "Sales": "33.335", "Discount": "0.12345"},
        {"Category": "Tech", "Sales": "66.665", "Discount": "0.12355"},
    ]
    got = calculate_sales_and_avg_discount_by_category(data)
    assert got["Tech"] == (100.0, 0.124)

def test_calculate_sales_and_avg_discount_by_category_edge_missing_discount():
    data = [
        {"Category": "Office Supplies", "Sales": "100", "Discount": ""},
        {"Category": "Office Supplies", "Sales": "200", "Discount": "0.2"},
    ]
    got = calculate_sales_and_avg_discount_by_category(data)
    assert got["Office Supplies"] == (300.0, 0.1) 

def run_all_tests():
    test_calculate_avg_profit_margin_by_region_general_two_regions()
    test_calculate_avg_profit_margin_by_region_edge_zero_sales()
    test_calculate_avg_profit_margin_by_region_edge_negative_profit()
    test_calculate_avg_profit_margin_by_region_edge_messy_strings()
    test_calculate_sales_and_avg_discount_by_category_general_two_cats()
    test_calculate_sales_and_avg_discount_by_category_edge_blank_category()
    test_calculate_sales_and_avg_discount_by_category_edge_rounding()
    test_calculate_sales_and_avg_discount_by_category_edge_missing_discount()
    print("tests passed")

def main():
    data = read_csv_file(DATA_FILENAME)
    profit_margin_by_region = calculate_avg_profit_margin_by_region(data)
    sales_discount_by_category = calculate_sales_and_avg_discount_by_category(data)
    write_results_txt(profit_margin_by_region, "avg_profit_margin_by_region.txt")
    write_category_stats_csv(sales_discount_by_category, "sales_and_discount_by_category.csv")
    print("Average Profit Margin by Region (pct):", profit_margin_by_region)
    print("Total Sales & Average Discount by Category:", sales_discount_by_category)
    print("Files written: avg_profit_margin_by_region.txt, sales_and_discount_by_category.csv")
    

if __name__ == "__main__":
    run_all_tests()
    main()


