import os
import time
import openai
import pandas as pd
import re
from openai import OpenAI

client = OpenAI()
# Template 0 was for testing.
PROMPT_TEMPLATE_0 = """
You should not consider any previous prompts or answers. Make your answer for the next prompt independent of any previous chat.
Entity: <entity>
Property: <property>
Values:
<values_list>

Based on your knowledge and reasoning, determine the correct values. Provide the correct values in the format below, encapsulated in square brackets and separated by commas:
Correct Answer: [correct_value1, correct_value2, ...]
"""

PROMPT_TEMPLATE_1 = """
You should not consider any previous prompts or answers. Make your answer for the next prompt independent of any previous chat. 
You are a history facts expert checker, and your role is to validate and correct information in a new dataset generated from fusing two historic data sources: WIKIDATA and DBpedia.
Below are examples of resolved inconsistencies and validations for reference:
1. Entity:  Bon Jovi
Property: label, record label
The fused values: Mercury, Island, Vertigo, Mercury Records, Island Records.
Correct Answer: [Mercury Records, Island Records, Vertigo].
2. Entity: 50 Cent
Property: name, birth name, family name, given name.
The fused values: 50, 50 Cent, Curtis James Jackson III, Jackson, James Curtis.
Correct Answer: [50 Cent, Curtis James Jackson III, Jackson].
3. Entity: Backstreet Boys
Property: genre
The fused values: Teen_pop, Dance-pop, Adult_contemporary_music, Contemporary_R&B, pop music.
Correct Answer: [Pop music, Dance-pop, Teen-pop, adult contemporary, R&B].
Now resolve the following inconsistency based on your knowledge by providing the correct values from the fused values between square brackets [...]:
Entity: <entity>
Property: <property>
The fused values: <values_list>

Provide the answer in the format below:
Correct Answer: [correct_value1, correct_value2, ...]
"""

PROMPT_TEMPLATE_2 = """
You should not consider any previous prompts or answers. Make your answer for the next prompt independent of any previous chat. 
You are a history facts expert checker, and your role is to validate and correct information in a new dataset generated from fusing two historic data sources: WIKIDATA and DBpedia.
Below are examples of resolved inconsistencies and validations for reference:
1. Entity: Boron 
Property: formula, chemical formula 
The fused values: Blue_diamond, B.
Correct Answer: [B].
2. Entity: Zinc
Property: instance of, type.
The fused values: chalcophile element, chemical element, landmark, simple substance.
Correct Answer: [chalcophile element, chemical element, landmark, simple substance].
3. Entity: Nickel
Property: industry
The fused values: Solway Group, Tsingshan_Holding_Group, Xinjiang_Xinxin_Mining_Industry_Company.
Correct Answer: [Solway Group, Tsingshan_Holding_Group, Xinjiang_Xinxin_Mining_Industry_Company].
Now resolve the following inconsistency based on your knowledge by providing the correct values from the fused values between square brackets [...]:
Entity: <entity>
Property: <property>
The fused values: <values_list>

Provide the answer in the format below:
Correct Answer: [correct_value1, correct_value2, ...]
"""

PROMPT_TEMPLATE_3 = """
You should not consider any previous prompts or answers. Make your answer for the next prompt independent of any previous chat. You are a history facts expert checker, and your role is to validate and correct information in a new dataset generated from fusing two historic data sources: WIKIDATA and DBpedia.
Below are examples of resolved inconsistencies (for constellations fused data) and validations for reference:
1. Entity: Aquila 
Property: neighbour Constellations, bordering, shares border with.
The fused values: Serpens Cauda, Serpens Cauda, Hercules_(constellation), Scutum_(constellation), Aquarius_(constellation), Capricornus, Sagitta, Sagittarius, Hercules, Delphinus, Ophiuchus, Scutum, Aquarius, Serpens, Serpens.
Correct Answer: [Sagitta, Hercules, Ophiuchus, Serpens Cauda, Scutum, Sagittarius, Capricornus, Aquarius, Delphinus]
2. Entity: Antlia
Property: symbolism, named after.
The fused values: the Air Pump, air pump.
Correct Answer: [the Air Pump, air pump]
Now resolve the following inconsistency based on your knowledge by providing the correct values from the fused values between square brackets [...]:
Entity: <entity>
Property: <property>
The fused values: <values_list>.
Provide the answer in the format below:
Correct Answer: [correct_value1, correct_value2, ...]
"""

PROMPT_TEMPLATE_4 = """
You should not consider any previous prompts or answers. Make your answer for the next prompt independent of any previous chat. You are a history facts expert checker, and your role is to validate and correct information in a new dataset generated from fusing two historic data sources: WIKIDATA and DBpedia.
Below are examples of resolved inconsistencies (for Movies fused data) and validations for reference:
1. Entity: Dawn of the planet of the apes  
Property: title
The fused values: List_of_Honest_Trailers_episodes, Dawn of the Planet of the Apes.
Correct Answer: [Dawn of the Planet of the Apes]
2. Entity: Guardians of the Galaxy
Property: budget, capital cost.
The fused values: 1.959E8, 2.323E8, 170000000.
Correct Answer: [1.959E8, 2.323E8]
3. Entity: Interstellar
Property: country, country of origin.
The fused values: United States, United Kingdom, United States of America.
Correct Answer: [United States, United Kingdom].
Now resolve the following inconsistency based on your knowledge by providing the correct values from the fused values between square brackets [...]:
Entity: <entity>
Property: <property>.
The fused values: <values_list>.
Provide the answer in the format below:
Correct Answer: [correct_value1, correct_value2, ...]
"""

PROMPT_TEMPLATE_5 = """
You should not consider any previous prompts or answers. Make your answer for the next prompt independent of any previous chat. You are a history facts expert checker, and your role is to validate and correct information in a new dataset generated from fusing two historic data sources: WIKIDATA and DBpedia.
Below are examples of resolved inconsistencies (for S&P 500 fused data) and validations for reference:
1. Entity: Berkshire Hathaway  
Property: location, hqLocationCity, locationCity, headquarters location.
The fused values: Omaha, Kiewit_Plaza, Omaha,_Nebraska, Omaha,_Nebraska.
Correct Answer: [Omaha - Nebraska].
2. Entity: Johnson & Johnson
Property: sponsor.
The fused values: National_Diversity_Awards, It's_Your_Life_(radio_program), baby,The National Diversity Awards.
Correct Answer: [National Diversity Awards, It's Your Life" Radio Program]
3. Entity: Nvidia
Property: parent, parent organization.
The fused values: Mental_Images, Cumulus_Networks, Icera, Mellanox Technologies, 3dfx Interactive, “NVIDIA, Helsinki Oy”, Nvidia Ltd., Ageia.
Correct Answer: [Mellanox Technologies, Cumulus Networks, Ageia, Mental Images, Nvidia Ltd.]
Now resolve the following inconsistency based on your knowledge by providing the correct values from the fused values between square brackets [...]:
Entity: <entity>
Property: <property>.
The fused values: <values_list>.
Provide the answer in the format below:
Correct Answer: [correct_value1, correct_value2, ...]
"""

def construct_prompt(entity, property_, values_list):
    """Constructs the prompt for GPT based on the given inputs."""
    prompt = (
        PROMPT_TEMPLATE_4
        .replace("<entity>", entity)
        .replace("<property>", property_)
        .replace("<values_list>", values_list)
    )
    print(prompt)
    return prompt

def parse_response(response):
    """Extracts the content within brackets or returns 'UNKNOWN'."""
    match = re.search(r'\[(.*?)\]', response)
    return match.group(1).strip() if match else "UNKNOWN"

def get_gpt4_response(prompt, max_retries=5, backoff_factor=1.5):
    """sends a prompt to GPT and retrieves the response with retry logic."""
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4o",
                temperature=0,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except openai.RateLimitError:
            time.sleep(backoff_factor ** attempt)
        except Exception as e:
            print(f"Error: {e}. Retrying...")
    return None

def add_headers_to_csv(file_path):
    """Adds headers to the CSV file, avoiding duplicate headers."""
    headers = [
        "label (Source A)",
        "value (Source A)",
        "value (common)",
        "value (Source B)",
        "label (Source B)"
    ]
    df = pd.read_csv(file_path, header=None)
    if df.iloc[0].tolist() != headers:  # check if headers are already present
        df.columns = headers
        df.to_csv(file_path, index=False)

def resolve_inconsistencies(input_csv_path, output_csv_path, entity_name):
    """Reads the dataset, resolves inconsistencies, and saves the updated dataset."""
    df = pd.read_csv(input_csv_path)

    # group values by label
    resolved_values = []

    for idx, row in df.iterrows():
        label_a = row['label (Source A)']
        value_a = str(row['value (Source A)']).strip() if pd.notnull(row['value (Source A)']) else None
        value_common = str(row['value (common)']).strip() if pd.notnull(row['value (common)']) else None
        label_b = row['label (Source B)']
        value_b = str(row['value (Source B)']).strip() if pd.notnull(row['value (Source B)']) else None

        # process rows with a value in the 3ed column directly
        if value_common:
            combined_label = f"{label_a} | {label_b}".strip("|")
            resolved_set = set(map(str.strip, value_common.split("|")))

            # if additional values exist in Source A or B, send them to LLM
            if value_a or value_b:
                labels_combined = set(map(str.strip, str(label_a).split("|") + str(label_b).split("|")))
                values_combined = set(map(str.strip, str(value_a).split("|") + str(value_b).split("|")))

                # prepare values for the prompt
                values_list = "\n".join([f"- {v}" for v in sorted(values_combined)])
                combined_label = " | ".join(sorted(labels_combined))

                prompt = construct_prompt(entity_name, combined_label, values_list)
                response = get_gpt4_response(prompt)

                if response is not None:
                    resolved = parse_response(response)
                    resolved_set.update(map(str.strip, resolved.split(",")))

            resolved_values.append({
                "label": combined_label,
                "correct values": " | ".join(sorted(resolved_set))
            })
            print(f"Resolved: {combined_label} -> {' | '.join(sorted(resolved_set))}")

        # process rows with non-empty labels in both Source A and B, without a common value
        elif pd.notnull(label_a) and pd.notnull(label_b) and (value_a or value_b):
            labels_combined = set(map(str.strip, str(label_a).split("|") + str(label_b).split("|")))
            values_combined = set(map(str.strip, str(value_a).split("|") + str(value_b).split("|")))

            values_list = "\n".join([f"- {v}" for v in sorted(values_combined)])
            combined_label = " | ".join(sorted(labels_combined))

            prompt = construct_prompt(entity_name, combined_label, values_list)
            response = get_gpt4_response(prompt)

            resolved_set = set()
            if response is not None:
                resolved = parse_response(response)
                resolved_set.update(map(str.strip, resolved.split(",")))

            resolved_values.append({
                "label": combined_label,
                "correct values": " | ".join(sorted(resolved_set))
            })
            print(f"Resolved: {combined_label} -> {' | '.join(sorted(resolved_set))}")

    # save the resolved dataset
    resolved_df = pd.DataFrame(resolved_values)
    resolved_df.to_csv(output_csv_path, index=False)
    print(f"Resolved dataset saved to {output_csv_path}")

def process_entities(entities_dir, output_dir):
    """Processes all CSV files in the entities directory."""
    for file_name in os.listdir(entities_dir):
        if file_name.endswith(".csv"):
            input_file_path = os.path.join(entities_dir, file_name)
            output_file_path = os.path.join(output_dir, file_name.replace(".csv", "_resolved.csv"))

            # Skip processing if resolved file already exists
            if os.path.exists(output_file_path):
                print(f"Resolved file already exists for {file_name}. Skipping processing.")
                continue

            # extract entity name from the file name
            entity_name = file_name.replace("_", " ").replace(".csv", "")

            # add headers
            add_headers_to_csv(input_file_path)

            resolve_inconsistencies(input_file_path, output_file_path, entity_name)

if __name__ == "__main__":
    entities_dir = "../topics/movies/entities"
    output_dir = "../topics/movies/llm_correct_entities"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    process_entities(entities_dir, output_dir)
