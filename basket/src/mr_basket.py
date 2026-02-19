#! /usr/bin/env python

from mrjob.job import MRJob
from mrjob.step import MRStep
from itertools import combinations


class MRBasket(MRJob):
    """
    A class to count item co-occurrence in shopping baskets
    """

    # ----------------------------
    # STEP 1: Build baskets
    # ----------------------------

    def mapper_get_session_items(self, _, line):
        # input format:
        # user_id, date, item

        parts = line.strip().split(",")

        if len(parts) != 3:
            return

        user_id = parts[0].strip()
        date = parts[1].strip()
        item = parts[2].strip()

        # key = (user_id, date)
        yield (user_id, date), item

    def reducer_build_baskets(self, key, items):
        # key = (user_id, date)
        # items = all items bought that day by that user

        # remove duplicates within basket
        unique_items = list(set(items))

        yield key, unique_items


    # ----------------------------
    # STEP 2: Generate & count pairs
    # ----------------------------

    def mapper_generate_pairs(self, key, items):
        # key = (user_id, date)
        # items = list of items in basket

        # sort to make combinations deterministic
        items = sorted(items)

        # generate unordered combinations
        for item1, item2 in combinations(items, 2):
            # emit both directions
            yield item1, item2
            yield item2, item1

    def reducer_count_pairs(self, item1, item2_list):
        # count occurrences
        counts = {}

        for item2 in item2_list:
            counts[item2] = counts.get(item2, 0) + 1

        for item2, count in counts.items():
            yield (item1, item2), count


    # ----------------------------
    # STEP 3: Find top co-occurring item
    # ----------------------------

    def mapper_prepare_top(self, pair, count):
        # pair = (item1, item2)
        item1, item2 = pair
        yield item1, (item2, count)

    def reducer_find_top(self, item1, values):
        max_item = None
        max_count = 0

        for item2, count in values:
            if count > max_count:
                max_item = item2
                max_count = count

        if max_item is not None:
            yield item1, [max_item, max_count]


    # ----------------------------
    # Define pipeline steps
    # ----------------------------

    def steps(self):
        return [
            MRStep(
                mapper=self.mapper_get_session_items,
                reducer=self.reducer_build_baskets
            ),
            MRStep(
                mapper=self.mapper_generate_pairs,
                reducer=self.reducer_count_pairs
            ),
            MRStep(
                mapper=self.mapper_prepare_top,
                reducer=self.reducer_find_top
            ),
        ]


if __name__ == "__main__":
    MRBasket.run()
