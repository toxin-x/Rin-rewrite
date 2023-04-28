FROM python:3.11.2-bullseye

# Or any preferred Python version.
ADD .. .
ENV DISCORD_TOKEN=
ENV DISCORD_COMMAND_PREFIX=
ENV TEST_ID=
ENV MADEON_ID=
ENV SPOTIPY_CLIENT_ID=
ENV SPOTIPY_CLIENT_SECRET=
ENV VERSION=
ENV OWNER_ID=
ENV BOT_ID=
ENV QUEUE_PAGE_LEN=5
RUN pip install discord python-dotenv spotipy
CMD python3 ./main.py
# Or enter the name of your unique directory and parameter set.