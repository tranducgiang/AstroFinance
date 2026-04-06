import swisseph as swe
import datetime
import time


# Định nghĩa các hành tinh cai quản Decan theo hệ thống Chaldean (truyền thống)
# Thứ tự: Hỏa (Mars), Mặt Trời (Sun), Kim (Venus), Thủy (Mercury), Nguyệt (Moon), Thổ (Saturn), Mộc (Jupiter)
DECAN_RULERS = ["Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter"]

ZODIAC_SIGNS = [
    ("Aries", "♈"),        ("Taurus", "♉"),       ("Gemini", "♊"),   ("Cancer", "♋"),
    ("Leo", "♌"),          ("Virgo", "♍"),        ("Libra", "♎"),    ("Scorpio", "♏"),
    ("Sagittarius", "♐"),  ("Capricorn", "♑"),    ("Aquarius", "♒"), ("Pisces", "♓")
]

PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "🌙", "Mars": "♂", "Venus": "♀", 
    "Mercury": "☿", "Jupiter": "♃", "Saturn": "♄"
}
def get_decan_ruler(total_degree):
    # Mỗi Decan rộng 10 độ, có tổng cộng 36 Decan trong vòng tròn 360 độ
    decan_index = int(total_degree / 10)
    # Quy luật Chaldean lặp lại sau mỗi 7 hành tinh
    ruler_name = DECAN_RULERS[decan_index % 7]
    return ruler_name, PLANET_SYMBOLS.get(ruler_name, "")

def monitor_astro():
    print(f"{'THỜI GIAN (VN)':<20} | {'HÀNH TINH':<10} | {'VỊ TRÍ':<15} | {'DECAN RULER'}")
    print("-" * 70)
    
    try:
        while True:
            # Lấy thời gian hiện tại
            now_vn = datetime.datetime.now()
            # Chuyển sang UTC để tính toán thiên văn (VN = UTC + 7)
            now_utc = now_vn - datetime.timedelta(hours=7)
            
            jd = swe.julday(now_utc.year, now_utc.month, now_utc.day, 
                            now_utc.hour + now_utc.minute/60 + now_utc.second/3600)

            for p_name, p_code in [("Sun", swe.SUN), ("Moon", swe.MOON)]:
                res, _ = swe.calc_ut(jd, p_code)
                lon = res[0]
                
                sign_idx = int(lon / 30)
                sign_name, sign_sym = ZODIAC_SIGNS[sign_idx]
                ruler_name, ruler_sym = get_decan_ruler(lon)
                
                p_sym = PLANET_SYMBOLS[p_name]
                pos_str = f"{p_sym} {sign_sym}"
                ruler_display = f"{ruler_sym} ({ruler_name})"
                
                print(f"{now_vn.strftime('%H:%M:%S'):<20}| {p_name:<10} | {pos_str:<15}  | {ruler_display}")
            
            print("-" * 70)
            time.sleep(5) # Đợi 5 giây trước khi cập nhật tiếp
            
    except KeyboardInterrupt:
        print("\nĐã dừng chương trình.")

def get_astro_data(date_time):
    # 1. Chuyển đổi thời gian sang Giờ Julian (chuẩn thiên văn)
    jd = swe.julday(date_time.year, date_time.month, date_time.day, 
                    date_time.hour + date_time.minute/60)

    # Danh sách các hành tinh cần lấy dữ liệu
    planets = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER
    }

    results = {}
    
    # 12 Cung Hoàng Đạo
    zodiac_signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    for name, code in planets.items():
        # 2. Tính toán vị trí hành tinh
        # res[0] là Longitude (Kinh độ thiên văn từ 0-360)
        res, err = swe.calc_ut(jd, code)
        lon = res[0]
        
        # 3. Xác định Cung và Decan
        sign_idx = int(lon / 30)
        decan_idx = int((lon % 30) / 10) + 1 # Decan 1, 2 hoặc 3
        
        results[name] = {
            "Degree": round(lon, 2),
            "Sign": zodiac_signs[sign_idx],
            "Decan": decan_idx
        }
        
    return results

def get_detailed_astro_pos(year, month, day, hour, minute, second):
    # 1. Thiết lập thời gian theo định dạng UTC (Chuẩn thiên văn)
    # Nếu bạn dùng giờ Việt Nam, hãy trừ đi 7 (UTC = Giờ VN - 7)
    dt = datetime.datetime(year, month, day, hour, minute, second)
    
    # Chuyển đổi sang giờ Julian (Julian Day)
    jd = swe.julday(year, month, day, hour + minute/60 + second/3600)

    # 12 Cung Hoàng Đạo
    zodiac_signs = [
        "Bạch Dương (Aries)", "Kim Ngưu (Taurus)", "Song Tử (Gemini)", 
        "Cự Giải (Cancer)", "Sư Tử (Leo)", "Xử Nữ (Virgo)",
        "Thiên Bình (Libra)", "Bọ Cạp (Scorpio)", "Nhân Mã (Sagittarius)", 
        "Ma Kết (Capricorn)", "Bảo Bình (Aquarius)", "Song Ngư (Pisces)"
    ]

    def calculate_body(body_code, name):
        # Tính toán vị trí hành tinh
        res, err = swe.calc_ut(jd, body_code)
        lon = res[0] # Kinh độ thiên văn 0-360
        
        sign_idx = int(lon / 30)
        degree_in_sign = lon % 30
        decan = int(degree_in_sign / 10) + 1
        
        return {
            "name": name,
            "total_degree": round(lon, 2),
            "sign": zodiac_signs[sign_idx],
            "sign_degree": round(degree_in_sign, 2),
            "decan": decan
        }

    # Tính cho Mặt Trời và Mặt Trăng
    sun_data = calculate_body(swe.SUN, "Mặt Trời")
    moon_data = calculate_body(swe.MOON, "Mặt Trăng")

    return dt, sun_data, moon_data

def find_time_from_angle(target_angle, planet_code, start_date):
    # Thiết lập thời gian bắt đầu quét (UTC)
    jd = swe.julday(start_date.year, start_date.month, start_date.day, start_date.hour)
    
    current_jd = jd
    found = False
    
    print(f"Đang tìm kiếm thời điểm hành tinh đạt {target_angle}°...")

    # Quét trong vòng 365 ngày tiếp theo (mỗi bước nhảy 1 phút = 1/1440 ngày)
    for _ in range(365 * 1440):
        res, err = swe.calc_ut(current_jd, planet_code)
        current_lon = res[0]
        
        # Kiểm tra sai số (ngưỡng 0.01 độ để chính xác đến từng phút)
        if abs(current_lon - target_angle) < 0.01:
            # Chuyển đổi ngược từ Julian Day sang ngày giờ
            y, m, d, h_float = swe.revjul(current_jd)
            
            # Tính toán giờ, phút, giây từ số thập phân
            hour = int(h_float)
            minute = int((h_float - hour) * 60)
            second = int(((h_float - hour) * 60 - minute) * 60)
            
            result_dt = datetime.datetime(y, m, d, hour, minute, second)
            return result_dt
            
        current_jd += (1 / 1440) # Tiến thêm 1 phút
    
    return None

# cai nay nhap vao nam ra tat ca ngay ma mat troi va mat trang vao cung nao trong nam do
def get_zodiac_ingress(year, planet_name):
    planet_code = swe.SUN if planet_name.lower() == "sun" else swe.MOON
    
    # Thiết lập thời gian bắt đầu: 1/1 của năm đó (UTC)
    jd = swe.julday(year, 1, 1, 0)
    
    zodiac_signs = [
        "Bạch Dương (Aries)", "Kim Ngưu (Taurus)", "Song Tử (Gemini)", 
        "Cự Giải (Cancer)", "Sư Tử (Leo)", "Xử Nữ (Virgo)",
        "Thiên Bình (Libra)", "Bọ Cạp (Scorpio)", "Nhân Mã (Sagittarius)", 
        "Ma Kết (Capricorn)", "Bảo Bình (Aquarius)", "Song Ngư (Pisces)"
    ]

    ingress_list = []
    
    # Lấy vị trí ban đầu
    res, _ = swe.calc_ut(jd, planet_code)
    last_sign_idx = int(res[0] / 30)

    # Quét theo bước nhảy (Mặt trời: 1 giờ, Mặt trăng: 5 phút để chính xác hơn)
    step = (1/24) if planet_code == swe.SUN else (5 / 1440)
    
    # Quét trong khoảng 366 ngày (để bao phủ cả năm nhuận)
    current_jd = jd
    end_jd = jd + 366

    while current_jd < end_jd:
        res, _ = swe.calc_ut(current_jd, planet_code)
        current_lon = res[0]
        current_sign_idx = int(current_lon / 30)

        # Nếu chỉ số cung thay đổi, nghĩa là đã bước sang cung mới
        if current_sign_idx != last_sign_idx:
            y, m, d, h_float = swe.revjul(current_jd)
            
            # Kiểm tra xem có còn nằm trong năm yêu cầu không
            if y > year: break
            
            hour = int(h_float)
            minute = int((h_float - hour) * 60)
            
            dt_utc = datetime.datetime(y, m, d, hour, minute)
            # Chuyển sang giờ Việt Nam (UTC+7)
            dt_vn = dt_utc + datetime.timedelta(hours=7)
            
            ingress_list.append({
                "time": dt_vn.strftime("%d/%m/%Y %H:%M"),
                "new_sign": zodiac_signs[current_sign_idx]
            })
            
            last_sign_idx = current_sign_idx
            
        current_jd += step

    return ingress_list



# --- CHẠY CHƯƠNG TRÌNH ---
print("--- TÌM NGÀY TỪ GÓC ĐỘ (CLOCK OF LIFE) ---")
angle = float(input("Nhập góc muốn tìm (0-359.9): "))
planet_choice = input("Tìm cho (Sun/Moon): ").lower()
p_code = swe.SUN if planet_choice == "sun" else swe.MOON

# --- CHẠY THỬ ---
# Lấy thời gian hiện tại từ hệ thống (hoặc nhập ngày lịch sử như 6/8/1945)
now = datetime.datetime.now()
data = get_astro_data(now)


print(f"--- ASTRO CLOCK: {now} ---")
for p, info in data.items():
    print(f"{p}: {info['Degree']}° | {info['Sign']} (Decan {info['Decan']})")

#
if __name__ == "__main__":
    monitor_astro()

# --- PHẦN NHẬP DỮ LIỆU ---
# print("--- NHẬP THỜI GIAN MUỐN KIỂM TRA ---")
# y = int(input("Năm (YYYY): "))
# m = int(input("Tháng (MM): "))
# d = int(input("Ngày (DD): "))
# h = int(input("Giờ (0-23): "))
# mi = int(input("Phút (0-59): "))
# s = int(input("Giây (0-59): "))

# dt_obj, sun, moon = get_detailed_astro_pos(y, m, d, h, mi, s)

# print(f"\n[Kết quả cho ngày: {dt_obj}]")
# print(f"☀️ {sun['name']}: {sun['total_degree']}° trên Clock | Thuộc {sun['sign']} | Độ trong cung: {sun['sign_degree']}° | Decan: {sun['decan']}")
# print(f"🌙 {moon['name']}: {moon['total_degree']}° trên Clock | Thuộc {moon['sign']} | Độ trong cung: {moon['sign_degree']}° | Decan: {moon['decan']}")


# Nhập mốc bắt đầu tìm kiếm (để tránh ra kết quả quá khứ)
# start_y = int(input("Bắt đầu tìm từ năm nào (YYYY): "))
# start_date = datetime.datetime(start_y, 1, 1)

# result = find_time_from_angle(angle, p_code, start_date)

# if result:
#     # Nếu là giờ VN, hãy cộng thêm 7
#     print(f"\n✅ Kết quả tìm thấy (Giờ UTC): {result}")
#     print(f"👉 Giờ Việt Nam dự kiến: {result + datetime.timedelta(hours=7)}")
# else:
#     print("\n❌ Không tìm thấy thời điểm nào khớp trong vòng 1 năm kể từ mốc bắt đầu.")



# --- CHẠY CHƯƠNG TRÌNH ---
# year_input = int(input("Nhập năm bạn muốn lập danh sách: "))

# print(f"\n--- DANH SÁCH CHUYỂN CUNG CỦA MẶT TRỜI (SUN) NĂM {year_input} ---")
# sun_list = get_zodiac_ingress(year_input, "sun")
# for item in sun_list:
#     print(f"📅 {item['time']} -> Sang cung: {item['new_sign']}")

# print(f"\n--- DANH SÁCH CHUYỂN CUNG CỦA MẶT TRĂNG (MOON) NĂM {year_input} ---")
# moon_list = get_zodiac_ingress(year_input, "moon")
# # In 10 mốc đầu tiên của Mặt Trăng vì danh sách rất dài (~13 lần chuyển mỗi cung)
# for item in moon_list[:15]: 
#     print(f"🌙 {item['time']} -> Sang cung: {item['new_sign']}")
# print("... (Danh sách còn tiếp)")