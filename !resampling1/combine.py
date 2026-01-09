import pandas as pd
import os

folder_path = r'd:\Users\Admin\Desktop\ModelAll\!resampling1'
file1_name = 'Final_Merged_Output.csv'
file2_name = 'frit.csv'
output_name = 'Combined_Data_Fixed_Columns.csv'

# 1. รายชื่อคอลัมน์มาตรฐานตามที่คุณต้องการ (ห้ามสลับที่)
target_columns = [
    'Date', 'Time', 'Out', 'Temp', 'Temp.1', 'Hum', 'Pt.', 'Speed', 'Dir', 'Run', 
    'Speed.1', 'Dir.1', 'Chill', 'Index', 'Index.1', 'Bar ', 'Rain', 'Rate', 'D-D ', 
    'D-D .1', 'Temp.2', 'Hum.1', 'Dew', 'Heat', 'EMC', 'Density', 'Samp', 'Tx ', 
    'Recept', 'Int.', 'out_temp', 'out_humid', 'out_pm1', 'out_pm25', 'out_pm10', 
    'in_temp', 'in_humid', 'in_pm1', 'in_pm25', 'in_pm10', 'PC0.1', 'PC0.3', 'PC0.5', 
    'PC1.0', 'PC2.5', 'PC5.0', 'PC10', 'PM0.1', 'PM0.3', 'PM0.5', 'PM1.0', 'PM2.5', 
    'PM5.0', 'PM10'
]

def load_and_clean(path):
    # อ่านไฟล์
    df = pd.read_csv(path, low_memory=False)
    # ลบช่องว่างส่วนเกินที่หัวคอลัมน์ออก เพื่อให้ชื่อตรงกันง่ายขึ้น
    df.columns = df.columns.str.strip()
    return df

try:
    # 2. อ่านและล้างชื่อคอลัมน์เบื้องต้น
    df1 = load_and_clean(os.path.join(folder_path, file1_name))
    df2 = load_and_clean(os.path.join(folder_path, file2_name))

    # 3. รวมไฟล์
    combined_df = pd.concat([df1, df2], ignore_index=True)

    # 4. ล้างแถวหัวข้อที่อาจหลุดมาเป็นข้อมูล
    combined_df = combined_df[combined_df['Date'] != 'Date']

    # 5. บังคับคอลัมน์ให้ตรงตาม target_columns (ถ้าอันไหนไม่มีให้เป็นค่าว่าง อันไหนเกินมาให้ตัดออก)
    # ล้างช่องว่างในลิสต์เป้าหมายด้วยเพื่อให้เทียบกันได้
    clean_targets = [c.strip() for c in target_columns]
    combined_df.columns = combined_df.columns.str.strip()
    
    # Reindex เพื่อจัดลำดับคอลัมน์ใหม่ตามที่คุณต้องการเป๊ะๆ
    combined_df = combined_df.reindex(columns=clean_targets)

    # 6. เรียงตามเวลา
    temp_dt = pd.to_datetime(
        combined_df['Date'].astype(str) + ' ' + combined_df['Time'].astype(str), 
        dayfirst=True, errors='coerce'
    )
    combined_df = combined_df.iloc[temp_dt.argsort()]

    # 7. บันทึกไฟล์
    combined_df.to_csv(os.path.join(folder_path, output_name), index=False, encoding='utf-8-sig')

    print(f"--- รวมไฟล์และจัดเรียงคอลัมน์ใหม่เรียบร้อย ---")
    print(f"คอลัมน์จะเรียงตามที่คุณกำหนด และไม่มีคอลัมน์ซ้ำซ้อนที่ท้ายไฟล์ครับ")

except Exception as e:
    print(f"เกิดข้อผิดพลาด: {e}")