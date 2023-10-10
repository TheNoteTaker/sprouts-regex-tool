import re
from typing import List, Tuple, Union


def read_file(file_path: str) -> List[str]:
    """Read the content of a file and return its lines."""
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []


def print_output(title: str, content: List[str], total: int,
                 pattern: Union[str, None] = None):
    """Print the output in the desired format with title, content, total, and an optional regex pattern."""
    print(title)
    for item in content:
        print(item)
    print("--------------------")
    print(f"Total: {total}")
    if pattern:
        print(f"RegexSearch Pattern:\n{pattern}")

def get_amounts_and_vendors(lines: List[str]):
    """Parse and print items and their respective amounts. Exclude duplicates and sort numerically."""
    AMOUNT = r'\d{4,5}(?!\.)|\d+\.00'
    tuples_list = []
    lines_str = " ".join(lines)
    amounts = re.findall(AMOUNT, lines_str)

    for i in range(0, len(amounts), 2):
        item = amounts[i].strip()
        number = amounts[i + 1].strip()
        tuples_list.append((item, number))

    tuples_list = sorted(set(tuples_list),
                         key=lambda x: int(x[0]))  # Remove duplicates and sort

    max_num_length = 0
    for num in tuples_list:
        num = len(num[1])
        if max_num_length < num:
            max_num_length = num

    max_item_length = 0
    for item in tuples_list:
        num = len(item[0])
        if max_item_length < num:
            max_item_length = num

    for item, number in tuples_list:
        print(f"{item:0>{max_item_length}} | {number:0>{max_num_length}}")

    print(f"\nTotal: {len(tuples_list)}")


def get_duplicates(lines: List[str]) -> Tuple[List[str], List[str], List[str]]:
    """Identify duplicates from the provided lines and return items, non-duplicates, and duplicates."""
    duplicates = {}
    for item in lines:
        base_item = item[:4]
        if base_item not in duplicates:
            duplicates[base_item] = 1
        else:
            duplicates[base_item] += 1

    items = sorted(duplicates.keys(), key=lambda x: int(x))
    non_duplicates = [k for k, v in duplicates.items() if v == 1]
    duplicate_items = [k for k, v in duplicates.items() if v > 1]

    return items, non_duplicates, duplicate_items


def generate_markdown_table(lines: List[str], use_scan: bool) -> str:
    """Generate a markdown table based on the provided lines and include totals for each column."""
    segmented_lists = segment_lists(lines)
    unique_items = sorted(set(lines))

    list_names = ["Values"]
    if use_scan:
        list_names.append("Scan 0")
        list_names.extend(
            [f"List {i + 1}" for i in range(len(segmented_lists) - 1)])
    else:
        list_names.extend(
            [f"List {i + 1}" for i in range(len(segmented_lists))])

    max_width = max(max(len(item) for item in unique_items),
                    6)  # Ensure at least 6 characters for padding
    table = [" | ".join(name.ljust(max_width) for name in list_names)]
    table.append(" | ".join(["-" * max_width] * len(list_names)))

    for item in unique_items:
        row = [item.ljust(max_width)]
        for segment in segmented_lists:
            if item in segment:
                content = item
            elif use_scan and item not in [one for two in segmented_lists[1:]
                                           for one in two]:
                content = "////"
            else:
                content = "----"
            row.append(content.ljust(max_width))
        table.append(" | ".join(row))

    totals = [f"\nValues Total: {len(unique_items)}"]
    for i, segment in enumerate(segmented_lists):
        totals.append(f"{list_names[i + 1]} Total: {len(set(segment))}")
    table.extend(totals)

    return "\n".join(table)


def segment_lists(lines: List[str]) -> List[List[str]]:
    """Segment the provided list of lines based on the criteria: when the next number in the file is less than the previous number, it indicates a new segment."""
    segmented_lists = []
    current_segment = []
    last_item = None

    for item in lines:
        if last_item and int(item) < int(last_item):
            segmented_lists.append(current_segment)
            current_segment = []
        current_segment.append(item)
        last_item = item

    segmented_lists.append(current_segment)
    return segmented_lists


def get_duplicates_with_table(lines: List[str], use_scan: bool):
    """Generate markdown table and print duplicates."""
    items, non_duplicates, duplicates = get_duplicates(lines)
    items_regex = "^(?:" + "|".join(items) + ")$"
    non_duplicates_regex = "^(?:" + "|".join(non_duplicates) + ")$"
    duplicates_regex = "^(?:" + "|".join(duplicates) + ")$"

    print_output("Items\n====================", items, len(items), items_regex)
    print_output("\nDuplicates\n====================", duplicates,
                 len(duplicates), duplicates_regex)
    print_output("\nNon-duplicates (Difference)\n====================",
                 non_duplicates, len(non_duplicates), non_duplicates_regex)

    print("\n\nMarkdown Table\n====================")
    table = generate_markdown_table(lines, use_scan)
    print(table)

    print("\nRegexSearch Patterns\n====================")
    unique_items = sorted(set(lines))
    pattern = f"Values Total: ^(?:{'|'.join(unique_items)})$"
    print(pattern)
    pattern = ""

    segmented_lists = segment_lists(lines)

    # Overlap search values
    if not use_scan:
        search_values = " ".join(
            sorted([num for segment in segmented_lists for num in segment]))
    else:
        search_values = " ".join(
            sorted([num for segment in segmented_lists[1:] for num in segment]))

    # Overlap
    for segment in segmented_lists[1:] if use_scan else segmented_lists:
        pattern = "^(?:"
        segment = sorted(set(segment))
        for item in segment:
            if search_values.count(item) > 1:
                pattern += f"{item}|"

    pattern = f"{pattern[:-1]})$"
    if len(pattern) > 5:
        print(f"\nList Overlap: {pattern}")

    if use_scan:
        # Scan 0
        pattern = "^(?:" + "|".join(sorted(set(segmented_lists[0]))) + ")$"
        print(f"\nScan 0: {pattern}")

        for idx, segment in enumerate(segmented_lists[1:]):
            pattern = "^(?:" + "|".join(
                sorted(set([item[:4] for item in segment]))) + ")$"
            print(f"\nList {idx + 1}:", pattern)
    else:
        for idx, segment in enumerate(segmented_lists):
            pattern = "^(?:" + "|".join(
                sorted(set([item[:4] for item in segment]))) + ")$"
            print(f"\nList {idx + 1}:", pattern)


def get_vendor_and_suffix(lines: List[str]):
    """Parse and print vendors with and without a suffix."""
    PREFIX = r"^\d{4}[^\d]\d+$"
    NO_PREFIX = r"^\d{4}$"

    prefix = []
    no_prefix = []

    for item in lines:
        if re.match(NO_PREFIX, item):
            no_prefix.append(item)
        elif re.match(PREFIX, item):
            prefix.append(item)

    sections = [("=====Suffix=====", prefix),
                ("\n\n=====No Suffix=====", no_prefix),
                ("\n\n=====All Items=====", [num[:4] for num in lines if num])]
    for title, content in sections:
        regex_str = "^(?:" + "|".join(content) + ")$"
        print_output(title, content, len(content), regex_str)


def main():
    """Main function to drive the program."""
    choice = input(
        "Duplicates search [1] | Amounts + Vendor [2] | Vendor + Suffix [3]:\n> ")
    print()
    lines = read_file('items.txt')

    if choice == "1":
        use_scan = input("Use scan column [Y/n]?\n>").casefold() not in ["n",
                                                                         "no",
                                                                         "0"]
        print()
        get_duplicates_with_table(lines, use_scan)
    elif choice == "2":
        get_amounts_and_vendors(lines)
    elif choice == "3":
        get_vendor_and_suffix(lines)
    else:
        print("Invalid choice!")


main()
