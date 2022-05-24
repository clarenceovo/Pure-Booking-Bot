# Pure-Booking-Bot
This application aims to book Pure yoga class at 9am sharply to secure the yoga class seat for my girl friend :)

## User guideline


1. Fetch the repo 
2.  Fill in your credential in config/config.json
   
3. Install pip packages
   ```sh
   pip install -r requirements.txt
   ```
4. Set up the crontab (Linux) / Task Scheduler
   ```sh
   crontab -e 
   ```
   (macos/Linux) Paste the following command in the the terminal 
   ```sh
   # m h  dom mon dow   command
   0 9 * * * <the full path of your app.py>
   ```
