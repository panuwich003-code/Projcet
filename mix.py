import pandas as pd
import os
import numpy as np

# --- 1. กำหนดค่าต่างๆ ---
input_file_path = r'd:\Users\Admin\Desktop\ModelAll\Final_Merged_Smart_Cleaned.csv'
output_dir = os.path.dirname(input_file_path)

# Mapping ชื่อคอลัมน์
column_mapping = {
    'Date': 'Date',
    'Time': 'Time',
    'Bar': 'Bar',
    'Dir': 'Wind_Dir', 
    'Speed': 'Wind_Speed',
    'outdoor_Temp': 'Outdoor_Temperature',
    'outdoor_Hum': 'Outdoor_Humidity',
    'outdoor_PM2.5': 'Outdoor_PM2.5',
    'indoor_PC0.1': 'Indoor_PC0.1'
}

# Mapping ทิศทางลม
wind_directions = {
    "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5,
    "E": 90, "ESE": 112.5, "SE": 135, "SSE": 157.5,
    "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5,
    "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5
}

# รายชื่อคอลัมน์ที่ต้องการเรียงลำดับในไฟล์สุดท้าย
final_columns_order = [
    'Date', 'Time', 'Bar', 'Wind_Dir', 'Wind_Speed', 
    'Outdoor_Temperature', 'Outdoor_Humidity', 'Outdoor_PM2.5', 
    'Indoor_PC0.1', 'Wind_Dir_Degree'
]

# --- ฟังก์ชันสำหรับหาค่าที่ปรากฏบ่อยสุด (Mode) สำหรับ Text ---
def get_mode(x):
    mode = x.mode()
    if not mode.empty:
        return mode[0]
    return np.nan

# --- 2. การประมวลผลข้อมูล ---
try:
    print(f"🔄 กำลังอ่านไฟล์: {input_file_path}")
    df = pd.read_csv(input_file_path, low_memory=False)
    df.columns = df.columns.str.strip() # ลบช่องว่างชื่อคอลัมน์

    # 2.1 เปลี่ยนชื่อและเลือกคอลัมน์
    available_cols = [col for col in column_mapping.keys() if col in df.columns]
    df_processed = df[available_cols].rename(columns=column_mapping)

    # 2.2 แปลงทิศทางลมเป็นองศา
    if 'Wind_Dir' in df_processed.columns:
        df_processed['Wind_Dir'] = df_processed['Wind_Dir'].astype(str).str.strip().str.upper()
        df_processed['Wind_Dir_Degree'] = df_processed['Wind_Dir'].map(wind_directions)

    # 2.3 สร้าง DateTime Column เพื่อใช้คำนวณเวลา
    # หมายเหตุ: dayfirst=True ลองใช้ดูถ้า Date เป็น วว/ดด/ปปปป (ถ้า error ให้ลองลบ dayfirst ออก)
    df_processed['Datetime'] = pd.to_datetime(
        df_processed['Date'] + ' ' + df_processed['Time'], 
        dayfirst=True, 
        errors='coerce'
    )
    
    # ลบแถวที่แปลงเวลาไม่ได้ (ถ้ามี)
    df_processed = df_processed.dropna(subset=['Datetime'])
    df_processed = df_processed.set_index('Datetime')
    df_processed = df_processed.sort_index() # เรียงเวลาให้ถูกต้อง

    # ==========================================
    # ส่วนที่ 1: บันทึกไฟล์ 5 นาที (ต้นฉบับ Clean แล้ว)
    # ==========================================
    df_5min = df_processed.copy().reset_index()
    # จัดการ Column ให้ตรงตามต้องการ
    output_5min = df_5min[final_columns_order]
    
    path_5min = os.path.join(output_dir, 'Processed_Data_5min.csv')
    output_5min.to_csv(path_5min, index=False, encoding='utf-8-sig')
    print(f"✅ บันทึกไฟล์ 5 นาที เรียบร้อย: {path_5min}")

    # ==========================================
    # ฟังก์ชันสำหรับการรวมเวลา (Resampling)
    # ==========================================
    def process_and_save_resampled(df_source, rule, suffix_name):
        print(f"⏳ กำลังประมวลผลข้อมูลราย {suffix_name}...")
        
        # แยกคอลัมน์ตัวเลขและไม่ใช่ตัวเลข
        numeric_cols = ['Bar', 'Wind_Speed', 'Outdoor_Temperature', 
                        'Outdoor_Humidity', 'Outdoor_PM2.5', 'Indoor_PC0.1', 'Wind_Dir_Degree']
        
        # ตรวจสอบว่าคอลัมน์มีอยู่จริงไหมก่อนเลือก
        numeric_cols = [c for c in numeric_cols if c in df_source.columns]
        
        # 1. Resample ข้อมูลตัวเลข (หาค่าเฉลี่ย Mean)
        # closed='right', label='right' คือการรวมแบบ 00:10-00:20 ให้เป็นค่าของ 00:20
        df_num = df_source[numeric_cols].resample(rule, closed='right', label='right').mean()

        # 2. Resample ข้อมูลตัวหนังสือ (Wind_Dir) (เลือกค่าที่พบบ่อยสุด หรือค่าสุดท้าย)
        # ในที่นี้ใช้ 'last' (ค่าล่าสุด ณ เวลาจบช่วง) เพื่อให้ตรงกับสภาพอากาศตอนบันทึก
        # หรือถ้าอยากได้ค่าที่พบบ่อยให้เปลี่ยน .last() เป็น .apply(get_mode)
        if 'Wind_Dir' in df_source.columns:
            df_str = df_source['Wind_Dir'].resample(rule, closed='right', label='right').last()
        else:
            df_str = pd.Series()

        # 3. รวมกลับมารวมกัน
        df_result = pd.concat([df_num, df_str], axis=1)

        # 4. สร้าง Date และ Time กลับมาใหม่จาก Index
        df_result = df_result.reset_index()
        df_result['Date'] = df_result['Datetime'].dt.strftime('%d/%m/%Y') # ปรับ format วันที่ตามต้องการ
        df_result['Time'] = df_result['Datetime'].dt.strftime('%H:%M')

        # 5. เรียงคอลัมน์และบันทึก
        # กรองเฉพาะคอลัมน์ที่มีอยู่จริงจาก final_columns_order
        cols_to_save = [c for c in final_columns_order if c in df_result.columns]
        df_final = df_result[cols_to_save]

        # ลบแถวที่ว่างทั้งหมด (เผื่อกรณีเวลาข้าม)
        df_final = df_final.dropna(how='all', subset=numeric_cols)

        output_path = os.path.join(output_dir, f'Processed_Data_{suffix_name}.csv')
        df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"✅ บันทึกไฟล์ {suffix_name} เรียบร้อย: {output_path}")

    # ==========================================
    # ส่วนที่ 2 & 3: สร้างไฟล์ 10 นาที และ 20 นาที
    # ==========================================
    
    # สร้างไฟล์ 10 นาที (10T = 10 Minutes)
    process_and_save_resampled(df_processed, '10T', '10min')

    # สร้างไฟล์ 20 นาที (20T = 20 Minutes)
    process_and_save_resampled(df_processed, '20T', '20min')

    print("-" * 40)
    print("🎉 เสร็จสิ้นทุกขั้นตอน!")

except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")
    import traceback
    traceback.print_exc()