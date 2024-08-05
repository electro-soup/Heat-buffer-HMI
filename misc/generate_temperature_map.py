from PIL import Image, ImageOps



import numpy as np


def getHeatMapColor(value):

  NUM_COLORS = 4
  #color = [ [0,0,1], [0,1,0], [1,1,0], [1,0,0] ] # // A static array of 4 colors:  (blue,   green,  yellow,  red) using {r,g,b} for each.
  #make 7 colors
  NUM_COLORS = 7
  color = [[0,0,0] ,[0,0,1], [0,1,1], [0,1,0], [1,1,0], [1,0,0], [1,0.7,0.7] ]

  idx1 = 0      #  // |-- Our desired color will be between these two indexes in "color".
  idx2 = 0    #   // |
  fractBetween = 0 #  // Fraction between "idx1" and "idx2" where our value is.
  
  if value <= 0:
    idx1 = idx2 = 0    
  elif value >= 1:    idx1 = idx2 = NUM_COLORS-1
  else:  
    value = value * (NUM_COLORS-1);        # Will multiply value by 3.
    idx1  = np.floor(value);                  # Our desired color will be after this index.
    idx2  = idx1+1;                        # ... and before this index (inclusive).
    fractBetween = value - float(idx1);    # Distance between the two indexes (0-1).
    
  idx1 = int(idx1)
  idx2 = int(idx2)  

  red   = (color[idx2][0] - color[idx1][0])*fractBetween + color[idx1][0]
  green = (color[idx2][1] - color[idx1][1])*fractBetween + color[idx1][1]
  blue  = (color[idx2][2] - color[idx1][2])*fractBetween + color[idx1][2]
  #make it 255 from float
  
  red =int(red*255)
  blue = int(blue*255)
  green = int(green*255)
  
  return red, green, blue
import os
print(os.getcwd())

def getValueBetweenTwoFixedColors(value):

    aR = 0
    aG = 0
    aB = 255 #RGB for our 1st color (blue in this case).

    bR = 255
    bG = 0
    bB = 0 #RGB for our 2nd color (red in this case)

    red   = (bR - aR) * value + aR      # Evaluated as -255*value + 255.
    green = (bG - aG) * value + aG      # Evaluates as 0.
    blue  = (bB - aB) * value + aB      # Evaluates as 255*value + 0.

    return red, green, blue

lower_value_temp = 20
upper_value_temp = 90
i = 0
# top, right, bottom, left # na odwrut
border = (4,0,4,0)
color_offset = 10
for value in range(lower_value_temp, upper_value_temp+1):
    #red, green, blue = getValueBetweenTwoFixedColors((value-lower_value_temp)/(upper_value_temp-lower_value_temp))
    red, green, blue = getHeatMapColor((value-lower_value_temp+color_offset)/(upper_value_temp-lower_value_temp))
    img = Image.new('RGB', (159, 5), (int(red), int(green), int(blue)))
    new_img = ImageOps.expand(img, border=border, fill="black")
    new_img.save(f'testfolder/7colors/{i}_{value}C_image.png')
    i+=1

i = 0
#modified reduntand loop to do some lazy temp capping
for value in range(lower_value_temp, upper_value_temp+1):
    red, green, blue
    if value in range(20,30):
        red, green, blue = getValueBetweenTwoFixedColors(0) #make it just blue
    
    if value in range(30,80):
        red, green, blue = getValueBetweenTwoFixedColors((value-lower_value_temp-10)/(upper_value_temp-lower_value_temp-20)) #make it more 30-80 range
    
    if value in range(80, 91):
       red, green, blue = getValueBetweenTwoFixedColors(1) #max red
    img = Image.new('RGB', (143, 5), (int(red), int(green), int(blue)))
    
    new_img = ImageOps.expand(img, border=border, fill="black")
    new_img.save(f'testfolder/{i}_{value}C_image.png')
    i+=1


temperature_list = [84, 84, 85, 83, 82, 77, 65, 47, 29]

x = np.linspace(0,9,9)
print(x)

xvals = np.linspace(0,9,90)
yinterp =np.interp(xvals, x, temperature_list)


bufor_image = Image.new('RGB', (500, 90*10),"black")
iterator = 0
for value in yinterp:
    #red, green, blue = getValueBetweenTwoFixedColors((value-lower_value_temp)/(upper_value_temp-lower_value_temp))
    red, green, blue = getHeatMapColor((value-lower_value_temp)/(upper_value_temp-lower_value_temp))
    img = Image.new('RGB', (500, 10), (int(red), int(green), int(blue)))
    bufor_image.paste(img,(0,iterator*10))
    
    iterator+=1
print(iterator)
bufor_image.save(f'testfolder/0000image_interpolate3d.png')


#the same for up, there will be some code testinmg
from PIL import ImageDraw
i = 0
# top, right, bottom, left # na odwrut
image_to_color = Image.open("up.png")


width, height = image_to_color.size
center = (int(0.5 * width), int(0.5 * height))
ImageDraw.floodfill(image_to_color, xy=center, value = (255, 6,6, 255))


color_offset = 10
for value in range(lower_value_temp, upper_value_temp+1):
    #red, green, blue = getValueBetweenTwoFixedColors((value-lower_value_temp)/(upper_value_temp-lower_value_temp))
    red, green, blue = getHeatMapColor((value-lower_value_temp+color_offset)/(upper_value_temp-lower_value_temp))
    
    ImageDraw.floodfill(image_to_color, xy=center, value = (int(red), int(green),int(blue), 255))
    
    image_to_color.save(f'testfolder/up/{i}_{value}C_image.png')
    i+=1

i = 0
# top, right, bottom, left # na odwrut
image_to_color = Image.open("down.png")


width, height = image_to_color.size
center = (int(0.5 * width), int(0.5 * height))
ImageDraw.floodfill(image_to_color, xy=center, value = (255, 6,6, 255))


color_offset = 10
for value in range(lower_value_temp, upper_value_temp+1):
    #red, green, blue = getValueBetweenTwoFixedColors((value-lower_value_temp)/(upper_value_temp-lower_value_temp))
    red, green, blue = getHeatMapColor((value-lower_value_temp+color_offset)/(upper_value_temp-lower_value_temp))
    
    ImageDraw.floodfill(image_to_color, xy=center, value = (int(red), int(green),int(blue), 255))
    
    image_to_color.save(f'testfolder/down/{i}_{value}C_image.png')
    i+=1
