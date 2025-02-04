from flask import Flask, render_template
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Google Sheets Authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("data-infinity-449901-a2-ea37c82dc115.json", scope)
client = gspread.authorize(creds)

# Open the Google Sheet
SHEET_ID = "1RfCLG-fjZY3VL1zJvwPbLcpWQGBzWRSWfzxf9bFTzF8"
sheet = client.open_by_key(SHEET_ID).sheet1  # First sheet

@app.route("/")
def index():
    # Fetch all rows (excluding headers)
    data = sheet.get_all_values()[1:]  # Skip the first row (headers)

    albums = []
    for row in data:
        album = {
            "name": row[0],
            "artist": row[1],
            # "cover": row[2],
            # "back_cover": row[3]
        }
        albums.append(album)
        
    print(albums)

    return render_template("alltime.html", albums=albums)

if __name__ == "__main__":
    app.run(debug=True)
    
    