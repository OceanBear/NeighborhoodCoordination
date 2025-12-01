import json
import pandas as pd
import numpy as np
from pathlib import Path
import glob

# Cell type mapping: numeric type -> [name, RGB_color]
CELL_TYPE_MAPPING = {
    0: ["Undefined", [0, 0, 0]],
    1: ["Epithelium (PD-L1lo/ki67lo)", [56, 127, 57]],
    2: ["Epithelium (PD-L1hi/ki67hi)", [0, 255, 0]],
    3: ["Macrophage", [252, 141, 98]],
    4: ["Lymphocyte", [255, 217, 47]],
    5: ["Vascular", [69, 53, 193]],
    6: ["Fibroblast/Stroma", [23, 190, 207]]
}

def convert_tiles_to_dataframe(tile_directory, output_file='main_fcs_csv.csv'):
    """
    Convert multiple JSON tile files into a single pandas DataFrame
    compatible with the Neighborhood Coordination scripts.
    
    Parameters:
    -----------
    tile_directory : str
        Directory containing tile JSON files (e.g., 'tile_*.json')
    output_file : str
        Output CSV filename (default: 'main_fcs_csv.csv')
    
    Returns:
    --------
    pd.DataFrame
        Combined dataframe with columns: X:X, Y:Y, File Name, ClusterName
    """
    
    # Find all tile JSON files
    tile_files = glob.glob(str(Path(tile_directory) / 'tile_*.json'))
    
    if not tile_files:
        raise ValueError(f"No tile JSON files found in {tile_directory}")
    
    print(f"Found {len(tile_files)} tile files")
    
    all_cells = []
    
    for tile_file in tile_files:
        # Extract tile name from filename (e.g., 'tile_15077_29493' from 'tile_15077_29493.json')
        tile_name = Path(tile_file).stem
        
        print(f"Processing {tile_name}...")
        
        # Load JSON file
        with open(tile_file, 'r') as f:
            tile_data = json.load(f)
        
        # Extract cell data from 'nuc' field
        if 'nuc' not in tile_data:
            print(f"  Warning: No 'nuc' field in {tile_name}, skipping...")
            continue
        
        nuc_data = tile_data['nuc']
        
        # Process each cell
        for cell_id, cell_info in nuc_data.items():
            # Extract centroid coordinates (x, y)
            centroid = cell_info.get('centroid', [None, None])
            
            # Extract cell type
            cell_type = cell_info.get('type', None)
            
            # Extract type probability (optional, for filtering)
            type_prob = cell_info.get('type_prob', 0.0)
            
            # Only include cells with valid data
            if centroid[0] is not None and centroid[1] is not None and cell_type is not None:
                # Map numeric type to cell type name
                if cell_type in CELL_TYPE_MAPPING:
                    cell_type_name = CELL_TYPE_MAPPING[cell_type][0]
                    cell_type_color = CELL_TYPE_MAPPING[cell_type][1]
                else:
                    # Fallback for unknown types
                    cell_type_name = f'Unknown_Type_{cell_type}'
                    cell_type_color = [128, 128, 128]  # Gray for unknown
                    print(f"  Warning: Unknown cell type {cell_type} in {tile_name}")
                
                all_cells.append({
                    'X:X': centroid[0],
                    'Y:Y': centroid[1],
                    'File Name': tile_name,  # Use tile name as region identifier
                    'ClusterName': cell_type_name,  # Use mapped cell type name
                    'type': cell_type,  # Keep numeric type
                    'type_prob': type_prob,  # Keep probability
                    'tile': tile_name,  # Keep tile reference
                    'color_R': cell_type_color[0],  # RGB color components
                    'color_G': cell_type_color[1],
                    'color_B': cell_type_color[2]
                })
        
        print(f"  Extracted {len([c for c in all_cells if c['tile'] == tile_name])} cells")
    
    # Create DataFrame
    df = pd.DataFrame(all_cells)
    
    print(f"\nTotal cells extracted: {len(df)}")
    print(f"Unique tiles: {df['File Name'].nunique()}")
    print(f"Unique cell types: {df['ClusterName'].nunique()}")
    print(f"\nCell type distribution:")
    print(df['ClusterName'].value_counts())
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"\nSaved to {output_file}")
    
    return df


# Example usage:
if __name__ == "__main__":
    # Set your tile directory path (WSL format)
    # Windows path: J:\HandE\results\SOW1885_n=201_AT2 40X\JN_TS_023\manual_2mm_17\json
    # WSL format: /mnt/j/HandE/results/SOW1885_n=201_AT2 40X/JN_TS_023/manual_2mm_17/json
    tile_dir = "/mnt/j/HandE/results/SOW1885_n=201_AT2 40X/JN_TS_023/manual_2mm_17/json"
    
    # Output files will be saved in the current working directory
    output_csv = 'main_fcs_csv.csv'
    output_pkl = 'main_fcs.pkl'
    
    # Convert tiles to dataframe
    df = convert_tiles_to_dataframe(tile_dir, output_file=output_csv)
    
    # Optional: Also save as pickle for faster loading
    df.to_pickle(output_pkl)
    print(f"Also saved as pickle: {output_pkl}")