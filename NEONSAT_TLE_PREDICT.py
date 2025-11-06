import requests
import numpy as np
import matplotlib.pyplot as plt
import datetime
#from sgp4.api import Satrec, WGS72
from sgp4.api import Satrec, WGS72, jday
import cartopy.crs as ccrs

import datetime

def fetch_tle(norad_id):
    # 간단히 Celestrak의 “satcat” 또는 기타 URL 이용
    url = f'https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}'
    resp = requests.get(url)
    resp.raise_for_status()
    lines = resp.text.strip().splitlines()
    # 보통 3줄: 이름 줄 + TLE line1 + line2
    if len(lines) >= 3:
        return lines[1], lines[2]
    else:
        raise RuntimeError(f"TLE 데이터를 가져올 수 없습니다 for NORAD {norad_id}")
    
def parse_epoch_from_tle(line1):
    # line1 예: "1 59587U 24077A   25308.62789300 ..."
    year = 2000 + int(line1[18:20])
    day_of_year = float(line1[20:32])
    epoch = datetime.datetime(year, 1, 1, tzinfo=datetime.UTC) + datetime.timedelta(days=day_of_year - 1)
    return epoch

def propagate_positions(line1, line2, start_time, minutes, step_min=1):
    sat = Satrec.twoline2rv(line1, line2, WGS72)
    times = []
    lats = []
    lons = []
    heights = []
    for dt in range(0, minutes+1, step_min):
        t = start_time + datetime.timedelta(minutes=dt)
        # Julian date
        #jd, fr = sat.sgp4_jday(t.year, t.month, t.day, t.hour, t.minute, t.second + t.microsecond*1e-6)
        jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second + t.microsecond*1e-6)

        e, r, v = sat.sgp4(jd, fr)
        if e != 0:
            # 오류 발생 시 스킵
            continue
        # r = km 단위 ECI 좌표
        x, y, z = r
        # 단순히 위도·경도 변환 (지구 중심 고정 ECEF 변환을 거치면 더 정확하지만 기본 수준에서는 근사)
        # 여기서는 numpy 이용해 단순 위도·경도 추정
        lon = np.degrees(np.arctan2(y, x))
        hyp = np.sqrt(x*x + y*y)
        lat = np.degrees(np.arctan2(z, hyp))
        height = np.sqrt(x*x + y*y + z*z) - 6371.0  # 지구 반경 ~6371 km
        times.append(t)
        lats.append(lat)
        lons.append(lon)
        heights.append(height)
    return times, lats, lons, heights

def plot_ground_track(lats, lons):
    fig = plt.figure(figsize=(10,5))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    ax.gridlines(draw_labels=True)
    ax.scatter(lons, lats, s=5, color='red', transform=ccrs.Geodetic())
    ax.set_title('Ground track of NEONSAT-1')
    plt.show()

# if __name__ == '__main__':
#     NORAD_ID = 59587
#     line1, line2 = fetch_tle(NORAD_ID)
#     print("TLE lines:")
#     print(line1)
#     print(line2)

#     #start = datetime.datetime.utcnow()
#     start = datetime.datetime.now(datetime.UTC)

#     duration_min = 90 * 3  # 예: 3회 궤도 (~90분 주기 ×3)
#     times, lats, lons, heights = propagate_positions(line1, line2, start, duration_min, step_min=1)

#     plot_ground_track(lats, lons)

if __name__ == '__main__':
    NORAD_ID = 59587
    line1, line2 = fetch_tle(NORAD_ID)
    epoch = parse_epoch_from_tle(line1)

    print("TLE lines:")
    print(line1)
    print(line2)
    print(f"\n📅 Epoch (UTC): {epoch}")
    print(f"📆 한국 시각 (KST): {epoch + datetime.timedelta(hours=9)}")

    # 유효기간 추정 (보통 ±3일)
    valid_until = epoch + datetime.timedelta(days=3)
    print(f"⏳ 예상 유효기간: ~ {valid_until + datetime.timedelta(hours=9)} (KST 기준)")

    start = datetime.datetime.now(datetime.UTC)
    duration_min = 90 * 3
    times, lats, lons, heights = propagate_positions(line1, line2, start, duration_min, step_min=1)
    plot_ground_track(lats, lons)
