import os
import time
import pandas as pd
import re
from typing import Optional

from openai import OpenAI

client = OpenAI()

PROMPT_TEMPLATE = """
You should not consider any previous prompts or answers. Make your answer for the next prompt independent of any previous chat. You are a data engineer, and based on your knowledge, you should determine the correct answer.

A new dataset was generated from fusing two historic data sources: WIKIDATA and DBpedia (both likely contain correct information). An inconsistency was revealed due to conflicting information from the two sources about <entity>'s <property>:

- Source A (DBpedia): <source_a>
- Source B (Wikidata): <source_b>

Based on your knowledge and reasoning, determine the correct value that should be added to the new fused dataset. Explain your reasoning and provide the correct answer in the following format and make sure to encapsulate the correct answer between square bracket as follows:

Correct Answer: [correct_value]

Add the correct value only if you are sure of it. If you are unsure, provide: [UNKNOWN].
"""

PROMPT_TEMPLATE2 = """
You should not consider any previous prompts or answers. Make your answer for the next prompt independent of any previous chat.
You are a history facts expert checker, and your role is to validate and correct information in a new dataset generated from
fusing two historic data sources: WIKIDATA and DBpedia. 
Below are examples of resolved inconsistencies and validations for reference:
Entity: <example_entity1>
Property: <example_property1>
Source A value (DBpedia): <example_value1>
Source B value (Wikidata): <example_value2>
Correct Answer: [.....]
Reasoning: ….
Entity: <example_entity2>
Property: <example_property2>
Source A value (DBpedia): <example_value1>
Source B value (Wikidata): <example_value2>
Correct Answer: [.....]
Reasoning: ….
Entity: <example_entity3>
Property: <example_property3>
Source A value (DBpedia): <example_value1>
Source B value (Wikidata): <example_value2>
Correct Answer: [.....]
Reasoning: ….

Now resolve the following inconsistency:
Entity: <entity>
Property: <property>
Source A value (DBpedia): <value1>
Source B (Wikidata): <value2>
Correct Answer: [.....]
Reasoning: ….
Based on your knowledge and reasoning, determine the correct value. Provide the answer in the format below:
Correct Answer: [...]
Reasoning: Explain your reasoning here.
"""


def construct_prompt(entity: str, property_: str, source_a: str, source_b: str) -> str:
    return PROMPT_TEMPLATE.replace("<entity>", entity) \
        .replace("<property>", property_) \
        .replace("<source_a>", source_a) \
        .replace("<source_b>", source_b)


def parse_response(response: str) -> str:
    """Extracts the content within brackets or returns 'UNKNOWN'."""
    match = re.search(r'\[(.*?)\]', response)
    if match:
        return match.group(1).strip()
    else:
        return "UNKNOWN"


def get_gpt4_response(prompt: str, max_retries: int = 5, backoff_factor: float = 1.5) -> Optional[str]:
    """Sends a prompt to the GPT-4 model and retrieves the response with retry logic."""
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4o",
                temperature=0,
                max_tokens=1000
            )
            print(response.choices[0].message.content.strip())
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error: {e}. Retrying in {backoff_factor ** attempt} seconds...")
            time.sleep(backoff_factor ** attempt)
    print("Max retries exceeded. Skipping this prompt.")
    return None


def resolve_inconsistencies(fused_csv_path: str, inconsistencies_csv_path: str, output_csv_path: str):
    """Reads the datasets, resolves inconsistencies, and saves the updated dataset."""
    fused_df = pd.read_csv(fused_csv_path)
    inconsistencies_df = pd.read_csv(inconsistencies_csv_path)

    # Expecting specific columns in the inconsistencies CSV
    required_cols = {'entity', 'property', 'source A value', 'source B value', 'location'}
    if not required_cols.issubset(inconsistencies_df.columns):
        missing = required_cols - set(inconsistencies_df.columns)
        raise ValueError(f"The following required columns are missing in inconsistencies file: {missing}")

    for idx, row in inconsistencies_df.iterrows():
        entity, property_, source_a, source_b, location = row['entity'], row['property'], row['source A value'], row[
            'source B value'], row['location']

        try:
            row_id, col_name = map(str.strip, location.split(','))
            row_id = int(row_id)
        except ValueError:
            print(f"Invalid location format: {location}. Skipping this inconsistency.")
            continue

        prompt = construct_prompt(entity, property_, source_a, source_b)
        response = get_gpt4_response(prompt)

        resolved_value = parse_response(response) if response else "UNKNOWN"
        print(f"Resolved {entity}'s {property_}: {resolved_value}")

        if 0 <= row_id < len(fused_df) and col_name in fused_df.columns:
            fused_df.at[row_id, col_name] = resolved_value
        else:
            print(f"Invalid row_id or column name for {entity}'s {property_}. Skipping update.")

        time.sleep(1)

    fused_df.to_csv(output_csv_path, index=False)
    print(f"Updated fused dataset saved to {output_csv_path}")


if __name__ == "__main__":
    # Define file paths
    fused_csv = "fused_dataset.csv"
    inconsistencies_csv = "inconsistencies.csv"
    output_csv = "updated_fused_dataset.csv"

    if not os.path.exists(fused_csv) or not os.path.exists(inconsistencies_csv):
        print("Required input files are missing.")
    else:
        resolve_inconsistencies(fused_csv, inconsistencies_csv, output_csv)

