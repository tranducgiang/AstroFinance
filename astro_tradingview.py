import pandas as pd
import swisseph as swe
from lightweight_charts import Chart
from datetime import datetime

# --- LOGIC CHIÊM TINH ---
# lightweight_charts không hỗ trợ trực tiếp việc vẽ vùng màu (vrect), chúng ta sẽ sử dụng vertical_line để đánh dấu sự thay đổi cung hoàng đạo
# Các ký hiệu cung hoàng đạo và các hành tinh sẽ được sử dụng để tạo nhãn trên nến hoặc dưới đáy biểu đồ.
# dung thu vien khac cho de

ZODIAC_SYMS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
DECAN_RULERS = ["♂", "☉", "♀", "☿", "☽", "♄", "♃"] * 6

def get_astro_data(df):
    markers = []
    zones = []
    last_decan = -1
    last_sign = -1

    for i, row in df.iterrows():
        dt = row['time']
        jd = swe.utc_to_jd(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)[1]
        
        # 1. Tính Mặt Trăng cho Markers (Ký hiệu trên nến)
        res_m, _ = swe.calc_ut(jd, swe.MOON)
        cur_decan = int(res_m[0] / 10)
        if cur_decan != last_decan:
            markers.append({
                'time': row['time'],
                'position': 'inBar',
                'color': '#00ffff',
                'shape': 'arrowDown',
                'text': f"{ZODIAC_SYMS[int(res_m[0]/30)]} {DECAN_RULERS[cur_decan % 7]} qqqqqq"
            })
            last_decan = cur_decan

        # 2. Tính Mặt Trời cho Vùng màu
        res_s, _ = swe.calc_ut(jd, swe.SUN)
        cur_sign = int(res_s[0] / 30)
        if cur_sign != last_sign:
            # Lưu lại điểm bắt đầu của cung mới
            color = 'rgba(255, 69, 0, 0.2)' if cur_sign in [0, 3, 6, 9] else 'rgba(128, 128, 128, 0.1)'
            zones.append({'time': row['time'], 'color': color})
            last_sign = cur_sign
            
    return markers, zones

def setup_astro_labels(chart, df):
    # 1. Tạo một series ẩn để gán nhãn
    astro_series = chart.create_line(name='Astro Labels', color='rgba(0,0,0,0)')
    
    last_decan = -1
    label_data = []

    for i, row in df.iterrows():
        dt = row['time']
        jd = swe.utc_to_jd(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)[1]
        
        output = swe.calc_ut(jd, swe.MOON)
        res_m = output[0]
        cur_decan = int(res_m[0] / 10)
        
        if cur_decan != last_decan:
            sign_sym = ZODIAC_SYMS[int(res_m[0]/30)]
            ruler_sym = DECAN_RULERS[cur_decan % 7]
            
            # GÁN VỊ TRÍ: Lấy giá Low trừ đi một khoảng (ví dụ 1% giá)
            label_price = row['low'] * 0.99 
            
            # Thêm điểm vào series ẩn
            label_data.append({'time': row['time'], 'value': label_price})
            
            # Tạo một nhãn giá cố định tại điểm đó
            astro_series.price_line(
                label_price, 
                text=f"{sign_sym}{ruler_sym}",
                color='#00F0FF'
            )
            
            last_decan = cur_decan
    
    astro_series.set(pd.DataFrame(label_data))

# --- CHƯƠNG TRÌNH CHÍNH ---
def run_chart(file_path):
    # Đọc dữ liệu
    df = pd.read_csv(file_path)
    df['time'] = pd.to_datetime(df['datetime'])
    
    # Khởi tạo Chart (TradingView Style)
    chart = Chart(inner_width=0.9, inner_height=1, toolbox=True)
    
    # Cấu hình nến
    chart.set(df)
    
    # Lấy dữ liệu Astro
    markers, zones = get_astro_data(df)
    
    # 1. Đặt Markers (Ký hiệu Decan trên đầu nến)
    #chart.marker_list(markers)
    
    # Thay vì markers, hãy gọi:
    setup_astro_labels(chart, df)

    # 2. Vẽ vùng màu (Lines/Background)
    # Lưu ý: Lightweight charts không có add_vrect trực tiếp, 
    # chúng ta dùng các đường line đứng hoặc Marker ở dưới đáy để phân vùng.
    for zone in zones:
        chart.vertical_line(zone['time'], color=zone['color'], width=2)

    # 3. Thêm EMA
    ema21 = df['close'].ewm(span=21, adjust=False).mean()
    line21 = chart.create_line(name='EMA 21', color='#FFD700')
    line21.set(pd.DataFrame({'time': df['time'], 'EMA 21': ema21}))

    # Hiển thị
    chart.show(block=True)

if __name__ == "__main__":
    # Thay đường dẫn file của bạn vào đây
    run_chart(r"d://PYTra//AstroFinance//fecth_btc_m30_1768348800000.csv")