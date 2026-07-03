import re
import csv
import os

# Paths
base_path = '/home/prime/Documents/g3/tab-r1/papers/arXiv-2605.13986v1'
tex_file = os.path.join(base_path, 'use-case-list.tex')
bib_file = os.path.join(base_path, 'bib.bib')
output_csv = 'healthcare_tabpfn_usecases.csv'

def parse_tex(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract the Healthcare and Life Sciences section
    section_match = re.search(r'\\section\*\{Healthcare and Life Sciences\}(.*?)\\section\*', content, re.DOTALL)
    if not section_match:
        # If it's the last section or only section
        section_match = re.search(r'\\section\*\{Healthcare and Life Sciences\}(.*)', content, re.DOTALL)
    
    if not section_match:
        return []
    
    section_content = section_match.group(1)
    
    # Extract items
    # Format: \item DESCRIPTION \cite{KEY}. \href{LINK}{Link}
    items = re.findall(r'\\item\s+(.*?)\\cite\{(.*?)\}\.?\s*(?:\\href\{(.*?)\}\{Link\}|)', section_content, re.DOTALL)
    
    parsed_items = []
    for desc, cite_key, link in items:
        # Clean up description
        desc = desc.strip().replace('\n', ' ').replace('\t', ' ').replace('  ', ' ')
        parsed_items.append({
            'description': desc,
            'cite_key': cite_key.strip(),
            'link': link.strip()
        })
    
    return parsed_items

def parse_bib(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    bib_entries = {}
    # Split by @TYPE{
    entries = re.split(r'@\w+\s*\{', content)
    for entry in entries:
        if not entry: continue
        # Key is everything until the first comma
        key_match = re.match(r'^\s*([\w\-:\.]+),', entry)
        if key_match:
            key = key_match.group(1)
            # Find title field: title = { ... } or title = " ... "
            title_field_match = re.search(r'title\s*=\s*([\{\"])(.*)', entry, re.DOTALL | re.IGNORECASE)
            if title_field_match:
                delimiter = title_field_match.group(1)
                remaining = title_field_match.group(2)
                title_raw = ""
                if delimiter == '{':
                    # Balanced braces
                    brace_count = 1
                    for i, char in enumerate(remaining):
                        if char == '{': brace_count += 1
                        elif char == '}': brace_count -= 1
                        if brace_count == 0:
                            title_raw = remaining[:i]
                            break
                else:
                    # Until next "
                    end_quote = remaining.find('"')
                    if end_quote != -1:
                        title_raw = remaining[:end_quote]
                
                if title_raw:
                    # Clean up
                    title = title_raw.replace('\n', ' ').replace('\t', ' ').replace('  ', ' ')
                    # Remove LaTeX braces from title (e.g. {T}abPFN -> TabPFN)
                    title = re.sub(r'[\{\}]', '', title)
                    bib_entries[key] = title.strip()
    return bib_entries

def main():
    print("Parsing TeX file...")
    items = parse_tex(tex_file)
    print(f"Found {len(items)} items in TeX.")
    
    print("Parsing Bib file...")
    titles = parse_bib(bib_file)
    print(f"Found {len(titles)} titles in Bib.")
    
    print("Merging data...")
    final_data = []
    for item in items:
        title = titles.get(item['cite_key'], "Title not found in bib")
        final_data.append({
            'Paper Title': title,
            'Summary/Description': item['description'],
            'Link': item['link']
        })
    
    print(f"Saving to {output_csv}...")
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Paper Title', 'Summary/Description', 'Link'])
        writer.writeheader()
        writer.writerows(final_data)
    
    print("Done!")

if __name__ == '__main__':
    main()
