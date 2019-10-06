from nredarwin.webservice import DarwinLdbSession
import threading
from datetime import datetime
from inky import InkyPHAT
from PIL import Image, ImageDraw, ImageFont
from font_source_serif_pro import SourceSerifPro
import re

inky_display = InkyPHAT("yellow")

font = ImageFont.truetype(SourceSerifPro, 10)

darwin_sesh = DarwinLdbSession(wsdl="https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx",
                               api_key="")
platforms = [
    {'platform': 1, 'service': None, 'dotCoordinates': [144, 42], 'textCoordinates': [0, 0]},
    {'platform': 2, 'service': None, 'dotCoordinates': [91, 42], 'textCoordinates': [106, 0]},
]


def main():
    img = Image.open("")
    display_image(img)
    check_trains()


def check_trains():
    global platforms
    img = Image.open("")
    draw = ImageDraw.Draw(img)
    has_changed = False
    arrivals = darwin_sesh.get_station_board('EMS', 5, True, True, None, None)

    # loop over platforms and remove any services that have departed
    for platform in platforms:
        if train_has_left_station(platform['service']):
            platform['service'] = None
            has_changed = True

    # loop over services and add any services that have arrived
    for service in arrivals.train_services:
        if train_is_at_station(service):
            platform_number = extract_platform_number(service.platform)
            platforms[platform_number - 1]['service'] = service
            has_changed = True

    if has_changed:
        for platform in platforms:
            service = platform['service']
            if service:
                text = service.sta + ' to ' + service.destinations[0].crs + ' from ' + service.origins[0].crs
                mark_train_on_map(platform, text, draw)
        display_image(img)
    threading.Timer(50.0, check_trains).start()
    return


def train_is_at_station(service):
    if not service:
        return False

    current_time = datetime.now().strftime('%H:%M')
    scheduled_arrival_time = str(service.sta)
    estimated_arrival_time = service.eta.lower()
    platform = service.platform and service.platform.lower()

    if not platform:
        return False
    elif ((estimated_arrival_time == 'on time' and scheduled_arrival_time == current_time)
            or estimated_arrival_time == current_time):
        return True
    else:
        return False


def train_has_left_station(service):
    if not service:
        # no service currently on the platform
        return False

    current_time = datetime.now().strftime('%H:%M')
    scheduled_depart_time = service.std
    estimated_depart_time = service.etd.lower()

    if ((estimated_depart_time == 'on time' and scheduled_depart_time < current_time)
            or (estimated_depart_time < current_time)):
        return True
    else:
        return False


def extract_platform_number(platform):
    return int(''.join(re.findall(r'\d+', platform)))


def mark_train_on_map(platform, text, drawRef):
    train_x, train_y = platform['dotCoordinates'][0], platform['dotCoordinates'][1]
    text_x, text_y = platform['textCoordinates'][0], platform['textCoordinates'][1]
    drawRef.pieslice([(train_x, train_y), (train_x + 15, train_y + 15)], 0, 360, fill=inky_display.YELLOW, outline=inky_display.YELLOW)
    drawRef.rectangle([(0, 0), (212, 12)], fill=inky_display.WHITE, outline=inky_display.WHITE)
    drawRef.text((text_x, text_y), text, inky_display.BLACK, font)


def display_image(img):
    inky_display.set_image(img)
    inky_display.set_border(inky_display.WHITE)
    inky_display.show()


if __name__ == "__main__":
    main()
