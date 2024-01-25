# SPDX-FileCopyrightText: 2020 Carter Nelson for Adafruit Industries
#
# SPDX-License-Identifier: MIT
# pylint: disable=redefined-outer-name, eval-used, wrong-import-order

import time
import terminalio
import displayio
import adafruit_imageload
from adafruit_display_text import label
from adafruit_magtag.magtag import MagTag
from secrets import secrets

# --| USER CONFIG |--------------------------
METRIC = False  # set to True for metric units
# -------------------------------------------

# ----------------------------
# Define various assets
# ----------------------------
BACKGROUND_BMP = "/bmps/weather_bg.bmp"
ICONS_LARGE_FILE = "/bmps/weather_icons_70px.bmp"
ICONS_SMALL_FILE = "/bmps/weather_icons_20px.bmp"
ICON_MAP = ("01", "02", "03", "04", "09", "10", "11", "13", "50")
DAYS = ("Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun")
MONTHS = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)
magtag = MagTag()

# ----------------------------
# Backgrounnd bitmap
# ----------------------------
magtag.graphics.set_background(BACKGROUND_BMP)

# ----------------------------
# Weather icons sprite sheet
# ----------------------------
icons_large_bmp, icons_large_pal = adafruit_imageload.load(ICONS_LARGE_FILE)
icons_small_bmp, icons_small_pal = adafruit_imageload.load(ICONS_SMALL_FILE)

# /////////////////////////////////////////////////////////////////////////


def get_data_source_url(api="onecall", location=None):
    """Build and return the URL for the OpenWeather API."""
    if api.upper() == "GEO":
        URL = "https://api.openweathermap.org/geo/1.0/direct?q="
        URL += location
    elif api.upper() == "GEOREV":
        URL = "https://api.openweathermap.org/geo/1.0/reverse?limit=1"
        URL += "&lat={}".format(location[0])
        URL += "&lon={}".format(location[1])
    elif api.upper() == "ONECALL":
        URL = "https://api.openweathermap.org/data/3.0/onecall?exclude=minutely,hourly,alerts"
        URL += "&lat={}".format(location[0])
        URL += "&lon={}".format(location[1])
    else:
        raise ValueError("Unknown API type: " + api)
    return URL + "&appid=" + secrets["openweather_token"]


def get_latlon(city_name):
    """Use the Geolocation API to determine lat/lon for given city."""
    magtag.url = get_data_source_url(api="geo", location=city_name)
    raw_data = eval(magtag.fetch())[0]
    return raw_data["lat"], raw_data["lon"]


def get_city(latlon_location):
    """Use the Geolocation API to determine city for given lat/lon."""
    magtag.url = get_data_source_url(api="georev", location=latlon_location)
    raw_data = eval(magtag.fetch())[0]
    return raw_data["name"] + ", " + raw_data["country"]


def get_forecast(location):
    """Use OneCall API to fetch forecast and timezone data."""
    resp = magtag.network.fetch(get_data_source_url(api="onecall", location=location))
    json_data = resp.json()
    return json_data["daily"], json_data["current"], json_data["current"]["dt"], json_data["timezone_offset"]


def make_banner(x=0, y=0):
    """Make a single future forecast info banner group."""
    day_of_week = label.Label(terminalio.FONT, text="DAY", color=0x000000)
    day_of_week.anchor_point = (0, 0.5)
    day_of_week.anchored_position = (0, 11)

    icon = displayio.TileGrid(
        icons_small_bmp,
        pixel_shader=icons_small_pal,
        x=21,
        y=1,
        width=1,
        height=1,
        tile_width=20,
        tile_height=20,
    )

    day_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
    day_temp.anchor_point = (0, 0.5)
    day_temp.anchored_position = (44, 10)

    group = displayio.Group(x=x, y=y)
    group.append(day_of_week)
    group.append(icon)
    group.append(day_temp)

    return group


def temperature_text(tempK):
    if METRIC:
        return "{:3.0f}C".format(tempK - 273.15)
    else:
        return "{:3.0f}".format(32.0 + 1.8 * (tempK - 273.15))


def wind_text(speedms):
    if METRIC:
        return "{:3.0f}m/s".format(speedms)
    else:
        return "{:3.0f}mph".format(2.23694 * speedms)


def update_banner(banner, data):
    """Update supplied forecast banner with supplied data."""
    banner[0].text = DAYS[time.localtime(data["dt"]).tm_wday][:3].upper()
    banner[1][0] = ICON_MAP.index(data["weather"][0]["icon"][:2])
    banner[2].text = temperature_text(data["temp"]["min"])+"/"+temperature_text(data["temp"]["max"])


def update_today(data, tz_offset=0):
    """Update today info banner."""
    today_min_temp.text = temperature_text(data["temp"]["min"])
    today_max_temp.text = temperature_text(data["temp"]["max"])
    #today_pop.text = "{2d}%".format(data["pop"])

def update_now(data, tz_offset=0):
    """Update hourly info banner."""
    date = time.localtime(data["dt"])
    sunrise = time.localtime(data["sunrise"] + tz_offset)
    sunset = time.localtime(data["sunset"] + tz_offset)

    today_date.text = "{} {} {}, {}".format(
        DAYS[date.tm_wday].upper(),
        MONTHS[date.tm_mon - 1].upper(),
        date.tm_mday,
        date.tm_year,
    )
    today_icon[0] = ICON_MAP.index(data["weather"][0]["icon"][:2])
    #today_description.text = data["weather"]["main"]
    today_cur_temp.text = temperature_text(data["temp"])
    today_pressure.text = "{:4d}mb".format(data["pressure"])
    today_humidity.text = "{:3d}%".format(data["humidity"])
    today_wind.text = wind_text(data["wind_speed"])
    today_clouds.text = "{:3d}%".format(data["clouds"])
    #today_uvi.text - "{:3d}%".format(data["uvi"])
    today_sunrise.text = "{:2d}:{:02d} AM".format(sunrise.tm_hour, sunrise.tm_min)
    today_sunset.text = "{:2d}:{:02d} PM".format(sunset.tm_hour - 12, sunset.tm_min)

def go_to_sleep(current_time):
    """Enter deep sleep for time needed."""
       # wake up in one hour
    seconds_to_sleep = (1 * 60 * 60 )
    print(
        "Sleeping for {} hours, {} minutes".format(
            seconds_to_sleep // 3600, (seconds_to_sleep // 60) % 60
        )
    )
    magtag.exit_and_deep_sleep(seconds_to_sleep)


# ===========
# Location
# ===========
if isinstance(secrets["openweather_location"], str):
    # Get lat/lon using city name
    city = secrets["openweather_location"]
    print("Getting lat/lon for city:", city)
    latlon = get_latlon(city)
elif isinstance(secrets["openweather_location"], tuple):
    # Get city name using lat/lon
    latlon = secrets["openweather_location"]
    print("Getting city name for lat/lon:", latlon)
    city = get_city(latlon)
else:
    raise ValueError("Unknown location:", secrets["openweather_location"])

print("City =", city)
print("Lat/Lon = ", latlon)

# ===========
# U I
# ===========
today_date = label.Label(terminalio.FONT, text="?" * 30, color=0x000000)
today_date.anchor_point = (0, 0)
today_date.anchored_position = (15, 13)

city_name = label.Label(terminalio.FONT, text=city, color=0x000000)
city_name.anchor_point = (0, 0)
city_name.anchored_position = (15, 22)

today_icon = displayio.TileGrid(
    icons_large_bmp,
    pixel_shader=icons_small_pal,
    x=10,
    y=33,
    width=1,
    height=1,
    tile_width=70,
    tile_height=70,
)

today_description = label.Label(terminalio.FONT, text="Thunderstorm", color=0x000000)
today_description.anchor_point = (0.5,1)
today_description.anchored_position = (47,115)

today_cur_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
today_cur_temp.anchor_point = (0, 0)
today_cur_temp.anchored_position = (150, 24)

today_min_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
today_min_temp.anchor_point = (0, 0)
today_min_temp.anchored_position = (100, 50)

today_max_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
today_max_temp.anchor_point = (0, 0)
today_max_temp.anchored_position = (130, 50)

#today_pop = label.Label(terminalio.FONT, text="100%", color=0x000000)
#today_pop.anchor_point = (0, 0)
#today_pop.anchored_position = (165, 50)

today_humidity = label.Label(terminalio.FONT, text="100%", color=0x000000)
today_humidity.anchor_point = (0, 0)
today_humidity.anchored_position = (118, 70)

today_wind = label.Label(terminalio.FONT, text="99m/s", color=0x000000)
today_wind.anchor_point = (0, 0)
today_wind.anchored_position = (150, 70)

today_pressure = label.Label(terminalio.FONT, text="99m/s", color=0x000000)
today_pressure.anchor_point = (0, 0)
today_pressure.anchored_position = (105, 94)

#today_uvi = label.Label(terminalio.FONT, text="100%", color=0x000000)
#today_uvi.anchor_point = (0, 0)
#today_uvi.anchored_position = (160, 94)

today_clouds = label.Label(terminalio.FONT, text="100", color=0x000000)
today_clouds.anchor_point = (0, 0)
today_clouds.anchored_position = (165, 50)

today_sunrise = label.Label(terminalio.FONT, text="12:12 PM", color=0x000000)
today_sunrise.anchor_point = (0, 0.5)
today_sunrise.anchored_position = (45, 120)

today_sunset = label.Label(terminalio.FONT, text="12:12 PM", color=0x000000)
today_sunset.anchor_point = (0, 0.5)
today_sunset.anchored_position = (130, 120)

today_banner = displayio.Group()
today_banner.append(today_date)
today_banner.append(city_name)
today_banner.append(today_icon)
today_banner.append(today_description)
today_banner.append(today_cur_temp)
today_banner.append(today_min_temp)
today_banner.append(today_max_temp)
today_banner.append(today_humidity)
today_banner.append(today_pressure)
#today_banner.append(today_uvi)
#today_banner.append(today_pop)
today_banner.append(today_clouds)
today_banner.append(today_wind)
today_banner.append(today_sunrise)
today_banner.append(today_sunset)

future_banners = [
    make_banner(x=203, y=18),
    make_banner(x=203, y=39),
    make_banner(x=203, y=60),
    make_banner(x=203, y=81),
    make_banner(x=203, y=102),
]

magtag.splash.append(today_banner)
for future_banner in future_banners:
    magtag.splash.append(future_banner)

# ===========
#  M A I N
# ===========
print("Fetching forecast...")
forecast_data, current, utc_time, local_tz_offset = get_forecast(latlon)

print("Updating...")
update_today(forecast_data[0], local_tz_offset)
update_now(current, local_tz_offset)
for day, forecast in enumerate(forecast_data[1:6]):
    update_banner(future_banners[day], forecast)

print("Refreshing...")
time.sleep(magtag.display.time_to_refresh + 1)
magtag.display.refresh()
time.sleep(magtag.display.time_to_refresh + 1)

print("Sleeping...")
go_to_sleep(utc_time + local_tz_offset)
#  entire code will run again after deep sleep cycle
#  similar to hitting the reset button