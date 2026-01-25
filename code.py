
import time
import terminalio
import displayio
import adafruit_imageload
from adafruit_display_text import label
from adafruit_magtag.magtag import MagTag
from secrets import secrets

# --| USER CONFIG |--------------------------
lat = secrets["openweather_location"][0]
lon = secrets["openweather_location"][1]
key = secrets["openweather_token"]

weather_url = "https://api.openweathermap.org/data/3.0/onecall?units=imperial&exclude=minutely,hourly,alerts&"
aqi_url = "https://api.openweathermap.org/data/2.5/air_pollution?"

# -------------------------------------------

# ----------------------------
# Define various assets
# ----------------------------
BACKGROUND_BMP = "/bmps/weather_bg.bmp"
ICONS_LARGE_FILE = "/bmps/weather_icons_70px.bmp"
ICONS_SMALL_FILE = "/bmps/weather_icons_20px.bmp"
ICON_MAP = ("01", "02", "03", "04", "09", "10", "11", "13", "50")
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
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

def make_banner(x=0, y=0):
    """Make a single future forecast info banner group."""
    day_of_week = label.Label(terminalio.FONT, text="DAY", color=0x000000)
    day_of_week.anchor_point = (0, 0.5)
    day_of_week.anchored_position = (0, 10)

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

def update_banner(banner, data):
    """Update supplied forecast banner with supplied data."""
    banner[0].text = DAYS[time.localtime(data["dt"]).tm_wday][:3].upper()
    banner[1][0] = ICON_MAP.index(data["weather"][0]["icon"][:2])
    banner[2].text = "{:3.0f}".format(data["temp"]["min"]) + "/" + "{:3.0f}".format(data["temp"]["max"])



def go_to_sleep(current_time):
    hour, minutes, seconds = time.localtime(current_time)[3:6]
    # if its after 10pm, sleep till 5 am.  if not, sleep for an hour
    if hour >21:
        seconds_to_sleep = (((24-hour)*3600)-(minutes*60) + (3600*5))
    else:
        seconds_to_sleep = 900

    print(
        "Sleeping for {} hours, {} minutes".format(
            seconds_to_sleep // 3600, (seconds_to_sleep // 60) % 60
        )
    )
    magtag.exit_and_deep_sleep(seconds_to_sleep)


def deg_to_cardinal(deg):
 directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
 # Normalize degrees to 0–360
 deg = deg % 360
 # Each sector is 45°, centered on the cardinal direction
 index = int((deg + 22.5) // 45) % 8
 return directions[index]

def aq_to_text(value):
    mapping = { 1: "GOOD",
                2: "FAIR",
                3: "MODR",
                4: "POOR",
                5: "VPRR",
                }
    return mapping.get(value, "UNKN")

def uv_to_text(uv):
    if uv < 0:
        return "UNKN"
    elif uv <= 2.9:
        return "LOW "
    elif uv <= 5.9:
        return "MODR"
    elif uv <= 7.9:
        return "HIGH"
    elif uv <= 10.9:
        return "VHI "   # “Very High”
    else:
        return "XTRM"   # “Extreme”


# ===========
# U I
# ===========

# time and date
curdt = label.Label(terminalio.FONT, text="time", color=0x000000)
curdt.anchor_point = (0, 0)
curdt.anchored_position = (15, 13)

curtim = label.Label(terminalio.FONT, text="?" * 30, color=0x000000)
curtim.anchor_point = (0, 0)
curtim.anchored_position = (15, 23)

# Weather Icon
curicon = displayio.TileGrid(
    icons_large_bmp,
    pixel_shader=icons_large_pal,
    x=10,
    y=34,
    width=1,
    height=1,
    tile_width=70,
    tile_height=70,
    )

curcond = label.Label(terminalio.FONT, text="Thunderstorm", color=0x000000)
curcond.anchor_point = (0.5,1)
curcond.anchored_position = (47,115)

# Top line - temp and feels
curtemp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
curtemp.anchor_point = (0, 0)
curtemp.anchored_position = (130, 21)

curfeels = label.Label(terminalio.FONT, text="+100F", color=0x000000)
curfeels.anchor_point = (0, 0)
curfeels.anchored_position = (160, 21)

# Second Line - Lo, Hi, Precip
daylo = label.Label(terminalio.FONT, text="+100F", color=0x000000)
daylo.anchor_point = (0, 0)
daylo.anchored_position = (100, 47)

dayhi = label.Label(terminalio.FONT, text="+100F", color=0x000000)
dayhi.anchor_point = (0, 0)
dayhi.anchored_position = (130, 47)

dayprecip = label.Label(terminalio.FONT, text="...", color=0x000000)
dayprecip.anchor_point = (0, 0)
dayprecip.anchored_position = (165, 47)

#Third LIne - Humidity, Wind/gust
curhumid = label.Label(terminalio.FONT, text="100%", color=0x000000)
curhumid.anchor_point = (0, 0)
curhumid.anchored_position = (110, 61)

curwindir = label.Label(terminalio.FONT, text="..", color=0x000000)
curwindir.anchor_point = (0, 0)
curwindir.anchored_position = (151, 61)

curwind = label.Label(terminalio.FONT, text="99m/s", color=0x000000)
curwind.anchor_point = (0, 0)
curwind.anchored_position = (155, 61)

curgust = label.Label(terminalio.FONT, text="99m/s", color=0x000000)
curgust.anchor_point = (0, 0)
curgust.anchored_position = (175, 61)

# 4th Line CC, Prs
curcloud = label.Label(terminalio.FONT, text="100", color=0x000000)
curcloud.anchor_point = (0, 0)
curcloud.anchored_position = (120, 75)

curprs = label.Label(terminalio.FONT, text="99m/s", color=0x000000)
curprs.anchor_point = (0, 0)
curprs.anchored_position = (165, 75)

# 5th line - UV, AQ, vis
curuv = label.Label(terminalio.FONT, text="100%", color=0x000000)
curuv.anchor_point = (0, 0)
curuv.anchored_position = (100, 95)

curaq = label.Label(terminalio.FONT, text="100%", color=0x000000)
curaq.anchor_point = (0, 0)
curaq.anchored_position = (137, 95)

curvis = label.Label(terminalio.FONT, text="100%", color=0x000000)
curvis.anchor_point = (0, 0)
curvis.anchored_position = (175, 95)

# Bottom - Sunrise, Sunset
sunrise = label.Label(terminalio.FONT, text="12:12 PM", color=0x000000)
sunrise.anchor_point = (0, 0.5)
sunrise.anchored_position = (45, 120)

sunset = label.Label(terminalio.FONT, text="12:12 PM", color=0x000000)
sunset.anchor_point = (0, 0.5)
sunset.anchored_position = (130, 120)

# Build Banner for screen
today_banner = displayio.Group()
today_banner.append(curdt)
today_banner.append(curtim)
today_banner.append(curicon)
today_banner.append(curcond)

# Top line
today_banner.append(curtemp)
today_banner.append(curfeels)

# 2nd line
today_banner.append(dayhi)
today_banner.append(daylo)
today_banner.append(dayprecip)

# 3rd line
today_banner.append(curhumid)
today_banner.append(curwindir)
today_banner.append(curwind)
today_banner.append(curgust)

# 4th line
today_banner.append(curvis)
today_banner.append(curcloud)
today_banner.append(curprs)

# 5th line
today_banner.append(curuv)
today_banner.append(curaq)

# Bottom
today_banner.append(sunrise)
today_banner.append(sunset)


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

#***** Pull in Weather and AQI Data
print("Fetching forecast from OWM")
final_url = weather_url + "appid=" + key + "&lat=" + lat + "&lon=" + lon
weather_data = magtag.network.fetch(final_url).json()
final_url = aqi_url + "appid=" + key + "&lat=" + lat + "&lon=" + lon
aqi_data = magtag.network.fetch(final_url).json()

#***** Setup buckets of data
print()
print("Setting up data buckets")
tzoffset = weather_data["timezone_offset"]
currentd = weather_data["current"]
utc_time = currentd["dt"]
todayd = weather_data["daily"][0]
forecast = weather_data["daily"][1:6]
if "alerts" in weather_data:
    alerts = weather_data["alerts"]
    print("ALERTS PRESENT")
else:
    alerts = None
    


print("Updating data labels")
date = time.localtime(utc_time + tzoffset)
sunr = time.localtime(currentd["sunrise"] + tzoffset)
suns = time.localtime(currentd["sunset"] + tzoffset)

curdt.text = "{} {} {}, {}".format(
        DAYS[date.tm_wday][:3],
        MONTHS[date.tm_mon - 1][:3],
        date.tm_mday,
        date.tm_year,
    )
curtim.text = "As of: {:d}:{:02d}".format(
        date.tm_hour,
        date.tm_min,
    )
curicon[0] = ICON_MAP.index(currentd["weather"][0]["icon"][:2])
curcond.text = currentd["weather"][0]["main"]

curtemp.text = "{:3.0f}".format(currentd["temp"])
curfeels.text = "{:3.0f}".format(currentd["feels_like"])

daylo.text = "{:3.0f}".format(todayd["temp"]["min"])
dayhi.text = "{:3.0f}".format(todayd["temp"]["max"])
dayprecip.text = "{:2.0f}%".format(todayd["pop"] * 100)

curhumid.text = "{:3d}%".format(currentd["humidity"])

windir = currentd["wind_deg"]
curwindir.text = deg_to_cardinal(windir)
curwind.text = "{:3.0f}/".format(currentd["wind_speed"])
curgust.text = "{:3.0f}".format(todayd["wind_gust"])

curvis.text = "{:2.1f}".format(currentd["visibility"] * 0.0006213712)
curcloud.text = "{:3d}%".format(currentd["clouds"])
curprs.text = "{:2.2f}".format(currentd["pressure"] * 0.02952998751)

uv = currentd["uvi"]
curuv.text = uv_to_text(uv)
aq = aqi_data["list"][0]["main"]["aqi"]
curaq.text = aq_to_text(aq)

sunrise.text = "{:2d}:{:02d} AM".format(sunr.tm_hour, sunr.tm_min)
sunset.text = "{:2d}:{:02d} PM".format(suns.tm_hour - 12, suns.tm_min)


for day, forecast in enumerate(forecast[0:5]):
    update_banner(future_banners[day], forecast)

print("Refreshing display")
time.sleep(magtag.display.time_to_refresh + 1)
magtag.display.refresh()
time.sleep(magtag.display.time_to_refresh + 1)

print("Sleeping...")
go_to_sleep(utc_time + tzoffset)
#  entire code will run again after deep sleep cycle
#  similar to hitting the reset button
