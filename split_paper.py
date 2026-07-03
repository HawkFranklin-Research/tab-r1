import re
import os

input_file = '/home/prime/Documents/g3/tab-r1/tabpfn.txt'
out_dir = '/home/prime/Documents/g3/tab-r1/papers-info/'
os.makedirs(out_dir, exist_ok=True)

with open(input_file, 'r', encoding='utf-8') as f:
    text = f.read()

def clean_content(content):
    content = content.replace('\f', '')
    content = re.sub(r'\d+\s*\|\s*Nature\s*\|\s*Vol\s*637\s*\|\s*\d+\s*January\s*2025', '', content)
    content = re.sub(r'^Article$', '', content, flags=re.MULTILINE)
    return content.strip()

# Keywords to find their indices
keywords = [
    ("START", r"Accurate predictions on small data with a"),
    ("ICL", r"Principled in-context learning"),
    ("ARCH", r"An architecture designed for tables"),
    ("QUAL", r"Qualitative analysis"),
    ("QUANT", r"Quantitative analysis"),
    ("SOTA", r"Comparison with state-of-the-art baselines"),
    ("ATTR", r"Evaluating diverse data attributes"),
    ("ENSEMBLE", r"Comparison with tuned ensemble methods"),
    ("INTERP", r"Foundation model with interpretability"),
    ("CONCL", r"Conclusion"),
    ("METHODS", r"Methods"),
    ("AVAIL", r"Data availability")
]

indices = []
for key, pattern in keywords:
    # Use re.IGNORECASE and find the first occurrence that looks like a header
    # For Methods, prioritize the one with \f
    if key == "METHODS":
        match = re.search(r"\f\s*Methods", text)
        if not match:
            match = re.search(r"Methods", text)
    else:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    
    if match:
        indices.append((key, match.start()))
    else:
        print(f"Warning: Could not find {key}")

# Sort indices by position
indices.sort(key=lambda x: x[1])

# Map files to keywords
file_map = {
    "Abstract_and_Introduction.md": ["START"],
    "Principled_In_Context_Learning.md": ["ICL"],
    "Architecture_and_Synthetic_Data.md": ["ARCH"],
    "Quantitative_and_Qualitative_Analysis.md": ["QUAL", "QUANT", "SOTA", "ATTR"],
    "Comparison_with_Tuned_Ensembles.md": ["ENSEMBLE"],
    "Foundation_Model_Abilities_and_Interpretability.md": ["INTERP"],
    "Conclusion.md": ["CONCL"],
    "Methods_Supplementary.md": ["METHODS"]
}

# Create a lookup for index by key
idx_by_key = {key: pos for key, pos in indices}

for filename, keys in file_map.items():
    start_key = keys[0]
    if start_key not in idx_by_key:
        print(f"Skipping {filename} as {start_key} not found")
        continue
    
    start_pos = idx_by_key[start_key]
    
    # Find the next key in the sorted list that is NOT in the current keys list
    end_pos = len(text)
    for i in range(len(indices)):
        if indices[i][0] == start_key:
            # Check the keys after this one
            for j in range(i + 1, len(indices)):
                if indices[j][0] not in keys:
                    end_pos = indices[j][1]
                    break
            break
            
    content = text[start_pos:end_pos]
    with open(os.path.join(out_dir, filename), "w", encoding="utf-8") as f:
        f.write(clean_content(content) + "\n")

# Figures extraction
# Looking for lines starting with Fig. X or Table X or Extended Data ...
figures_pattern = r"(?:^|\n)(Fig\.|Table|Extended Data)\s+\d+.*?\|.*?(?:\n\n|\n(?=[A-Z])|$)"
captions = re.findall(figures_pattern, text, re.MULTILINE | re.DOTALL)
# Actually, let's just grep for "Fig." and "Table" and take some lines after
with open(os.path.join(out_dir, "Tables_and_Figures_Captions.md"), "w", encoding="utf-8") as f:
    # Use a simpler regex to just find the caption lines
    for line in text.split('\n'):
        if re.match(r"^(?:Fig\.|Table|Extended Data (?:Fig\.|Table))\s+\d+", line):
            f.write(line.strip() + "\n\n")
