from similarity_engine import compare_documents


def group_documents(all_documents, threshold=75):

    groups = []
    used = set()

    for i in range(len(all_documents)):

        if i in used:
            continue

        current_group = [all_documents[i]["filename"]]
        used.add(i)

        for j in range(i + 1, len(all_documents)):

            if j in used:
                continue

            score = compare_documents(
                all_documents[i]["fingerprint"],
                all_documents[j]["fingerprint"]
            )

            # NEW: Print every comparison
            print(
                f'{all_documents[i]["filename"]} <--> {all_documents[j]["filename"]} = {score}%'
            )

            if score >= threshold:

                # NEW: Print when documents are grouped
                print(">>> GROUPED <<<")

                current_group.append(all_documents[j]["filename"])
                used.add(j)

        groups.append(current_group)

    return groups