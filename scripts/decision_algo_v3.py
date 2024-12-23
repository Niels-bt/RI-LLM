import os
import time
import openai
import pandas as pd
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-api-key"))

PROMPT_TEMPLATE = """
You should not consider any previous prompts or answers. Make your answer for the next prompt independent of any previous chat.
Entity: <entity>
Property: <property>
Values:
<values_list>

Based on your knowledge and reasoning, determine the correct values. Provide the correct values in the format below, encapsulated in square brackets and separated by commas:
Correct Answer: [correct_value1, correct_value2, ...]
"""

def construct_prompt(entity, property_, values_list):
    """Constructs the prompt for GPT based on the given inputs."""
    prompt = (
        PROMPT_TEMPLATE
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
    entities_dir = "../topics/celebrities/entities"
    output_dir = "../topics/celebrities/llm_correct_entities"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    process_entities(entities_dir, output_dir)
