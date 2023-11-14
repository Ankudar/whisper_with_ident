import os
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

base_dir = "dir"
output_base_dir = "dir"

tonality_dict = {'neutral': 0, 'supernegative': -1, 'negative': -0.7, 'positive': 0.7, 'superpositive': 1}

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".txt"):
            tonality = None
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith("Тональность беседы - "):
                        tonality_value = line.replace("Тональность беседы - ", "").strip()
                        if tonality_value in tonality_dict:
                            tonality = tonality_dict[tonality_value]
                        elif tonality_value.isdigit():
                            tonality = float(tonality_value)
                        break
            if tonality is not None:
                parts = file.split("-")
                date_parts = parts[1].split("_")
                year = date_parts[0]
                month = date_parts[1]
                day = date_parts[2]

                username = parts[2].split("@")[0]

                output_dir = os.path.join(output_base_dir, year)
                os.makedirs(output_dir, exist_ok=True)

                output_file = os.path.join(output_dir, f"{username}.xlsx")

                if not os.path.exists(output_file):
                    df = pd.DataFrame({day: [tonality]})
                    df.to_excel(output_file, sheet_name=month, index=False)

                    # Create empty 'result' and 'tech_list' tabs
                    df_empty = pd.DataFrame()
                    df_empty_tech_list = pd.DataFrame(columns=['filename'])
                    with pd.ExcelWriter(output_file, engine='openpyxl', mode='a') as writer:
                        df_empty.to_excel(writer, sheet_name='result')
                        df_empty_tech_list.to_excel(writer, sheet_name='tech_list')
                else:
                    # read the entire Excel file
                    xls = pd.ExcelFile(output_file)
                    dfs = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}

                    # check if file has been processed
                    df_tech_list = dfs['tech_list']
                    if file in df_tech_list['filename'].values:
                        continue

                    # update 'tech_list'
                    next_idx = len(df_tech_list)
                    df_tech_list.loc[next_idx, 'filename'] = file

                    # update the specific month sheet
                    if month in dfs:
                        df = dfs[month]

                        if day in df.columns:
                            max_index = df[day].notna().sum()
                            df.loc[max_index + 2, day] = tonality
                        else:
                            df[day] = pd.Series([None, None, None, tonality])
                    else:
                        # or create a new one if does not exist
                        df = pd.DataFrame({day: [tonality]})
                        dfs[month] = df

                    # Calculate averages
                    for sheet, df in dfs.items():
                        if sheet not in ['result', 'tech_list']:
                            df.loc[0] = df.mean()

                    # write everything back
                    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                        for sheet, df in dfs.items():
                            df.to_excel(writer, sheet_name=sheet, index=False)