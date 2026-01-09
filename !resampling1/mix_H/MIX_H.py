import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- 1. กำหนด Path ---
# เปลี่ยน path ตรงนี้ให้ตรงกับเครื่องของคุณ
folder_path = r'd:\Users\Admin\Desktop\ModelAll\!resampling1\mix_H' 
file1_path = os.path.join(folder_path, 'Merged_AWS_with_PM.csv')
file2_path = os.path.join(folder_path, 'Weather_and_PM_Harry.csv')

output_file_name = 'Combined_Corrected.csv'
output_path = os.path.join(folder_path, output_file_name)

# --- 2. ฟังก์ชันแปลงข้อมูลแบบแยกส่วน (Robust) ---
def robust_convert(df, filename):
    print(f"\n🔄 กำลังประมวลผลไฟล์: {filename}")
    
    # ลบช่องว่างในชื่อคอลัมน์และข้อมูลประเภท string
    df.columns = df.columns.str.strip()
    if 'Date' in df.columns:
        df['Date'] = df['Date'].astype(str).str.strip()
    if 'Time' in df.columns:
        df['Time'] = df['Time'].astype(str).str.strip()

    # 🟢 Step 1: แปลงวันที่
    # errors='coerce' จะเปลี่ยนวันที่ที่เป็นไปไม่ได้ (เช่น 31-09-25) ให้เป็น NaT
    date_objs = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')

    # 🟢 Step 2: แปลงเวลา
    time_objs = pd.to_datetime(df['Time'], errors='coerce')

    # 🟢 Step 3: รวมร่าง (Date + Time)
    # ใช้สูตรนี้เพื่อรวมวันที่และเวลาเข้าด้วยกันอย่างถูกต้อง
    df['DateTime_Sort'] = date_objs + (time_objs - time_objs.dt.normalize())

    # --- เช็คแถวที่เสีย ---
    mask_bad = df['DateTime_Sort'].isna()
    bad_rows_count = mask_bad.sum()
    
    if bad_rows_count > 0:
        print(f"   ⚠️ พบแถวที่ข้อมูลวันที่/เวลาผิดปกติ: {bad_rows_count} แถว (ระบบจะลบทิ้งอัตโนมัติ)")
    else:
        print("   ✅ ข้อมูลวันที่ถูกต้องครบถ้วน")

    # ลบแถวเสีย
    df_clean = df[~mask_bad].copy()
    
    # จัด Format วันที่และเวลาใหม่ให้เป็นมาตรฐาน (24 ชม.)
    df_clean['Date'] = df_clean['DateTime_Sort'].dt.strftime('%d/%m/%Y')
    df_clean['Time'] = df_clean['DateTime_Sort'].dt.strftime('%H:%M:%S')
    
    # แปลงค่า PM2.5 เป็นตัวเลข (เผื่อมีขยะปนมา)
    if 'out_pm25' in df_clean.columns:
        df_clean['out_pm25'] = pd.to_numeric(df_clean['out_pm25'], errors='coerce')
    
    return df_clean

try:
    # อ่านไฟล์
    print("📂 กำลังอ่านไฟล์...")
    df1 = pd.read_csv(file1_path, low_memory=False)
    df2 = pd.read_csv(file2_path, low_memory=False)

    # แปลงและทำความสะอาด
    df1_clean = robust_convert(df1, 'Merged_AWS_with_PM.csv')
    df2_clean = robust_convert(df2, 'Weather_and_PM_Harry.csv')

    # รวมไฟล์
    print("\n🔗 กำลังรวมไฟล์...")
    combined_df = pd.concat([df1_clean, df2_clean], ignore_index=True)

    # เรียงตามเวลา
    combined_df = combined_df.sort_values(by='DateTime_Sort')
    
    # ลบข้อมูลที่เวลาซ้ำกันเป๊ะๆ (ถ้ามี)
    combined_df = combined_df.drop_duplicates(subset=['DateTime_Sort'])

    # --- 3. บันทึกไฟล์ ---
    # ลบคอลัมน์ช่วยเรียงออกก่อนเซฟ (หรือจะเก็บไว้ก็ได้ถ้าต้องการ)
    df_to_save = combined_df.drop(columns=['DateTime_Sort'])
    df_to_save.to_csv(output_path, index=False, encoding='utf-8')
    
    print("-" * 40)
    print(f"🎉 เสร็จสมบูรณ์! บันทึกไฟล์แล้วที่: {output_path}")
    print(f"📊 จำนวนแถวทั้งหมดหลังรวม: {len(combined_df)}")
    print("-" * 40)

    # ========================================================
    # 📈 ส่วนสร้างกราฟเช็คข้อมูล (Plotting Section)
    # ========================================================
    print("\n📊 กำลังสร้างกราฟตรวจสอบข้อมูล...")

    # ตั้งค่าขนาดรูป
    plt.rcParams['figure.figsize'] = [12, 10]
    
    # สร้างพื้นที่กราฟ 2 ช่อง (บน/ล่าง)
    fig, (ax1, ax2) = plt.subplots(2, 1)
    
    # --- กราฟที่ 1: PM2.5 Time Series ---
    # พล็อตค่า out_pm25 เทียบกับเวลา
    plot_data = combined_df.dropna(subset=['out_pm25'])
    ax1.plot(plot_data['DateTime_Sort'], plot_data['out_pm25'], 
             color='#d62728', linewidth=0.8, label='out_pm25')
    
    ax1.set_title('PM2.5 Value Over Time (ค่าฝุ่น PM2.5 ตลอดช่วงเวลา)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('PM2.5 (µg/m³)', fontsize=12)
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend()
    
    # Format แกน X
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())

    # --- กราฟที่ 2: Data Points per Day (Check Gaps) ---
    combined_df['Date_Only'] = combined_df['DateTime_Sort'].dt.date
    daily_counts = combined_df.groupby('Date_Only').size()
    
    ax2.plot(daily_counts.index, daily_counts.values, marker='o', linestyle='-', color='royalblue', markersize=4)
    ax2.set_title('Data Points per Day (จำนวนข้อมูลต่อวัน - เช็คช่วงข้อมูลขาด)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('จำนวนแถว (Rows)', fontsize=12)
    ax2.set_xlabel('วันที่ (Date)', fontsize=12)
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    # Format แกน X
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
    ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')

    plt.tight_layout()
    plt.show()
    
    print("✅ แสดงกราฟเรียบร้อย")

except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")