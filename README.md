# SBMagtag-Weather
My version of the Adafruit Magtag weather display.  This pulls from OpenWeatherMaps API for the latest forecast data and displays it on an epaper display on my fridge.  Its a work in progress thats for sure.  

I modified the original program to how it made sense for me, and added many sections to display more data.  The screen is pretty dense, as you can see below:
![Image of my magtag running.](https://github.com/sabarrett328/SBMagtag-Weather/blob/main/assets/images/20260127_005533682_iOS.jpg)
I changed the date and time around, added current and feel temperature, high and low, wind direction, speed and gust, cloud cover percent, pressure, UV, AQ and visibility, and added text describing the icon for the today forecast.  

The future now shows the icon as well as the low an high for the next 5 days. What I would like to explore next is to add an indicator that there is a weather alert somehow, and if a button is pressed on the Magtag, wake it up and display the text of the alert for 30 seconds, then bounce back to the forecast screen and go back to sleep.  Not sure how to do this yet.
