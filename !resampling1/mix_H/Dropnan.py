import pandas as pd
import os

# --- ตั้งค่าชื่อไฟล์ ---
folder_path = r'd:\Users\Admin\Desktop\ModelAll\!resampling1\mix_H' # แก้ Path ให้ตรงกับเครื่องคุณ
input_file_name = 'Final_Merged_Smart.csv'
output_file_name = 'Final_Merged_Smart_Cleaned.csv'

file_path = os.path.join(folder_path, input_file_name)
output_path = os.path.join(folder_path, output_file_name)

try:
    print(f"🔄 กำลังอ่านไฟล์: {input_file_name} ...")
    df = pd.read_csv(file_path, low_memory=False)
    
    # 1. ตรวจสอบและแสดงจำนวน NaN แต่ละคอลัมน์
    print("\n" + "="*40)
    print("📊 รายงานค่าว่าง (NaN) แยกรายคอลัมน์:")
    print("="*40)
    nan_report = df.isna().sum()
    print(nan_report[nan_report > 0]) # โชว์เฉพาะคอลัมน์ที่มี NaN
    
    print("\n" + "-"*40)
    total_rows = len(df)
    rows_with_nan = df.isna().any(axis=1).sum()
    print(f"📌 จำนวนแถวทั้งหมด: {total_rows:,}")
    print(f"⚠️  จำนวนแถวที่มีค่าว่าง: {rows_with_nan:,}")
    print("-"*40)

    # 2. ลบแถวที่มีค่าว่างออก (Drop NaN)
    if rows_with_nan > 0:
        print("\n🧹 กำลังลบแถวที่มีค่าว่างออก...")
        df_clean = df.dropna()
        
        # 3. บันทึกไฟล์ใหม่
        df_clean.to_csv(output_path, index=False, encoding='utf-8')
        
        remaining_rows = len(df_clean)
        print(f"✅ บันทึกไฟล์ที่คลีนแล้ว: {output_file_name}")
        print(f"📉 เหลือข้อมูลจำนวน: {remaining_rows:,} แถว")
        print(f"🗑️  หายไปทั้งหมด: {total_rows - remaining_rows:,} แถว")
    else:
        print("\n✅ ข้อมูลสมบูรณ์อยู่แล้ว (ไม่มี NaN) ไม่จำเป็นต้องลบ")

except FileNotFoundError:
    print(f"❌ ไม่พบไฟล์: {file_path}")
    print("   กรุณาตรวจสอบชื่อไฟล์และ Path อีกครั้ง")
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")