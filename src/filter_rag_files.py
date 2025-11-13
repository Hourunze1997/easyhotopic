#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

def filter_json_files(directory_path):
    """
    Traverse the specified directory and filter JSON files based on keywords.
    
    Args:
        directory_path (str): Path to the directory containing JSON files
        
    Returns:
        list: List of file paths that don't contain the filtered keywords
    """
    # Keywords to filter out
    filter_keywords = ["已评审", "待评审", "关闭issue统计"]
    
    # List to store filtered file paths
    filtered_files = []
    
    # Check if directory exists
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist.")
        return filtered_files
    
    # Traverse the directory
    for filename in os.listdir(directory_path):
        # Check if file has .json extension
        if filename.endswith('.json'):
            # Check if file contains any of the filter keywords
            should_filter = False
            for keyword in filter_keywords:
                if keyword in filename:
                    should_filter = True
                    break
            
            # If file doesn't contain any filter keywords, add to list
            if not should_filter:
                file_path = os.path.join(directory_path, filename)
                filtered_files.append(file_path)
    
    return filtered_files

def main():
    # Directory path
    directory_path = "/home/workspace/easyhotopic/openumbc/data/rag"
    
    # Get filtered files
    filtered_files = filter_json_files(directory_path)
    
    # Print results
    print(f"Found {len(filtered_files)} files that don't match the filter criteria:")
    for file_path in filtered_files:
        print(file_path)
    
    # Optionally save to a file
    output_file = "filtered_rag_files.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for file_path in filtered_files:
            f.write(file_path + '\n')
    
    print(f"\nFile list also saved to {output_file}")

if __name__ == "__main__":
    main()