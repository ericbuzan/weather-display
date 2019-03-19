ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

# Copy data for add-on
COPY run.sh /
COPY weather.py /
COPY RobotoCondensed-Regular.ttf /
COPY Roboto-Regular.ttf /
COPY weathericons-regular-webfont.ttf /
COPY weather_demo.png /weather/

# Install requirements for add-on
RUN apk add build-base python3-dev jpeg-dev zlib-dev freetype-dev
RUN pip3 install requests pillow

# Python 3 HTTP Server serves the current working dir
# So let's set it to our add-on persistent data directory.
WORKDIR /weather

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]