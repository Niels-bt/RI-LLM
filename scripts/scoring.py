import re
import statistics


def count_scoring(domains = ["celebrities", "chemical_elements", "constellations", "movies", "sp500"], llms = ["chatgpt", "gemini"]):

    if isinstance(domains, str): domains = [domains]
    if isinstance(llms, str): llms = [llms]

    llm_values = []

    for llm in llms:

        domain_values = []

        for domain in domains:

            entity_values = []

            line_counter = 0
            for entity in open(f"../topics/{domain}/wd_db_{domain}.csv", mode='r', encoding='utf-8'):

                # Only do the first 10 entities
                if line_counter >= 10: break
                line_counter += 1

                # The file_name is computed from the entity file
                entity_elements: list[str] = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', entity)[1::2]
                file_name = entity_elements[1].removeprefix(" ").replace(" ", "_").replace(":", "").lower()

                # We skip tesla and beyoncé because the files are broken
                if file_name != "tesla" and file_name != "beyoncé":

                    label_values = []

                    # The labels are collected in case they should be printed in the console
                    label_labels = []
                    for line in open(f"../topics/{domain}/entities/{file_name}.csv", mode='r', encoding='utf-8'):
                        label_elements: list[str] = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', line)[1::2]
                        if label_elements[0] != "" and label_elements[4] != "":
                            label_labels.append(label_elements[0].replace("\"", "").split(" | ") + label_elements[4].removesuffix("\n").replace("\"", "").split(" | "))

                    label_counter = 0
                    for line in open(f"../topics/{domain}/scoring_{llm}/{file_name}.csv", mode='r', encoding='utf-8'):

                        label_counter += 1

                        label_elements: list[str] = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', line)[1::2]

                        tp = int(label_elements[0])
                        tn = int(label_elements[1])
                        fp = int(label_elements[2])
                        fn = int(label_elements[3])

                        if (tp + fp) != 0: precision = tp / (tp + fp)
                        else: precision = -1
                        if (tp + fn) != 0: recall = tp / (tp + fn)
                        else: recall = -1
                        if (2 * tp + fp + fn) != 0: f1 = (2 * tp) / (2 * tp + fp + fn)
                        else: f1 = -1

                        labels = list(set(label_labels[label_counter-1]))
                        if "" in labels: labels.remove("")
                        scores = (precision, recall, f1)
                        values = (tp, tn, fp, tn)

                        label_values.append((labels, scores, values))

                    precision = []
                    recall = []
                    f1 = []

                    tp = 0
                    tn = 0
                    fp = 0
                    fn = 0

                    for label_value in label_values:

                        if label_value[1][0] != -1: precision.append(label_value[1][0])
                        if label_value[1][1] != -1: recall.append(label_value[1][1])
                        if label_value[1][2] != -1: f1.append(label_value[1][2])

                        tp += label_value[2][0]
                        tn += label_value[2][1]
                        fp += label_value[2][2]
                        fn += label_value[2][3]

                    if not precision: macro_precision = -1
                    else: macro_precision = statistics.fmean(precision)
                    if not recall: macro_recall = -1
                    else: macro_recall = statistics.fmean(recall)
                    if not f1: macro_f1 = -1
                    else: macro_f1 = statistics.fmean(f1)

                    if (tp + fp) == 0: micro_precision = -1
                    else: micro_precision = tp / (tp + fp)
                    if (tp + fn) == 0: micro_recall = -1
                    else: micro_recall = tp / (tp + fn)
                    if (2 * tp + fp + fn) == 0: micro_f1 = -1
                    else: micro_f1 = (2 * tp) / (2 * tp + fp + fn)

                    entity_name = entity_elements[1]
                    macro_values = (macro_precision, macro_recall, macro_f1)
                    micro_values = (micro_precision, micro_recall, micro_f1)
                    values = (tp, tn, fp, tn)

                    entity_values.append((entity_name, macro_values, micro_values, values, label_values))

            precision = []
            recall = []
            f1 = []

            tp = 0
            tn = 0
            fp = 0
            fn = 0

            for entity_value in entity_values:

                if entity_value[1][0] != -1: precision.append(entity_value[1][0])
                if entity_value[1][1] != -1: recall.append(entity_value[1][1])
                if entity_value[1][2] != -1: f1.append(entity_value[1][2])

                tp += entity_value[3][0]
                tn += entity_value[3][1]
                fp += entity_value[3][2]
                fn += entity_value[3][3]

            if not precision: macro_precision = -1
            else: macro_precision = statistics.fmean(precision)
            if not recall: macro_recall = -1
            else: macro_recall = statistics.fmean(recall)
            if not f1: macro_f1 = -1
            else: macro_f1 = statistics.fmean(f1)

            if (tp + fp) == 0: micro_precision = -1
            else: micro_precision = tp / (tp + fp)
            if (tp + fn) == 0: micro_recall = -1
            else: micro_recall = tp / (tp + fn)
            if (2 * tp + fp + fn) == 0: micro_f1 = -1
            else: micro_f1 = (2 * tp) / (2 * tp + fp + fn)

            domain_name = domain
            macro_values = (macro_precision, macro_recall, macro_f1)
            micro_values = (micro_precision, micro_recall, micro_f1)
            values = (tp, tn, fp, tn)

            domain_values.append((domain_name, macro_values, micro_values, values, entity_values))

        precision = []
        recall = []
        f1 = []

        tp = 0
        tn = 0
        fp = 0
        fn = 0

        for domain_value in domain_values:

            if domain_value[1][0] != -1: precision.append(domain_value[1][0])
            if domain_value[1][1] != -1: recall.append(domain_value[1][1])
            if domain_value[1][2] != -1: f1.append(domain_value[1][2])

            tp += domain_value[3][0]
            tn += domain_value[3][1]
            fp += domain_value[3][2]
            fn += domain_value[3][3]

        if not precision: macro_precision = -1
        else: macro_precision = statistics.fmean(precision)
        if not recall: macro_recall = -1
        else: macro_recall = statistics.fmean(recall)
        if not f1: macro_f1 = -1
        else: macro_f1 = statistics.fmean(f1)

        if (tp + fp) == 0: micro_precision = -1
        else: micro_precision = tp / (tp + fp)
        if (tp + fn) == 0: micro_recall = -1
        else: micro_recall = tp / (tp + fn)
        if (2 * tp + fp + fn) == 0: micro_f1 = -1
        else: micro_f1 = (2 * tp) / (2 * tp + fp + fn)

        llm_name = llm
        macro_values = (macro_precision, macro_recall, macro_f1)
        micro_values = (micro_precision, micro_recall, micro_f1)
        values = (tp, tn, fp, tn)

        llm_values.append((llm_name, macro_values, micro_values, values, domain_values))

    return llm_values



def show_scoring(llm_values, show = ["llms", "domains", "entities", "labels"]):

    if isinstance(show, str): show = [show]

    for llm_value in llm_values:

        if "llms" in show:
            print(f"{llm_value[0]}:")
            print(f"        macro-average: precision: {round(llm_value[1][0], 2)}, recall: {round(llm_value[1][1], 2)}, f1: {round(llm_value[1][2], 2)}")
            print(f"        micro-average: precision: {round(llm_value[2][0], 2)}, recall: {round(llm_value[2][1], 2)}, f1: {round(llm_value[2][2], 2)}")

        for domain_value in llm_value[4]:

            if "domains" in show:
                print(f"    {domain_value[0]}:")
                print(f"            macro-average: precision: {round(domain_value[1][0], 2)}, recall: {round(domain_value[1][1], 2)}, f1: {round(domain_value[1][2], 2)}")
                print(f"            micro-average: precision: {round(domain_value[2][0], 2)}, recall: {round(domain_value[2][1], 2)}, f1: {round(domain_value[2][2], 2)}")

            for entity_value in domain_value[4]:

                if "entities" in show:
                    print(f"        {entity_value[0]}:")
                    print(f"                macro-average: precision: {round(entity_value[1][0], 2)}, recall: {round(entity_value[1][1], 2)}, f1: {round(entity_value[1][2], 2)}")
                    print(f"                micro-average: precision: {round(entity_value[2][0], 2)}, recall: {round(entity_value[2][1], 2)}, f1: {round(entity_value[2][2], 2)}")

                for label_value in entity_value[4]:

                    if "labels" in show:
                        print(f"            {" | ".join(label_value[0])}:")
                        print(f"                    precision: {round(label_value[1][0], 2)}, recall: {round(label_value[1][1], 2)}, f1: {round(label_value[1][2], 2)}")



def generate_scoring_files(domains: list[str] = ["celebrities", "chemical_elements", "constellations", "movies", "sp500"], llms: list[str] = ["chatgpt", "gemini"]):

    for domain in domains:

        for llm in llms:

            # Opens the file containing all entity ids
            property_file = open(f"../topics/{domain}/wd_db_{domain}.csv", mode='r', encoding='utf-8')

            line_counter = 0
            for entity in property_file:

                # Only do the first 10 entities
                if line_counter >= 10: break
                line_counter += 1

                # The file_name is computed from the entity file
                file_name: str = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', entity)[1::2][1].removeprefix(" ").replace(" ", "_").replace(":", "").lower()

                # We skip tesla and beyoncé because the files are broken
                if file_name != "tesla" and file_name != "beyoncé":

                    # Collect the labels and values from the llm
                    llm_values = []
                    llm_file = open(f"../topics/{domain}/corrected_{llm}/{file_name}_resolved.csv", mode='r', encoding='utf-8')
                    skip_first_line = True
                    for line in llm_file:
                        if not skip_first_line:
                            elements: list[str] = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', line)[1::2]
                            labels = sorted(elements[0].replace("\"", "").split(" | "))
                            values = (elements[1].removesuffix("\n").replace("\"", "").split(" | "))
                            if "None" in values: values.remove("None")
                            llm_values.append((labels, values))
                        else: skip_first_line = False

                    # Collect the labels and values from the humans
                    human_values = []
                    human_file = open(f"../topics/{domain}/corrected_human/{file_name}.csv", mode='r', encoding='utf-8')
                    for line in human_file:
                        elements: list[str] = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', line)[1::2]
                        labels = sorted(list(set(elements[0].replace("\"", "").split(" | "))))
                        values = elements[1].replace("\"", "").split(" | ")
                        human_values.append((labels, values))

                    # Collect the labels that were matched before the correction
                    matched_values = []
                    matched_file = open(f"../topics/{domain}/entities/{file_name}.csv", mode='r', encoding='utf-8')
                    for line in matched_file:
                        elements: list[str] = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', line)[1::2]
                        labels = sorted(list(set(elements[0].replace("\"", "").split(" | ") + elements[4].removesuffix("\n").replace("\"", "").split(" | "))))
                        values = elements[2].replace("\"", "").split(" | ")
                        all_values = elements[1].replace("\"", "").split(" | ") + elements[3].replace("\"", "").split(" | ")
                        matched_values.append((labels, values, all_values))

                    output_file = open(f"../topics/{domain}/scoring_{llm}/{file_name}.csv", mode='w+', encoding='utf-8')

                    # Has this form: [[[label, ...], [human_value, ...], [llm_value, ...], [matched_value, ...]], [all_value, ...]], ...]
                    merged_values = [[label,
                                      human_value,
                                      {label[0]: llm_value for label, llm_value in llm_values}[label[0]],
                                      {label[0]: matched_value for label, matched_value, all_value in matched_values}[label[0]],
                                      {label[0]: all_value for label, matched_value, all_value in matched_values}[label[0]]
                                      ]
                                     for label, human_value in human_values]

                    for line in merged_values:

                        # format all values
                        line[1] = [human_value.lower().removeprefix(" ").removeprefix(" ").removesuffix(" ").removesuffix(" ").replace("_", " ").replace("-", " ") for human_value in line[1]]
                        line[2] = [llm_value.lower().removeprefix(" ").removeprefix(" ").removesuffix(" ").removesuffix(" ").replace("_", " ").replace("-", " ") for llm_value in line[2]]
                        line[3] = [matched_value.lower().removeprefix(" ").removeprefix(" ").removesuffix(" ").removesuffix(" ").replace("_", " ").replace("-", " ") for matched_value in line[3]]
                        line[4] = [all_value.lower().removeprefix(" ").removeprefix(" ").removesuffix(" ").removesuffix(" ").replace("_", " ").replace("-", " ") for all_value in line[4]]

                        # Remove duplicates
                        line[1] = list(set(line[1]))
                        line[2] = list(set(line[2]))
                        line[3] = list(set(line[3]))
                        line[4] = list(set(line[4]))

                        if "" in line[1]: line[1].remove("")
                        if "" in line[2]: line[2].remove("")
                        if "" in line[3]: line[3].remove("")
                        if "" in line[4]: line[4].remove("")

                        # TN
                        tn = line[4].copy()
                        for all_value in line[4]:
                            if all_value in line[1] or all_value in line[2]: tn.remove(all_value)

                        # TP
                        tp = []
                        for human_value in line[1].copy():
                            if human_value in line[2]:
                                tp.append(human_value)
                                line[1].remove(human_value)
                                line[2].remove(human_value)
                        for matched_value in line[3]:
                            if matched_value in tp:
                                tp.remove(matched_value)

                        # FN
                        fn = line[1]

                        # FP
                        fp = line[2]

                        # write to output file
                        tp_string = f"\"{" | ".join(tp)}\""
                        tn_string = f"\"{" | ".join(tn)}\""
                        fp_string = f"\"{" | ".join(fp)}\""
                        fn_string = f"\"{" | ".join(fn)}\""
                        output_columns = [str(len(tp)), str(len(tn)), str(len(fp)), str(len(fn)), tp_string, tn_string, fp_string, fn_string]
                        output_file.write(",".join(output_columns) + "\n")



if __name__ == "__main__":

    scoring = count_scoring()
    show_scoring(scoring, ["llms", "domains"])