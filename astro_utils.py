import swisseph as swe
import pandas as pd
from datetime import datetime

def get_zodiac_zones(start_dt, end_dt):
    zones = []
    zodiac_symbols = [
        "♈(♂)", "♉(♀)", "♊(☿)", "♋(☽)", 
        "♌(☉)", "♍(☿)", "♎(♀)", "♏(♇)", 
        "♐(♃)", "♑(♄)", "♒(♅)", "♓(♆)"
    ]
    
    # Màu sắc: 0, 3, 6, 9 (Cardinal) cùng màu cam đỏ
    cardinal_color = "rgba(255, 69, 0, 0.2)"
    other_colors = [
        cardinal_color,            # 0. Bạch Dương
        "rgba(128, 128, 128, 0.1)", # 1. Kim Ngưu
        "rgba(0, 255, 127, 0.08)", # 2. Song Tử
        cardinal_color,            # 3. Cự Giải
        "rgba(147, 112, 219, 0.12)",# 4. Sư Tử
        "rgba(255, 20, 147, 0.12)", # 5. Xử Nữ
        cardinal_color,            # 6. Thiên Bình
        "rgba(218, 112, 214, 0.1)", # 7. Bọ Cạp
        "rgba(65, 105, 225, 0.12)", # 8. Nhân Mã
        cardinal_color,            # 9. Ma Kết
        "rgba(0, 206, 209, 0.1)",  # 10. Bảo Bình
        "rgba(128, 128, 128, 0.1)"  # 11. Song Ngư
    ]

    # Chuyển đổi start_dt sang Julian Day
    jd_start = swe.utc_to_jd(start_dt.year, start_dt.month, start_dt.day, 
                             start_dt.hour, start_dt.minute, start_dt.second)[1]
    jd_end = swe.utc_to_jd(end_dt.year, end_dt.month, end_dt.day, 
                           end_dt.hour, end_dt.minute, end_dt.second)[1]

    # Xác định cung hiện tại của điểm bắt đầu
    res, _ = swe.calc_ut(jd_start, swe.SUN)
    current_sign = int(res[0] / 30)
    
    # Thêm vùng đầu tiên từ mốc bắt đầu
    y, m, d, h_dec = swe.revjul(jd_start)
    dt_start = datetime(y, m, int(d), int(h_dec), int((h_dec % 1) * 60))
    zones.append({
        'time': int(dt_start.timestamp() * 1000),
        'color': other_colors[current_sign],
        'label': zodiac_symbols[current_sign]
    })

    # Tìm các điểm chuyển cung (Ingress) tiếp theo
    curr_jd = jd_start
    while curr_jd < jd_end:
        # Tìm tọa độ kinh độ Mặt Trời hiện tại
        res, _ = swe.calc_ut(curr_jd, swe.SUN)
        next_ingress_degree = (int(res[0] / 30) + 1) * 30
        if next_ingress_degree >= 360: next_ingress_degree = 0
        
        # Dùng solcross để tìm chính xác thời điểm Mặt Trời chạm độ tiếp theo (0, 30, 60...)
        # Đây là thuật toán chính xác nhất thay vì cộng ngày cố định
        next_ingress_jd = swe.solcross(next_ingress_degree, curr_jd, 0)
        
        if next_ingress_jd > jd_end:
            break
            
        y, m, d, h_dec = swe.revjul(next_ingress_jd)
        hh = int(h_dec)
        mm = int((h_dec - hh) * 60)
        dt_obj = datetime(y, m, int(d), hh, mm)
        
        # Xác định cung tại điểm vừa tìm được
        res_check, _ = swe.calc_ut(next_ingress_jd + 0.001, swe.SUN) # Cộng sai số nhỏ để vào hẳn cung mới
        sign_idx = int(res_check[0] / 30)
        
        zones.append({
            'time': int(dt_obj.timestamp() * 1000), 
            'color': other_colors[sign_idx],
            'label': zodiac_symbols[sign_idx]
        })
        
        curr_jd = next_ingress_jd + 1 # Nhảy qua điểm vừa tìm để tìm điểm kế tiếp
        
    return zones

# Hàm này ko dùng tới
def get_moon_decans(start_dt, end_dt):
    decans = []
    # Ký hiệu 12 cung
    zodiac_syms = ["♈", "♉", " ♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
    # Ký hiệu 7 hành tinh cổ điển chủ quản Decan (Chaldean order)
    planet_syms = ["♂", "☉", "♀", "☿", "☽", "♄", "♃"]
    
    # Bảng tra cứu hành tinh chủ quản cho 36 Decan (Bắt đầu từ 0 độ Bạch Dương)
    # Thứ tự: Hỏa, Nhật, Kim, Thủy, Nguyệt, Thổ, Mộc... lặp lại
    decan_rulers = [
        "♂", "☉", "♀", "☿", "☽", "♄", "♃", "♂", "☉", "♀", "☿", "☽", "♄", "♃", "♂", "☉", "♀", "☿", "☽", "♄", "♃", "♂", "☉", "♀", "☿", "☽", "♄", "♃", "♂", "☉", "♀", "☿", "☽", "♄", "♃", "♂"
    ]

    # Định nghĩa 4 Nguyên tố: Icon và Màu sắc đặc trưng
    # Hỏa (Fire): Bạch Dương(0), Sư Tử(4), Nhân Mã(8)
    # Thổ (Earth): Kim Ngưu(1), Xử Nữ(5), Ma Kết(9)
    # Phong (Air): Song Tử(2), Thiên Bình(6), Bảo Bình(10)
    # Thủy (Water): Cự Giải(3), Bọ Cạp(7), Song Ngư(11)
    elements = {
        0: {"icon": "🔥", "color": "#FF4500"}, # Fire
        4: {"icon": "🔥", "color": "#FF4500"},
        8: {"icon": "🔥", "color": "#FF4500"},
        1: {"icon": "🌱", "color": "#A2CD5A"}, # Earth
        5: {"icon": "🌱", "color": "#A2CD5A"},
        9: {"icon": "🌱", "color": "#A2CD5A"},
        2: {"icon": "🌬️", "color": "#00CED1"}, # Air
        6: {"icon": "🌬️", "color": "#00CED1"},
        10: {"icon": "🌬️", "color": "#00CED1"},
        3: {"icon": "💧", "color": "#1E90FF"}, # Water
        7: {"icon": "💧", "color": "#1E90FF"},
        11: {"icon": "💧", "color": "#1E90FF"}
    }

    jd_start = swe.utc_to_jd(start_dt.year, start_dt.month, start_dt.day, start_dt.hour, start_dt.minute, start_dt.second)[1]
    jd_end = swe.utc_to_jd(end_dt.year, end_dt.month, end_dt.day, end_dt.hour, end_dt.minute, end_dt.second)[1]

    curr_jd = jd_start
    while curr_jd < jd_end:
        # Tính vị trí Mặt Trăng
        res, _ = swe.calc_ut(curr_jd, swe.MOON)
        lon = res[0]
        
        sign_idx = int(lon / 30)
        decan_idx = int(lon / 10) # 0 đến 35
        #elem = elements.get(sign_idx)        # Lấy thông tin nguyên tố dựa trên sign_idx
        #print(f"Debug: JD={curr_jd}, Lon={lon:.2f}, Sign={sign_idx}, Decan={decan_idx}, Element={elem['icon'] if elem else 'N/A'}")

        y, m, d, h_dec = swe.revjul(curr_jd)
        dt_obj = datetime(y, m, int(d), int(h_dec), int((h_dec % 1) * 60))
        
        # Tạo nhãn: Ký hiệu Cung + Ký hiệu Sao chủ quản Decan
        label = f"{zodiac_syms[sign_idx]}\n{decan_rulers[decan_idx]}\n{'111111'}"
        
        decans.append({
            'time': int(dt_obj.timestamp() * 1000),
            'label': label,
            'color': "rgba(255, 255, 255, 0.15)" if decan_idx % 3 == 0 else "rgba(255, 255, 255, 0.05)"
        })
        
        # Mặt trăng đi 10 độ mất khoảng 18-20 giờ, ta nhảy bước nhỏ để quét
        # Tìm chính xác điểm 10 độ tiếp theo (Ingress Decan)
        target_lon = (decan_idx + 1) * 10
        if target_lon >= 360: target_lon = 0
        
        # Tìm thời điểm chạm mốc 10 độ kế tiếp
        curr_jd = swe.solcross(target_lon, curr_jd, 0) # Dùng solcross cho chính xác mốc tọa độ
        if curr_jd == 0: # Phòng hờ lỗi tìm kiếm
            curr_jd += 0.8 

    return decans
    phases = []
    
    jd_start = swe.utc_to_jd(start_dt.year, start_dt.month, start_dt.day, 
                             start_dt.hour, start_dt.minute, start_dt.second)[1]
    jd_end = swe.utc_to_jd(end_dt.year, end_dt.month, end_dt.day, 
                           end_dt.hour, end_dt.minute, end_dt.second)[1]
    
    curr_jd = jd_start
    while curr_jd < jd_end:
        # Tìm điểm New Moon (0) và Full Moon (180) tiếp theo
        # Dùng bước nhảy lớn để tìm vùng, sau đó thu hẹp độ chính xác
        res_sun, _ = swe.calc_ut(curr_jd, swe.SUN)
        res_moon, _ = swe.calc_ut(curr_jd, swe.MOON)
        
        # Khoảng cách góc hiện tại
        diff = (res_moon[0] - res_sun[0]) % 360
        
        # Kiểm tra nếu gần điểm 0 hoặc 180 (sai số nhỏ để khớp nến H4)
        if abs(diff - 0) < 2 or abs(diff - 180) < 2:
            y, m, d, h_dec = swe.revjul(curr_jd)
            dt_obj = datetime(y, m, int(d), int(h_dec), int((h_dec % 1) * 60))
            
            phases.append({
                'time': int(dt_obj.timestamp() * 1000),
                'label': "🌑" if abs(diff - 0) < 2 else "🌕",
                'type': 'New' if abs(diff - 0) < 2 else 'Full'
            })
            curr_jd += 14 # Nhảy cách nửa tháng để tìm điểm tiếp theo
        else:
            curr_jd += 0.1 # Quét dần
            
    return phases

def get_optimized_candle_labels(df):
    labels = []
    last_decan = -1
    last_quadrant = -1 # Để theo dõi các góc 0, 90, 180, 270
    
    # Ký hiệu 12 cung và 7 hành tinh chủ quản (Chaldean Order)
    zodiac_syms = ["♈", "♉", " ♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
    decan_rulers = ["♂", "☉", "♀", "☿", "☽", "♄", "♃"] * 6 

    # Định nghĩa 4 Nguyên tố
    elements = {
        0: {"icon": "🔥", "color": "#FF4500"}, # Fire
        4: {"icon": "🔥", "color": "#FF4500"},
        8: {"icon": "🔥", "color": "#FF4500"},
        1: {"icon": "🌱", "color": "#A2CD5A"}, # Earth
        5: {"icon": "🌱", "color": "#A2CD5A"},
        9: {"icon": "🌱", "color": "#A2CD5A"},
        2: {"icon": "🌬️", "color": "#00CED1"}, # Air
        6: {"icon": "🌬️", "color": "#00CED1"},
        10: {"icon": "🌬️", "color": "#00CED1"},
        3: {"icon": "💧", "color": "#1E90FF"}, # Water
        7: {"icon": "💧", "color": "#1E90FF"},
        11: {"icon": "💧", "color": "#1E90FF"}
    }

    for index, row in df.iterrows():
        dt = row['datetime']
        jd = swe.utc_to_jd(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)[1]
        
        # Lấy vị trí Mặt Trăng (Longitude)
        res, _ = swe.calc_ut(jd, swe.MOON)
        lon = res[0]
        
        current_decan = int(lon / 10) # 0-35
        current_quadrant = int(lon / 90) # 0, 1, 2, 3 tương ứng các góc 0, 90, 180, 270

        # --- LOGIC TIẾP TỤC TẠI ĐÂY ---
        
        # 1. Kiểm tra nếu bước sang Decan mới HOẶC chạm góc đặc biệt (Quadrants)
        is_new_decan = current_decan != last_decan
        is_special_angle = current_quadrant != last_quadrant
        
        if is_new_decan or is_special_angle:
            sign_idx = int(lon / 30)
            elem = elements.get(sign_idx)
            ruler = decan_rulers[current_decan % 7]
            
            # Nếu là góc đặc biệt 0, 90, 180, 270, ta thêm ký hiệu nhấn mạnh
            angle_mark = ""
            if is_special_angle:
                # Xác định chính xác góc nào
                angle = current_quadrant * 90
                angle_mark = f"<b>[ {angle}° ]</b><br>" 
            
            # Tạo nhãn: Góc đặc biệt (nếu có) + Nguyên tố + Cung + Sao chủ quản
            labels.append(f"{angle_mark}{elem['icon']}<br>{zodiac_syms[sign_idx]}<br>{ruler}")
            
            # Cập nhật trạng thái cuối cùng
            last_decan = current_decan
            last_quadrant = current_quadrant
        else:
            labels.append(None) 
            
    return labels