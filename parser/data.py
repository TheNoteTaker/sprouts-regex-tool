import re


class DataParser:

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def segment_monotonic(lines: list[str]) -> list[list[str]]:
        """
        Segment a `list` of strings into monotonic `list`s.

        When something is monotonic, it either increases or decreases.
        This method will segment a `list` of strings based on a strictly
        positive trend. When a value following a previous value is less
        than the previous value, it indicates a new segment.

        Args:
            lines: A `list` of strings.

        Returns:
            A `list` of positively monotonic `list`s.
        """
        # Create a list of lists
        segmented_lines = []
        current_segment = []
        last_item = None

        for value in lines:
            try:
                if last_item and int(value) < int(last_item):
                    # The current value is less than the last value,
                    # indicating a new segment
                    segmented_lines.append(current_segment)
                    current_segment = []
            except ValueError as e:
                # The value is not an integer, so it cannot be compared
                # to the last value. This indicates a new segment.
                segmented_lines.append(current_segment)
                current_segment = []

            # Add the value to the current segment and update the last item
            current_segment.append(value)
            last_item = value

        # Add the last segment to the list of segments
        segmented_lines.append(current_segment)

        # Return the segmented lines
        return segmented_lines

    @staticmethod
    def segment_duplicates(lines: list[str],
                           ignore: str = "|") -> list[list[str]]:
        """
        Segment a `list` of strings based on duplicates.

        Every time a duplicate is found, a new segment is created.

        Args:
            lines: A `list` of strings.
            ignore: Characters to be ignored when looking for
                duplicates. These will not be included in the
                segments.

        Returns:
            A `list` of `list`s of strings. Each inner `list` will be a
            segment containing no duplicates.
        """
        segments = []
        current_segment = []

        # Iterate through the lines and identify duplicates
        for line in lines:
            # Check if line is a character to ignore
            if line in ignore:
                # Ignore the line
                continue

            if line in current_segment:
                # The line is a duplicate, so start a new segment
                segments.append(current_segment)
                current_segment = []

            # Add the line to the current segment
            current_segment.append(line)

        # Add the last segment to the list of segments
        segments.append(current_segment)

        # Return the segments
        return segments

    @staticmethod
    def segment_separator(data: list[str], sep: str = "|") -> list[list[str]]:
        """Segment a `list` of strings based on a separator."""
        segment = []
        segments = []
        for item in data:
            if item in sep:
                # The item is a separator, so start a new segment
                segments.append(segment)
                segment = []

                # Skip the separator
                continue

            segment.append(item)

        # Add the last segment to the list of segments
        if segment:
            segments.append(segment)

        # Return the segments
        return segments

    @staticmethod
    def pad_list(data: list,
                 pad: str = "0",
                 justify: str = "l",
                 max_length: int = 0,
                 remove: str = "",
                 ignore: str = ""
                 ) -> list:
        """
        Pad a `list` of strings with a specified character.

        Pads a `list` of strings with a specified character until each
        item in the `list` is the same length as the longest item in the
        `list`. The `justify` parameter determines whether the padding
        is added to the left, right, or both sides of the item.

        Args:
            data: A `list` of strings.
            pad: The character to use for padding.
            justify: The justification for the padding. Valid values are
                "l" (left), "r" (right), and "c" (center).
            max_length: The maximum `str` length of the items in the
                list.
            remove: A `str` of characters to filter out of the list.
            ignore: A `str` of characters to ignore when filtering the
                list.

        Returns:
            A `list` of strings with each item padded to the same length.
        """
        # Sanitize the data
        data = [item for item in data if item not in remove]

        try:
            # Convert the data to a list of integers to remove leading zeros
            data = DataParser.intify(data)
        except ValueError:
            # A non-integer value was found in the list. Skip intifying.
            pass

        # Get max length of the list
        data = DataParser.stringify(data)
        max_length = (max([len(item) for item in data])
                      if not max_length else max_length)

        # Set justify char
        if justify in ["l", "left"]:
            justify = ">"
        elif justify in ["r", "right"]:
            justify = "<"
        elif justify in ["c", "center"]:
            justify = "^"
        else:
            raise ValueError(f"Invalid `justify` value: {justify}")

        # Pad each item in the list with `pad` until it is the same length
        # as the longest item. `justify` determines whether the padding
        # is added to the left or right of the item.
        ret = []
        for item in data:
            if item not in ignore:
                ret.append(f"{item:{pad}{justify}{max_length}}")
            else:
                ret.append(f"{item:{item[0]}{justify}{max_length}}")

        return ret

    @staticmethod
    def remove_leading(data: list, remove: str = "0") -> list[str]:
        """
        Remove padding from a `list` of strings.

        Args:
            data: A `list` of strings.
            remove: One or more characters to remove from each item in `data`.

        Returns:
            A `list` of strings with the padding removed.
        """
        for char in remove:
            data = [item.lstrip(char) for item in data]

        return data

    @staticmethod
    def stringify(data: list) -> list[str]:
        """
        Convert a `list` of items to a `list` of strings.

        Args:
            data: A `list` of items.

        Returns:
            A `list` of strings.
        """
        return [str(item) for item in data]

    @staticmethod
    def intify(data: list) -> list[int]:
        """
        Convert a `list` of items to a `list` of integers.

        Args:
            data: A `list` of items.

        Returns:
            A `list` of integers.
        """
        return [int(item) for item in data]

    @staticmethod
    def _flatten(data: any) -> tuple[list, int]:
        """Helper method for `flatten`, flattens a `list` of lists."""
        result = 1
        try:
            # Flatten the list one level
            if isinstance(data[0], list):
                # The first item in the list is a list, so flatten it
                data = [item for sublist in data for item in sublist]
            else:
                result = -1
        except (IndexError, TypeError):
            # There are no more sublists to flatten
            result = -1

        return data, result

    @staticmethod
    def flatten(data: any, level: int = -1) -> list:
        """
        Flatten a `list` of lists recursively up to `level` times.

        Args:
            data: A `list` of lists.
            level: The number of levels to flatten. If set to -1, all
                sublists will be flattened.

        Returns:
            A `list` where all sublists up to `level` are flattened.
        """
        if level == -1:
            while True:
                # Flatten the list until there are no more sublists
                data, result = DataParser._flatten(data)

                if result == -1:
                    # There are no more sublists to flatten
                    break
        else:
            # Flatten the list `level` times
            for _ in range(level):
                data, _ = DataParser._flatten(data)

        return data

    @staticmethod
    def unique_list(data: list,
                    sort: bool = True,
                    remove: str = ""
                    ) -> list:
        """
        Return a list of unique items from the provided list.
        
        Returns a list of unique items from the provided list. If `sort`
        is True, the list will be sorted before returning. If `ignore`
        is provided, the items in the list will be filtered before
        returning.
        
        Args:
            data: A `list` of items.
            sort: Whether to sort the list before returning.
            remove: A string of characters to ignore when filtering the
                list.

        Returns:
            A `list` of unique items from the provided list, optionally
            sorted and filtered.
        """
        for char in remove:
            # Remove ignored items from the list
            data = [item for item in data if item != char]

        # Remove duplicates from the list if `sort` is True
        return sorted(set(data)) if sort else list(set(data))

    @staticmethod
    def get_max_str_length(data: any) -> int:
        """Get the length of the longest string in a `list` of strings."""
        data = DataParser.flatten(DataParser.stringify(data))
        return max([len(item) for item in data])


if __name__ == "__main__":
    print(
        DataParser.pad_list(["1", "2", "3", "4", "500"], pad="0", justify="l"))
    print(DataParser.remove_leading(["0001", "0002", "0003", "0004", "0500"],
                                    remove="0"))
    print(DataParser.flatten([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
    # 3 level flatten
    print(DataParser.flatten([[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                              [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                              [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
                              ], level=1))
