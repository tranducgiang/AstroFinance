import pandas as pd
import plotly.graph_objects as go
from astro_utils import get_optimized_candle_labels, get_zodiac_zones,get_moon_decans # Import hàm từ file kia
from InternationalFixedCalendarLich13Thang import SpiritualTradingCalc,InternationalFixedCalendarLich13Thang

calc_enoch = SpiritualTradingCalc()
 
def run_app(file_path):
    # --- 1. LOAD DATA ---
    try:
        df = pd.read_csv(file_path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        
    except Exception as e:
        print(f"Lỗi file: {e}")
        return
    
    # --- TÍNH TOÁN CHỈ BÁO ---
    # Tính EMA 99 và EMA 89 (Bạn có thể đổi số tùy ý)
    df['ema99'] = df['close'].ewm(span=99, adjust=False).mean()
    df['ema89'] = df['close'].ewm(span=89, adjust=False).mean()
    df['ema200'] = df['close'].ewm(span=200, adjust=False).mean()

    # --- 2. TÍNH TOÁN VÙNG CHIÊM TINH ---
    astro_zones = get_zodiac_zones(df['datetime'].min(), df['datetime'].max())

    # --- 3. KHỞI TẠO BIỂU ĐỒ ---
    # fig = go.Figure(data=[go.Candlestick(
    #     x=df['datetime'], open=df['open'], high=df['high'], 
    #     low=df['low'], close=df['close'], name='BTC H4'
    # )])
    # --- 3. KHỞI TẠO BIỂU ĐỒ ---
    fig = go.Figure(data=[go.Candlestick(
        x=df['datetime'], 
        open=df['open'], 
        high=df['high'], 
        low=df['low'], 
        close=df['close'], 
        name='BTC H4',

    )])

    # --- 4. VẼ VÙNG VÀ VẠCH ĐỨNG (DỰA TRÊN ẢNH MẪU) ---
    for i in range(len(astro_zones)):
        z = astro_zones[i]
        last_time = int(df['datetime'].iloc[-1].timestamp() * 1000)
        next_t = astro_zones[i+1]['time'] if i+1 < len(astro_zones) else last_time
        
        # Vẽ vùng màu
        fig.add_vrect(
            x0=z['time'], x1=next_t,
            fillcolor=z['color'], layer="below", line_width=0
        )
        
        # Vẽ vạch đứng và nhãn ký hiệu
        fig.add_vline(
            x=z['time'],
            line_width=1,
            line_color="rgba(255, 255, 255, 0.2)",
            annotation_text=z['label'], # Hiển thị ♈(♂), ♉(♀)...
            annotation_position="bottom left",
            annotation_font=dict(size=18, color="white") # Tăng kích thước ký hiệu
        )


    # Trong hàm run_app của main_chart.py
    # moon_decans = get_moon_decans(df['datetime'].min(), df['datetime'].max())
    # for i in range(len(moon_decans)):
    #     d = moon_decans[i]
    #     next_t = moon_decans[i+1]['time'] if i+1 < len(moon_decans) else int(df['datetime'].iloc[-1].timestamp() * 1000)
        
    #     # Vẽ vùng Decan
    #     fig.add_vrect(
    #         x0=d['time'], x1=next_t,
    #         fillcolor=d['color'], line_width=0, layer="below"
    #     )
        
    #     # Vẽ vạch đứng mỏng và nhãn ký hiệu xếp dọc
    #     fig.add_vline(
    #         x=d['time'],
    #         line_width=0.5,
    #         line_color="rgba(255,255,255,0.2)",
    #         annotation_text=d['label'],
    #         annotation_position="top left",
    #         annotation_font=dict(size=10, color="cyan")
    #     )



    # Trong hàm run_app sau khi đã có df
    astro_labels = get_optimized_candle_labels(df)
    # Vẽ ký hiệu lên đỉnh mỗi cây nến
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['high'] + 24, # Đẩy nhãn lên trên đỉnh nến một chút
        mode="text",
        text=astro_labels, # Hien thi astro
        textposition="top center",
        # Sử dụng 'cliponaxis' để ẩn nhãn nếu nó nằm ngoài vùng nhìn thấy
        cliponaxis=True, 
        textfont=dict(size=15),
        # Giảm độ đục của nhãn để nến nổi bật hơn
        textfont_color="rgba(255, 255, 255, 1)"
        ))

    # 2. Vẽ EMA 99 (Màu vàng nhạt)
    fig.add_trace(go.Scatter(
        x=df['datetime'], y=df['ema99'],
        line=dict(color='rgba(255, 235, 59, 0.7)', width=1.5),
        name='EMA 99', visible='legendonly' # Mặc định ẩn, bám theo legend để hiện
    ))

    # 3. Vẽ EMA 89 (Màu xanh cyan)
    fig.add_trace(go.Scatter(
        x=df['datetime'], y=df['ema89'],
        line=dict(color='rgba(0, 188, 212, 0.7)', width=1.5),
        name='EMA 89', visible='legendonly' # Mặc định ẩn, bấm vào legend để hiện
    ))
    # 4. Vẽ EMA 200 (Màu xanh Tim)
    fig.add_trace(go.Scatter(
        x=df['datetime'], y=df['ema200'],
        line=dict(color='rgba(128, 0, 128, 0.7)', width=1.5),
        name='EMA 200', visible='legendonly' # Mặc định ẩn, bấm vào legend để hiện
    ))

    # --- 5. CẤU HÌNH GIAO DIỆN LAYOUT CHUẨN (PAN + CROSSHAIR) ---
    fig.update_xaxes(
        showspikes=True, 
        spikecolor="rgba(255,255,255,0.3)", 
        spikethickness=0.3, 
        spikedash="dash", 
        # 'toaxis+across' giúp đường dóng bám sát vào trục và chạy xuyên suốt biểu đồ
        spikemode="toaxis+across", 
        spikesnap="cursor", # QUAN TRỌNG: Bám theo con trỏ chuột thay vì bám vào nến

        showline=True, showgrid=True,
        gridcolor="rgba(255,255,255,0.1)"
    )

    fig.update_yaxes(
        side="right",
        #spikes là crosshair dọc theo trục Y, cũng bám theo con trỏ chuột 
        showspikes=True, 
        spikecolor="rgba(255,255,255,0.3)", 
        spikethickness=0.3, 
        spikedash="dash", 
        spikemode="toaxis+across", 
        spikesnap="cursor", # QUAN TRỌNG: Bám theo con trỏ chuột

        showline=True, showgrid=True,
        gridcolor="rgba(255,255,255,0.1)"
    )

    fig.update_layout(
        template='plotly_dark',
        dragmode='pan',
        xaxis_rangeslider_visible=False,
        hovermode='closest',
        
        # Cấu hình Trục X (Thời gian)
        xaxis=dict(
            range=[df['datetime'].iloc[-800], df['datetime'].iloc[-1]],
            type='date',
            # Cho phép cuộn chuột để Zoom trong khi vẫn đang ở chế độ Pan
            fixedrange=False 
        ),
    )

    # --- 4c. VẼ VẠCH THỨ HAI HÀNG TUẦN (ENOCH) ---
    enoch_mondays = calc_enoch.get_enoch_mondays(df['datetime'].min(), df['datetime'].max())
    for mon in enoch_mondays:
        # Gọi hàm kiểm tra Tiết điểm (Xuân phân, Hạ chí...)
        solar_event = calc_enoch.get_solar_event(mon['date_obj'] )

        fig.add_vline(
            x=mon['time'],
            line_width=1,
            line_dash="dash", # Nét đứt
            line_color="white", # Màu xanh dương theo yêu cầu
            opacity=0.75,
            annotation_text=f"{mon['label']}{solar_event}", # Sẽ hiện: Thứ 2, 1/1 [Xuân Phân]            annotation_position="top right",
            annotation_font=dict(size=14, color="white"),
            layer="below" # Vẽ dưới nến để tránh rối mắt
        )

    # Hiển thị
    config = {'scrollZoom': True, 'displaylogo': False}
    fig.show(config=config)

# Chạy chương trình
if __name__ == "__main__":
    run_app("d:\\PYTra\\AstroFInance\\fetch_btc_USDT_1h.csv")