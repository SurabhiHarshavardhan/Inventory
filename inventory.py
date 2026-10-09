import csv
import os
from datetime import datetime

FILE_NAME = "inventory.csv"

FIELDS = [
    "product_id",
    "name",
    "category",
    "quantity",
    "price",
    "reorder_level",
    "last_updated"
]


def load_products():
    """Load products from CSV file."""
    products = []

    if not os.path.exists(FILE_NAME):
        return products

    try:
        with open(FILE_NAME, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                if not row.get("product_id"):
                    continue

                try:
                    row["quantity"] = int(row["quantity"])
                    row["price"] = float(row["price"])
                    row["reorder_level"] = int(row["reorder_level"])
                    products.append(row)
                except (ValueError, KeyError):
                    print("Warning: Skipping an invalid product record.")

    except OSError as error:
        print(f"Error loading inventory: {error}")

    return products


def save_products(products):
    """Save all products to CSV file."""
    try:
        with open(FILE_NAME, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(products)

        return True

    except OSError as error:
        print(f"Error saving inventory: {error}")
        return False


def get_product_by_id(products, product_id):
    """Find a product using its ID."""
    for product in products:
        if product["product_id"].lower() == product_id.lower():
            return product

    return None


def get_non_empty_input(message):
    """Read a non-empty string."""
    while True:
        value = input(message).strip()

        if value:
            return value

        print("Input cannot be empty.")


def get_integer(message, minimum=0):
    """Read and validate an integer."""
    while True:
        try:
            value = int(input(message))

            if value < minimum:
                print(f"Enter a value of at least {minimum}.")
                continue

            return value

        except ValueError:
            print("Please enter a valid whole number.")


def get_price(message):
    """Read and validate a non-negative price."""
    while True:
        try:
            value = float(input(message))

            if value < 0:
                print("Price cannot be negative.")
                continue

            return value

        except ValueError:
            print("Please enter a valid price.")


def add_product(products):
    """Add a new product."""
    print("\n--- Add Product ---")

    product_id = get_non_empty_input("Product ID: ")

    if get_product_by_id(products, product_id):
        print("Product ID already exists.")
        return

    name = get_non_empty_input("Product name: ")
    category = get_non_empty_input("Category: ")
    quantity = get_integer("Initial quantity: ")
    price = get_price("Price per unit: ")
    reorder_level = get_integer("Low-stock threshold: ")

    product = {
        "product_id": product_id,
        "name": name,
        "category": category,
        "quantity": quantity,
        "price": price,
        "reorder_level": reorder_level,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    products.append(product)

    if save_products(products):
        print("Product added successfully.")


def display_products(products):
    """Display products in a table."""
    if not products:
        print("\nNo products found.")
        return

    print("\n" + "-" * 112)
    print(
        f"{'ID':<12}{'Name':<22}{'Category':<17}"
        f"{'Qty':>7}{'Price':>12}{'Stock Value':>15}"
        f"{'Reorder':>10}"
    )
    print("-" * 112)

    for product in products:
        stock_value = product["quantity"] * product["price"]

        print(
            f"{product['product_id']:<12}"
            f"{product['name'][:20]:<22}"
            f"{product['category'][:15]:<17}"
            f"{product['quantity']:>7}"
            f"{product['price']:>12.2f}"
            f"{stock_value:>15.2f}"
            f"{product['reorder_level']:>10}"
        )

    print("-" * 112)


def view_products(products):
    """Show all products."""
    print("\n--- All Products ---")
    display_products(products)


def search_product(products):
    """Search by product ID or product name."""
    print("\n--- Search Product ---")
    query = get_non_empty_input("Enter product ID or name: ").lower()

    matches = [
        product for product in products
        if query in product["product_id"].lower()
        or query in product["name"].lower()
    ]

    display_products(matches)


def update_product(products):
    """Update a product's details."""
    print("\n--- Update Product ---")

    product_id = get_non_empty_input("Enter product ID: ")
    product = get_product_by_id(products, product_id)

    if product is None:
        print("Product not found.")
        return

    print("Press Enter to keep the current value.")

    new_name = input(
        f"Name [{product['name']}]: "
    ).strip()

    new_category = input(
        f"Category [{product['category']}]: "
    ).strip()

    if new_name:
        product["name"] = new_name

    if new_category:
        product["category"] = new_category

    product["quantity"] = get_integer(
        f"New quantity [{product['quantity']}]: "
    )

    product["price"] = get_price(
        f"New unit price [{product['price']:.2f}]: "
    )

    product["reorder_level"] = get_integer(
        f"New reorder level [{product['reorder_level']}]: "
    )

    product["last_updated"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    if save_products(products):
        print("Product updated successfully.")


def delete_product(products):
    """Delete a product."""
    print("\n--- Delete Product ---")

    product_id = get_non_empty_input("Enter product ID: ")
    product = get_product_by_id(products, product_id)

    if product is None:
        print("Product not found.")
        return

    print(
        f"Selected: {product['name']} "
        f"(ID: {product['product_id']})"
    )

    confirm = input("Are you sure you want to delete it? (y/n): ")

    if confirm.strip().lower() != "y":
        print("Deletion cancelled.")
        return

    products.remove(product)

    if save_products(products):
        print("Product deleted successfully.")


def low_stock_report(products):
    """Show products that need restocking."""
    print("\n--- Low Stock Report ---")

    low_stock = [
        product for product in products
        if product["quantity"] <= product["reorder_level"]
    ]

    if not low_stock:
        print("No low-stock products.")
        return

    display_products(low_stock)
    print(f"Products requiring attention: {len(low_stock)}")


def inventory_summary(products):
    """Calculate overall inventory statistics."""
    print("\n--- Inventory Summary ---")

    total_products = len(products)
    total_units = sum(p["quantity"] for p in products)
    total_value = sum(
        p["quantity"] * p["price"] for p in products
    )

    low_stock_count = sum(
        1 for p in products
        if p["quantity"] <= p["reorder_level"]
    )

    print(f"Unique products       : {total_products}")
    print(f"Total units in stock  : {total_units}")
    print(f"Total inventory value : {total_value:.2f}")
    print(f"Low-stock products    : {low_stock_count}")


def main():
    """Main menu."""
    products = load_products()

    print("=" * 45)
    print("   INVENTORY MANAGEMENT SYSTEM")
    print("=" * 45)
    print(f"Loaded {len(products)} product(s).")

    while True:
        print("\n========== MAIN MENU ==========")
        print("1. Add product")
        print("2. View all products")
        print("3. Search product")
        print("4. Update product")
        print("5. Delete product")
        print("6. Low-stock report")
        print("7. Inventory summary")
        print("8. Save inventory")
        print("0. Exit")
        print("===============================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_product(products)

        elif choice == "2":
            view_products(products)

        elif choice == "3":
            search_product(products)

        elif choice == "4":
            update_product(products)

        elif choice == "5":
            delete_product(products)

        elif choice == "6":
            low_stock_report(products)

        elif choice == "7":
            inventory_summary(products)

        elif choice == "8":
            if save_products(products):
                print("Inventory saved successfully.")

        elif choice == "0":
            if save_products(products):
                print("Inventory saved. Goodbye!")
            else:
                print("Warning: Inventory could not be saved.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()