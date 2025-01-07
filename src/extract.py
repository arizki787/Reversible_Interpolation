from PIL import Image
import numpy as np
import math

def parse_secret_key(secretKeyPath):
    f = open(secretKeyPath, "r")
    secretKey = f.read()
    f.close()
    #create a list of tuples from the secret key
    pixel_positions = [tuple(map(int, x.split(','))) for x in secretKey.split(';')]
    return pixel_positions

def extract_data(pixel_positions, stg_img):
    sdb = []
    stg_img = Image.open(stg_img).convert("L")
    stg_array = np.array(stg_img)
    with open("./logExtract.txt", "w") as f:
        for pixelPos in pixel_positions:
            pixel_val = stg_array[pixelPos]
            if (0 <= pixel_val <= 15) or (192 <= pixel_val <= 255):
                # Extract 4 LSBs
                lsb = format(pixel_val, '08b')[-4:]

            elif 32 <= pixel_val <= 191:
                # Extract 2 LSBs
                lsb = format(pixel_val, '08b')[-2:]

            else: # 16 - 31
                # Extract 3 LSBs
                lsb = format(pixel_val, '08b')[-3:]

            
            sdb.extend(lsb)
            f.write(f"pixel_val: {pixel_val:<5} lsb: {lsb:<8} pixelPos: {pixelPos}\n")
    return sdb

def extract_original_image(stg_img, ori_img_path):
    stg_img = Image.open(stg_img).convert("L")
    stg_array = np.array(stg_img)

    width_stg, height_stg = stg_img.size

    ori_array = np.zeros(((width_stg + 1) // 2, (height_stg + 1) // 2), dtype=np.uint8)

    for i in range(height_stg):
        for j in range(width_stg):
            if i % 2 == 0 and j % 2 == 0 and j < width_stg - 1:
                ori_array[i // 2, j // 2] = stg_array[i, j]
            elif i % 2 == 0 and j == width_stg - 1:
                ori_array[i // 2, j // 2] = stg_array[i, j]
            elif j % 2 == 0 and i == width_stg - 1:
                ori_array[i // 2, j // 2] = stg_array[i, j]

    oriImg = Image.fromarray(ori_array)
    oriImg.save(ori_img_path)

secretKey = "data/secret_key.txt"
stegoImg = "img/res/axial2_stg.bmp"
resPath = "data/extract.txt"
oriImgPath = "img/ori/extract_ori_axial2.bmp"

realImagePath = "img/ori/axial2.bmp"

#parse secret key
pixel_positions = parse_secret_key(secretKey)
#extract data
secretDataBits = extract_data(pixel_positions, stegoImg)
result = []
for i in range(0, len(secretDataBits), 8):
    result.append(''.join(map(str, secretDataBits[i:i + 8])))
res_string = ' '.join(result)
with open(resPath, "w") as f:
    f.write(res_string)

#get original image
extract_original_image(stegoImg, oriImgPath)
