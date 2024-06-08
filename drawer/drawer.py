import PIL
from PIL import Image, ImageDraw, ImageFont
import textwrap

class TierlistImage:
    
    def draw_tier_list(self, user_data: dict, user_id: str):
        image = Image.open('../tierlist_template.png')
        image_font = ImageFont.truetype("arial.ttf", 50)
        draw = ImageDraw.Draw(image)
        areas = {"Rank S": [230,10,2385,174], "Rank A": [230,190,2385,354], "Rank B": [230,370,2385,534], "Rank C": [230,550,2385,714], "Rank D": [230,730,2385,894]}

        for rank, books in user_data.items():
            area = areas[rank]
            area_top = area[1]
            lines = ['']
            total_height = 0
            for novel in books:
                line = lines[-1] + " | " + novel if lines[-1] != '' else novel
                left, top, right, bottom = image_font.getbbox(line)
                textwidth = right - left
                textheight = bottom - top
                if textwidth >= (area[2] - area[0]):
                    if textheight + total_height > (area[3] - area[1]):
                        break
                    draw.text((area[0], area_top), lines[-1], font=image_font, fill="white")
                    area_top += textheight + 2  # Defines new starting point for the next line, with 2px padding
                    lines.append(novel)
                    total_height += textheight
                else:
                    if textheight + total_height > (area[3] - area[1]):
                        break
                    lines[-1] = line
                    if novel == books[-1]:
                        draw.text((area[0], area_top), lines[-1], font=image_font, fill="white")
                        area[1] += textheight + 2  # Update position for next line
                        total_height += textheight
                        break
        image.save(f"drawer/{user_id}_img.png")