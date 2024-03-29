# *************************************************************************
# *************************************************************************
# 
# SBMagtag Weather Station
# My version of the Adafruit Magtag weather program
# 
# I edited many items:
# 	My style is to only use functions when I see a way to reduce code length
#		All the routines here were just unnecessary in my opinion
#	I removed all the extra code for conditions that I wouldn't need
#	    when this runs in my house
#	I found some errors and corrected them
#	I changed to the onecall 3.0 api, and subscribed.  the first 1000 calls
#		are free, the cost is workable, and it accomodated the change of units
#	I added many data points and updated the screen background to accomodate the 
#		extra data
#	I added the aqi api data
#		
#
# *************************************************************************
# *************************************************************************

# ----------------------------
# Preliminary items to setup 
# ----------------------------

# --| Imports |--------------------------
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

# --| Define program assets |--------------------------
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
# --| Define the board |--------------------------
magtag = MagTag()

# --| Background bitmap |--------------------------
magtag.graphics.set_background(BACKGROUND_BMP)

# --| Sprint Sheets |--------------------------
icons_large_bmp, icons_large_pal = adafruit_imageload.load(ICONS_LARGE_FILE)
icons_small_bmp, icons_small_pal = adafruit_imageload.load(ICONS_SMALL_FILE)

# /////////////////////////////////////////////////////////////////////////


# =========================================================================
# Functions for implementation
# =========================================================================
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

# =========================================================================
# Define the user HMI elements for the screen
# =========================================================================
curdt = label.Label(terminalio.FONT, text="date", color=0x000000)
curdt.anchor_point = (0, 0)
curdt.anchored_position = (15, 14)

curtim = label.Label(terminalio.FONT, text="time" * 30, color=0x000000)
curtim.anchor_point = (0, 0)
curtim.anchored_position = (15, 24)

curtemp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
curtemp.anchor_point = (0, 0)
curtemp.anchored_position = (150, 21)

#curfeels = label.Label(terminalio.FONT, text="+100F", color=0x000000)
#curfeels.anchor_point = (0, 0)
#curfeels.anchored_position = (150, 21)

curprs = label.Label(terminalio.FONT, text="99.99", color=0x000000)
curprs.anchor_point = (0, 0)
curprs.anchored_position = (105, 94)

curwind = label.Label(terminalio.FONT, text="99m/s", color=0x000000)
curwind.anchor_point = (0, 0)
curwind.anchored_position = (150, 70)

#curgust = label.Label(terminalio.FONT, text="99m/s", color=0x000000)
#curgust.anchor_point = (0, 0)
#curgust.anchored_position = (150, 70)

curhumid = label.Label(terminalio.FONT, text="100%", color=0x000000)
curhumid.anchor_point = (0, 0)
curhumid.anchored_position = (118, 70)

curuv = label.Label(terminalio.FONT, text="100%", color=0x000000)
curuv.anchor_point = (0, 0)
curuv.anchored_position = (160, 94)

#curaq = label.Label(terminalio.FONT, text="1", color=0x000000)
#curaq.anchor_point = (0, 0)
#curaq.anchored_position = (160, 94)

curcloud = label.Label(terminalio.FONT, text="100", color=0x000000)
curcloud.anchor_point = (0, 0)
curcloud.anchored_position = (165, 50)

#curvis = label.Label(terminalio.FONT, text="100", color=0x000000)
#curvis.anchor_point = (0, 0)
#curvis.anchored_position = (165, 50)

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

sunrise = label.Label(terminalio.FONT, text="12:12 AM", color=0x000000)
sunrise.anchor_point = (0, 0.5)
sunrise.anchored_position = (45, 120)

sunset = label.Label(terminalio.FONT, text="12:12 PM", color=0x000000)
sunset.anchor_point = (0, 0.5)
sunset.anchored_position = (130, 120)
	
dayhi = label.Label(terminalio.FONT, text="+100F", color=0x000000)
dayhi.anchor_point = (0, 0)
dayhi.anchored_position = (130, 50)

daylo = label.Label(terminalio.FONT, text="+100F", color=0x000000)
daylo.anchor_point = (0, 0)
daylo.anchored_position = (100, 50)

dayprecip = label.Label(terminalio.FONT, text="...", color=0x000000)
dayprecip.anchor_point = (0, 0)
dayprecip.anchored_position = (165, 50)

today_banner = displayio.Group()
today_banner.append(curdt)
today_banner.append(curtim)
today_banner.append(curtemp)
#today_banner.append(curfeels)
today_banner.append(curprs)
today_banner.append(curwind)
#today_banner.append(curgust)
today_banner.append(curhumid)
today_banner.append(curuv)
#today_banner.append(curaq)
today_banner.append(curcloud)
#today_banner.append(curvis)
today_banner.append(curicon)
today_banner.append(curcond)
today_banner.append(sunrise)
today_banner.append(sunset)
today_banner.append(dayhi)
today_banner.append(daylo)
today_banner.append(dayprecip)

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

# =========================================================================
#  Main section of the program to fill in the data and update the display
# =========================================================================

#***** Pull in Weather and AQI Data
print("Fetching forecast from OWM")
final_url = weather_url + "appid=" + key + "&lat=" + lat + "&lon=" + lon
weather_data = magtag.network.fetch(final_url).json()
final_url = aqi_url + "appid=" + key + "&lat=" + lat + "&lon=" + lon
aqi_data = magtag.network.fetch(final_url).json()
print()

#***** Moving data to the right bucket to process
print("Moving data to buckets")
tzoffset = weather_data["timezone_offset"]
currentd = weather_data["current"] 
utc_time = currentd["dt"]
todayd = weather_data["daily"][0]
forecast = weather_data["daily"][1:6]

print("Updating data labels")
#***** Setting up the local time and date
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

#***** Fill in the data for current conditions
curtemp.text = "{:3.0f}".format(currentd["temp"])
#curfeels.text = "{:3.0f}".format(currentd["feels_like"])
curprs.text = "{:2.2f}".format(currentd["pressure"] * 0.02952998751)
curwind.text = "{:3.0f}/".format(currentd["wind_speed"])
#curgust.text = {:3.0f}/".format(currentd["wind_gust"])
curhumid.text = "{:3d}%".format(currentd["humidity"])
curuv.text = "{:3.0f}%".format(currentd["uvi"])
#curaq.text = aqi_data["list"][0]["main"]["aqi"]
curcloud.text = "{:3d}%".format(currentd["clouds"])
#curvis.text = "{:2.0f}/".format(currentd["visibility"])
curicon[0] = ICON_MAP.index(currentd["weather"][0]["icon"][:2])
curcond.text = currentd["weather"][0]["main"]
sunrise.text = "{:2d}:{:02d} AM".format(sunr.tm_hour, sunr.tm_min)
sunset.text = "{:2d}:{:02d} PM".format(suns.tm_hour - 12, suns.tm_min)
dayhi.text = "{:3.0f}".format(todayd["temp"]["max"])
daylo.text = "{:3.0f}".format(todayd["temp"]["min"])
dayprecip.text = "{:2.0f}%".format(todayd["pop"] * 100)

#***** Fill in the table for future forecast
for day, forecast in enumerate(forecast[0:5]):
    update_banner(future_banners[day], forecast)

print("Refreshing display")
time.sleep(magtag.display.time_to_refresh + 1)
magtag.display.refresh()
time.sleep(magtag.display.time_to_refresh + 1)

print("Sleeping...")
#  entire code will run again after deep sleep cycle
#  similar to hitting the reset button
hour, minutes, seconds = time.localtime(current_time)[3:6]
# if its after 10pm, sleep till 5 am.  if not, sleep for 15 mins
if hour >21:
        seconds_to_sleep = (((24-hour)*3600)-(minutes*60) + (3600*5))
    else:
        seconds_to_sleep = 60*15
    print(
        "Sleeping for {} hours, {} minutes".format(
            seconds_to_sleep // 3600, (seconds_to_sleep // 60) % 60
        )
    )
magtag.exit_and_deep_sleep(seconds_to_sleep)

# =========================================================================
# End of program
# =========================================================================
