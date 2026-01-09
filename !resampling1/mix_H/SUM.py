import pandas as pd
import os

# --- 1. การตั้งค่า ---
folder_path = r'd:\Users\Admin\Desktop\ModelAll\!resampling1\mix_H' # แก้ path ตามจริง
file_source_name = '5.csv'
file_main_name = 'Combined_Corrected.csv'
output_name = 'Final_Merged_Smart.csv'

# คอลัมน์ที่ต้องการดึง
cols_data = ['indoor_PC0.1', 'outdoor_PM2.5', 'outdoor_Temp', 'outdoor_Hum']

file_source_path = os.path.join(folder_path, file_source_name)
file_main_path = os.path.join(folder_path, file_main_name)
output_path = os.path.join(folder_path, output_name)

try:
    print("🔄 กำลังอ่านไฟล์...")
    df_source = pd.read_csv(file_source_path, low_memory=False)
    df_main = pd.read_csv(file_main_path, low_memory=False)

    # ตัดช่องว่างชื่อคอลัมน์
    df_source.columns = df_source.columns.str.strip()
    df_main.columns = df_main.columns.str.strip()

    print("🕒 กำลังสร้างกุญแจสำหรับจับคู่ (Datetime Key)...")
    # เทคนิคสำคัญ: แปลง วัน+เวลา ให้เป็น datetime object มาตรฐานสากล
    # วิธีนี้จะแก้ปัญหา 1/1/2025 ไม่ตรงกับ 01/01/2025 ได้ 100%
    df_source['Match_Key'] = pd.to_datetime(df_source['Date'].astype(str) + ' ' + df_source['Time'].astype(str), dayfirst=True, errors='coerce')
    df_main['Match_Key'] = pd.to_datetime(df_main['Date'].astype(str) + ' ' + df_main['Time'].astype(str), dayfirst=True, errors='coerce')

    # กำจัดตัวซ้ำในไฟล์ 5.csv ก่อน (ป้องกันไฟล์ระเบิด)
    print("🧹 กำจัดเวลาที่ซ้ำกันใน 5.csv...")
    df_source_dedup = df_source.drop_duplicates(subset=['Match_Key'])
    
    # เลือกเฉพาะข้อมูลที่จะใช้
    cols_to_use = ['Match_Key'] + cols_data
    df_source_ready = df_source_dedup[cols_to_use]

    print("🔗 กำลังจับคู่ข้อมูล (Smart Merge)...")
    # เชื่อมด้วย Match_Key ที่สร้างขึ้นมา
    df_merged = pd.merge(df_main, df_source_ready, on='Match_Key', how='left')

    # ลบคอลัมน์กุญแจทิ้ง (ไม่จำเป็นต้องโชว์ในไฟล์ผลลัพธ์)
    df_merged.drop(columns=['Match_Key'], inplace=True)

    # บันทึก
    df_merged.to_csv(output_path, index=False, encoding='utf-8')
    
    print("-" * 30)
    print(f"✅ สำเร็จ! แก้ไขเรื่องรูปแบบเวลาไม่ตรงกันแล้ว")
    print(f"📂 ไฟล์บันทึกที่: {output_path}")
    print(f"📊 แถวไฟล์หลัก: {len(df_main)}")
    print(f"📊 แถวไฟล์ใหม่: {len(df_merged)} (เท่ากันเป๊ะ)")
    
    # เช็คยอดข้อมูลที่ดึงมาได้
    matched_count = df_merged['outdoor_PM2.5'].notna().sum()
    print(f"📈 ดึงข้อมูล outdoor_PM2.5 มาได้: {matched_count:,} แถว")
    print("-" * 30)
    print(df_merged.head())

except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")