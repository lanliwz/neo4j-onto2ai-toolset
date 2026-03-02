#!/usr/bin/env python3
import sys

def deduplicate_ontology(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    output_lines = []
    labels_seen = set()

    i = 0
    while i < len(lines):
        line = lines[i]
        if "<owl:ObjectProperty" in line:
            property_block = []
            is_duplicate = False
            
            j = i
            label = ""
            while j < len(lines):
                property_block.append(lines[j])
                if "<rdfs:label>" in lines[j]:
                    label_start = lines[j].find("<rdfs:label>") + len("<rdfs:label>")
                    label_end = lines[j].find("</rdfs:label>")
                    label = lines[j][label_start:label_end].strip()
                
                if "</owl:ObjectProperty>" in lines[j]:
                    break
                j += 1
                
            if label:
                if label.lower() in labels_seen:
                    is_duplicate = True
                else:
                    labels_seen.add(label.lower())
                    
            if is_duplicate:
                if len(output_lines) >= 2 and "<!--" in output_lines[-1] and output_lines[-2].strip() == "":
                    output_lines.pop()
                    output_lines.pop()
            else:
                output_lines.extend(property_block)
                
            i = j + 1
        else:
            output_lines.append(line)
            i += 1

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(output_lines)
    
    print(f"Deduplicated Object Properties in {file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 deduplicate_ontology.py <path_to_rdf_file>")
        sys.exit(1)
        
    deduplicate_ontology(sys.argv[1])
