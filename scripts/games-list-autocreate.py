import requests
from PIL import Image, UnidentifiedImageError, ImageFile
from io import BytesIO
import sys

fileToWrite = sys.argv[1]


def findLowQualityIcons():
  missing_icons = []
  char_limit_icons = []
  timeout_icons = []
  SSL_error_icons = []
  unidentified_icons = []
  low_quality_icons = []
  non_square_icons = []
  other_errors = []

  games_list = requests.get("https://raw.githubusercontent.com/MrCoolAndroid/Xbox-Rich-Presence-Discord/refs/heads/main/Games%20List.json").json()

  for game in games_list["Games List"][0]["Games"]:
    try:
      icon = game["titleicon"]
    except KeyError:
      print(f"Game missing icon: {game['titlename']}")
      missing_icons.append(game["titlename"])
      continue
    if len(icon) >= 256:
      print(f"Icon url >= 256 characters for game: {game['titlename']}")
      char_limit_icons.append(game["titlename"])
    if icon.startswith("http"):
      try:
        response = requests.get(icon, headers={"User-Agent": "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)"})
      except requests.exceptions.ConnectTimeout:
        print(f"Timeout getting icon for game: {game['titlename']}")
        timeout_icons.append(game["titlename"])
        continue
      except requests.exceptions.SSLError:
        print(f"SSL error getting icon for game: {game['titlename']}")
        SSL_error_icons.append(game["titlename"])
        continue
      except Exception as exception:
        print(exception)
        print(f"\nError getting icon for game: {game['titlename']} with url: {icon}")
        other_errors.append(game["titlename"])
    try:
      image = Image.open(BytesIO(response.content))
    except UnidentifiedImageError:
      try:
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        image = Image.open(BytesIO(response.content))
      except UnidentifiedImageError:
        print(f"Error opening image for game: {game['titlename']}")
        unidentified_icons.append(game["titlename"])
        continue
      finally:
        ImageFile.LOAD_TRUNCATED_IMAGES = False
    except Exception as exception:
      print(exception)
      print(f"\nError opening image for game: {game['titlename']} with url: {icon}")
      other_errors.append(game["titlename"])
    width, height = image.size
    if width < 256 and height < 256:
      print(f"Low quality icon found for game: {game['titlename']}: {width}x{height}")
      low_quality_icons.append(game["titlename"])
    if width != height:
      print(f"non-square icon found for game: {game['titlename']}: {width}x{height}")
      non_square_icons.append(game["titlename"])

  games = ""
  for game in games_list["Games List"][0]["Games"]:
    if game["titlename"] in ["UpdateCheck", "BroadcastObj"]:
      continue
    status = "❌" if (
    game["titlename"] in missing_icons or
    game["titlename"] in char_limit_icons or
    game["titlename"] in timeout_icons or
    game["titlename"] in SSL_error_icons or
    game["titlename"] in unidentified_icons or 
    game["titlename"] in other_errors
    ) else "❓" if (
      game["titlename"] in low_quality_icons or
      game["titlename"] in non_square_icons      
    ) else "✔"
    games = games + f"| {game['titlename'].replace('\\', '\\\\').replace('|', '\\|').replace('*', '\\*').replace('_', '\\_').replace('~', '\\~').replace('`', '\\`').replace('#', '\\#')} | [Image link]({game['titleicon'].replace(' ', '%20')}) | {status} |\n"
  
  def key(line):
    if '❌' in line:
      return 0
    elif '❓' in line:
      return 1
    else:
      return 2
  
  sorted_lines = "\n".join(sorted(games.split("\n"), key=key))


  results=f"| Game Title | Link | Status |\n| --- | --- | --- |\n{sorted_lines}"
  
  with open(fileToWrite, "w", encoding="utf-8", newline="\n") as file:
    file.write(results)
    print("Results written to file")


findLowQualityIcons()
