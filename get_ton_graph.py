# pylint: disable= missing-module-docstring, missing-function-docstring, missing-final-newline
# pylint: disable= line-too-long, redefined-outer-name

import os
import traceback
import unicodedata
import itertools
import pandas as pd
import subprocess
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

BASE_DIR = ".\\output\\key\\"
OUTPUT_BASE_DIR = ".\\personal_statistic\\base\\"
CHECK_LIST_FILE = ".\\personal_statistic\\check_list.txt"

CATEGORIES = {
    'Увольнение': {'нет': 0, 'да': 120},
    'Оффер': {'нет': 0, 'да': 100},
    'Вредительство': {'нет': 0, 'да': 50},
    'Конфликты': {'нет': 0, 'да': 40},
    'Стресс': {'нет': 0, 'да': 30},
    'Личная жизнь': {'нет': 0, 'да': 20},
    'Тон': {'дружественный': 0, 'негативный': 10}
}

DEPENDENCIES = {
    'Увольнение': {'Оффер': 1.8, 'Конфликты': 1.5, 'Вредительство': 1.2, 'Стресс': 1.4},
    'Оффер': {'Увольнение': 1.8, 'Конфликты': 1.5, 'Вредительство': 1.2, 'Стресс': 1.4},
    'Вредительство': {'Конфликты': 1.5, 'Стресс': 1.3},
    'Конфликты': {'Вредительство': 1.5, 'Стресс': 1.3, 'Личная жизнь': 1.2, 'Увольнение': 1.4, 'Оффер': 1.4},
    'Стресс': {'Конфликты': 1.5, 'Личная жизнь': 1.2, 'Увольнение': 1.4, 'Оффер': 1.4},
    'Личная жизнь': {'Стресс': 1.5, 'Конфликты': 1.2}
}

def process_files(base_dir, check_list_file, output_base_dir):
    with open(check_list_file, 'r', encoding='utf-8') as f:
        check_list = set(line.strip() for line in f)

    all_files = set()
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".txt"):
                full_path = os.path.join(root, file)
                all_files.add(full_path)

    files_to_process = all_files - check_list

    count = 1
    for file in files_to_process:
        process_file(file, check_list_file, output_base_dir, count, files_to_process)
        count += 1

    print(f"Всего {len(all_files)} файлов.")
    print(f"Было обработано ранее {len(check_list)} файлов.")
    print(f"Было обработано сейчас {len(files_to_process)} файлов.")

def process_file(file, check_list_file, output_base_dir, count, files_to_process):
    with open(check_list_file, 'a', encoding='utf-8') as f:
        f.write(file + '\n')
    print(f"{count}/{len(files_to_process)} --- {file}")
    try:
        summ_check = 0
        dialog_analysis = {
            'Увольнение': 'нет',
            'Оффер': 'нет',
            'Вредительство': 'нет',
            'Конфликты': 'нет',
            'Стресс': 'нет',
            'Личная жизнь': 'нет',
            'Тон': 'дружественный'
        }

        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) < 8:
                return
            lines = lines[:8]  # Берем первые строки
            for line in lines:
                line = line.lower().strip()
                if line.startswith('[увольнение]'):
                    dialog_analysis['Увольнение'] = 'да' if 'да' in line else 'нет'
                elif line.startswith('[оффер]'):
                    dialog_analysis['Оффер'] = 'да' if 'да' in line else 'нет'
                elif line.startswith('[вредительство]'):
                    dialog_analysis['Вредительство'] = 'да' if 'да' in line else 'нет'
                elif line.startswith('[конфликты]'):
                    dialog_analysis['Конфликты'] = 'да' if 'да' in line else 'нет'
                elif line.startswith('[стресс]'):
                    dialog_analysis['Стресс'] = 'да' if 'да' in line else 'нет'
                elif line.startswith('[личная жизнь]'):
                    dialog_analysis['Личная жизнь'] = 'да' if 'да' in line else 'нет'
                elif line.startswith('[тон]'):
                    dialog_analysis['Тон'] = 'негативный' if 'негативный' in line else 'дружественный'

        for category, value in dialog_analysis.items():
            if value == 'да':
                base_weight = CATEGORIES[category]['да']
                coefficients = []
                for dep_category, coefficient in DEPENDENCIES.get(category, {}).items():
                    if dialog_analysis.get(dep_category) == 'да':
                        coefficients.append(coefficient)
                if coefficients:
                    base_weight *= sum(coefficients) / len(coefficients)
                summ_check += base_weight

        if summ_check == 0:
            return

        parts = file.split("-")
        date_parts = parts[1].split("_")
        year = date_parts[0]
        month = date_parts[1]
        day = date_parts[2]

        date_formatted = f"{day}.{month}."

        username = parts[2].split("@")[0]

        output_dir = os.path.join(output_base_dir, year)
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, f"{username}.xlsx")

        if not os.path.exists(output_file):
            df = pd.DataFrame({date_formatted: [None, None, summ_check]})
            df.to_excel(output_file, sheet_name=month, index=False)

            df_empty = pd.DataFrame()
            df_empty_tech_list = pd.DataFrame(columns=['filename'])
            with pd.ExcelWriter(output_file, engine='openpyxl', mode='a') as writer:
                df_empty.to_excel(writer, sheet_name='result')
                df_empty_tech_list.to_excel(writer, sheet_name='tech_list')
        else:
            xls = pd.ExcelFile(output_file)
            dfs = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
            df_tech_list = dfs['tech_list']
            if file in df_tech_list['filename'].values:
                return

            next_idx = len(df_tech_list)
            df_tech_list.loc[next_idx, 'filename'] = file

            if month in dfs:
                df = dfs[month]

                if date_formatted in df.columns:
                    max_index = df[date_formatted].notna().sum() - 1
                    df.loc[max_index + 3, date_formatted] = summ_check
                else:
                    df[date_formatted] = pd.Series([None, None, summ_check])
            else:
                df = pd.DataFrame({date_formatted: [None, None, summ_check]})
                dfs[month] = df

            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                for sheet, df in dfs.items():
                    df.to_excel(writer, sheet_name=sheet, index=False)
    except Exception as e:
        print(f"Error processing file {file}: {e}")
        print(traceback.format_exc())

def calculate_averages(output_base_dir):
    for root, dirs, files in os.walk(output_base_dir):
        for file in files:
            if file.endswith(".xlsx"):
                full_path = os.path.join(root, file)
                try:
                    xls = pd.ExcelFile(full_path)
                    dfs = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}

                    for sheet, df in dfs.items():
                        if sheet in ['tech_list', 'result']:
                            continue
                        averages = df.mean()
                        df.loc[0] = averages
                        df.index = df.index + 1
                        df = df.sort_index()

                    with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
                        for sheet, df in dfs.items():
                            df.to_excel(writer, sheet_name=sheet, index=False)
                except Exception as e:
                    print(f"Error processing file {full_path}: {e}")

def main():
    process_files(BASE_DIR, CHECK_LIST_FILE, OUTPUT_BASE_DIR)
    calculate_averages(OUTPUT_BASE_DIR)
    subprocess.run(["python", "get_sum_stat.py"])

if __name__ == "__main__":
    main()
