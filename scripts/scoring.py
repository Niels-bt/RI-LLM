import re

def scoring():

    domains = ["celebrities", "chemical_elements", "constellations", "movies", "sp500"]

    for domain in domains:

        # Opens the file containing all entity ids
        property_file = open(f"../topics/{domain}/wd_db_{domain}.csv", mode='r', encoding='utf-8')

        line_counter = 0
        for entity in property_file:

            # Only do the first 10 entities
            if line_counter >= 10: break
            line_counter += 1

            # The file_name is computed from the entity file
            file_name: str = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', entity)[1::2][1].removeprefix(" ").replace(" ", "_").replace(":", "").lower()

            # Collect the labels and values from the llm
            llm_values = [()]
            llm_file = open(f"../topics/{domain}/llm_correct_entities/{file_name}_resolved.csv", mode='r', encoding='utf-8')
            skip_first_line = True
            for line in llm_file:
                if not skip_first_line:
                    elements: list[str] = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', line)[1::2]
                    labels = elements[0].split(" | ").sort()
                    values = elements[1].removesuffix("\n").replace("\"", "").split(" | ").remove("None")
                    llm_values.append((labels, values))
                else: skip_first_line = False

            # Collect the labels and values from the humans
            human_values = [()]
            human_file = open(f"../topics/{domain}/verified/{file_name}.csv", mode='r', encoding='utf-8')
            for line in human_file:
                elements: list[str] = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', line)[1::2]
                labels = list(set(elements[0].split(" | "))).sort()
                values = elements[1].replace("\"", "").split(" | ")
                all_values = elements[5].removesuffix("\n").replace("\"", "").split(" | ")
                human_values.append((labels, values, all_values))

            # Collect the labels that were matched before the correction
            matched_values = [()]
            matched_file = open(f"../topics/{domain}/entities/{file_name}.csv", mode='r', encoding='utf-8')
            for line in matched_file:
                elements: list[str] = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', line)[1::2]
                labels = list(set(elements[0].split(" | ") + elements[4].removesuffix("\n").split(" | "))).sort()
                values = elements[2].replace("\"", "").split(" | ")
                matched_values.append((labels, values))

            output_file = open(f"../topics/{domain}/scoring/{file_name}.csv", mode='w+', encoding='utf-8')

            # Has this form: [[[label, ...], [human_value, ...], [llm_value, ...], [matched_value, ...]], [all_value, ...]], ...]
            merged_values = [[label,
                              human_value,
                              {label: llm_value for label, llm_value in llm_values}[label],
                              {label: matched_value for label, matched_value in matched_values}[label],
                              all_values]
                             for label, human_value, all_values in human_values]

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

                # TN
                for all_value in line[4]:
                    if all_value in line[1]: line[4].remove(all_value)
                    elif all_value in line[2]: line[4].remove(all_value)
                tn = line[4]

                # TP
                tp = []
                for human_value in line[1]:
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
                output_columns = [len(tp), len(tn), len(fp), len(fn), tp_string, tn_string, fp_string, fn_string]
                output_file.write(",".join(output_columns) + "\n")