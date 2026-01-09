import pandas as pd
import os
import calendar
from datetime import datetime

# --- 1. กำหนด Path (ตามที่คุณระบุมา) ---
folder_path = r'd:\Users\Admin\Desktop\ModelAll'
file_name = 'Processed_Data_Final.csv'
file_path = os.path.join(folder_path, file_name)

# --- 2. โหลดและเตรียมข้อมูล ---
if not os.path.exists(file_path):
    print(f"❌ ไม่พบไฟล์: {file_path}")
    print("   (กรุณาตรวจสอบว่าได้รันโค้ดรวมไฟล์เพื่อสร้าง Combined_Corrected.csv หรือยัง)")
    exit()

print(f"📂 กำลังอ่านไฟล์จาก: {file_path}")
df = pd.read_csv(file_path)

# แปลง Date+Time ให้เป็น datetime object ที่สมบูรณ์
# หมายเหตุ: ถ้าในไฟล์มี column 'Date' กับ 'Time' แยกกัน
df['Date'] = df['Date'].astype(str).str.strip()
df['Time'] = df['Time'].astype(str).str.strip()
df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True, errors='coerce')

# ลบแถวที่เวลาเสีย (ถ้ามี)
df = df.dropna(subset=['Datetime'])

# เตรียมข้อมูลสำหรับตรวจสอบ
df['Date_Only'] = df['Datetime'].dt.date
present_dates = set(df['Date_Only']) # วันที่ที่มีอยู่จริงในไฟล์

# หาขอบเขตวันเริ่มต้น-สิ้นสุด
min_date = df['Datetime'].min().date()
max_date = df['Datetime'].max().date()

print("\n" + "="*60)
print(f"📊 รายงานสรุปวันขาดหาย (Missing Dates Report)")
print(f"📍 โฟลเดอร์: {folder_path}")
print(f"📅 ช่วงข้อมูล: {min_date.strftime('%d/%m/%Y')} ถึง {max_date.strftime('%d/%m/%Y')}")
print("="*60 + "\n")

# --- 3. ลูปตรวจสอบทีละเดือน ---
# สร้างช่วงเดือนทั้งหมดตั้งแต่เริ่มจนจบ
all_months = pd.period_range(min_date, max_date, freq='M')

for period in all_months:
    year = period.year
    month = period.month
    
    # จำนวนวันทั้งหมดในเดือนนั้น
    num_days_in_month = calendar.monthrange(year, month)[1]
    
    # สร้าง set ของวันที่ "ควรจะมี" ในเดือนนั้น (1 ถึง สิ้นเดือน)
    expected_dates = {
        datetime(year, month, d).date() for d in range(1, num_days_in_month + 1)
    }
    
    # หาวันที่หายไป (Expected - Present)
    missing_dates = sorted(list(expected_dates - present_dates))
    
    # นับจำนวนวันที่เจอ
    found_count = len(expected_dates.intersection(present_dates))
    
    # แสดงผล
    print(f"📅 เดือน {period}: มีข้อมูล {found_count} / {num_days_in_month} วัน")
    
    if missing_dates:
        # กรองเฉพาะวันที่อยู่ในช่วง "ขาดจริง" (ไม่นับก่อนเริ่มเก็บ หรือหลังเลิกเก็บ)
        real_missing = [d for d in missing_dates if min_date <= d <= max_date]
        
        if real_missing:
            missing_str = ", ".join([d.strftime('%d') for d in real_missing])
            print(f"   ❌ ขาดวันที่: {missing_str}")
        else:
            # กรณีวันหายไปเพราะอยู่นอกช่วงเริ่ม/จบไฟล์ (เช่น ไฟล์จบวันที่ 8 ม.ค. แต่วันที่ 9-31 ไม่มี)
            print(f"   ⚠️ วันที่เหลือไม่มีข้อมูล (อยู่นอกช่วง Start-End ของไฟล์)")
    else:
        print("   ✅ ครบถ้วน 100%")
    
    print("-" * 40)

print("\nจบการทำงาน")