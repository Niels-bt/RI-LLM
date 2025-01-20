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
            for line in llm_file:
                elements: list[str] = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', line)[1::2]
                labels = elements[0].split(" | ")
                values = elements[1].removesuffix("\n").split(" | ").remove("None")
                llm_values.append((labels, values))

            # Collect the labels and values from the humans
            human_values = [()]
            human_file = open(f"../topics/{domain}/merge/{file_name}.csv", mode='r', encoding='utf-8')
            for line in human_file:
                elements: list[str] = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', line)[1::2]
                labels = elements[0].split(" | ")
                values = elements[1].split(" | ")
                all_values = elements[2].split(" | ")
                human_values.append((labels, values, all_values))

            output_file = open(f"../topics/{domain}/scoring/{file_name}.csv", mode='w+', encoding='utf-8')

            # Has this form: [[[label, ...], [human_value, ...], [llm_value, ...], [all_value, ...]], ...]
            merged_values = [[label, human_value, {label: llm_value for label, llm_value in llm_values}[label], all_values] for label, human_value, all_values in human_values]
            for line in merged_values:

                # Apply .lower() and remove underscore and minus from all values
                line[1] = [human_value.lower().replace("_", " ").replace("-", " ") for human_value in line[1]]
                line[2] = [llm_value.lower().replace("_", " ").replace("-", " ") for llm_value in line[2]]
                line[3] = [all_value.lower().replace("_", " ").replace("-", " ") for all_value in line[3]]

                # Remove duplicates
                line[1] = list(set(line[1]))
                line[2] = list(set(line[2]))
                line[3] = list(set(line[3]))

                # TN
                for all_value in line[3]:
                    if all_value in line[1]: line[3].remove(all_value)
                    elif all_value in line[2]: line[3].remove(all_value)
                tn = line[3]

                # TP
                tp = []
                for human_value in line[1]:
                    if human_value in line[2]:
                        tp.append(human_value)
                        line[1].remove(human_value)
                        line[2].remove(human_value)

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