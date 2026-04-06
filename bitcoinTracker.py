import ccxt
import pandas as pd
import datetime
import time

def fetch_btc_h4_data():
    exchange = ccxt.binance()
    symbol = 'BTC/USDT'#'PAXG/USDT'#'BTC/USDT'
    timeframe = '1h' 
    
    # 1. Tải dữ liệu thực tế
    since = exchange.parse8601((datetime.datetime.utcnow() - datetime.timedelta(days=180)).isoformat())
    all_ohlcv = []
    
    while since < exchange.milliseconds():
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)
            if not ohlcv: break
            since = ohlcv[-1][0] + 1 
            all_ohlcv.extend(ohlcv)
            time.sleep(exchange.rateLimit / 1000)
        except Exception as e:
            print(f"Lỗi: {e}"); break

    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True).dt.tz_localize(None)

    # --- PHẦN CHÈN THÊM 1 THÁNG TỚI ---
    print("⏳ Đang chèn thêm dữ liệu dự báo cho 1 tháng tới...")
    
    last_row = df.iloc[-1]
    last_time = last_row['datetime']
    current_price = last_row['close'] # Lấy giá đóng cửa hiện tại làm mốc
    
    # Tạo danh sách các mốc thời gian tiếp theo (mỗi mốc cách nhau theo timeframe)
    # Ở đây dùng 'H' vì timeframe là 1h, nếu dùng 4h thì đổi thành '4H'
    future_dates = pd.date_range(
        start=last_time + pd.Timedelta(hours=1), 
        periods=24 * 30, # 24 giờ * 30 ngày
        freq='H'
    )
    
    # Tạo DataFrame tương lai với giá bằng giá hiện tại
    future_df = pd.DataFrame({
        'datetime': future_dates,
        'open': current_price,
        'high': current_price,
        'low': current_price,
        'close': current_price,
        'volume': 0 # Volume tương lai để bằng 0
    })
    
    # Nối dữ liệu thực và dữ liệu ảo
    df_final = pd.concat([df, future_df], ignore_index=True)

    # Lưu và hoàn tất
    filename = "fetch_btc_USDT_1h.csv"
    df_final[['datetime', 'open', 'high', 'low', 'close', 'volume']].to_csv(filename, index=False)
    #print(f"✅ Đã lưu {len(df_final)} dòng (bao gồm 1 tháng tương lai) vào {filename}")
    
    return df_final

# Chạy hàm
btc_df = fetch_btc_h4_data()
print(btc_df.head()) # Hiển thị 5 dòng đầu tiên