from PIL import Image
import numpy as np

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

    for pixelPos in pixel_positions:
        pixel_val = stg_array[pixelPos]
        if (0 <= pixel_val <= 15) or (195 <= pixel_val <= 255):
            # Extract 4 LSBs
            lsb = format(pixel_val, '08b')[-4:]
            print(f"pixel_val: {pixel_val}, lsb: {lsb}, pixelPos: {pixelPos}")
        elif 32 <= pixel_val <= 191:
            # Extract 2 LSBs
            lsb = format(pixel_val, '08b')[-2:]
            print(f"pixel_val: {pixel_val}, lsb: {lsb}, pixelPos: {pixelPos}")
        else: # 16 - 31
            # Extract 3 LSBs
            lsb = format(pixel_val, '08b')[-3:]
            print(f"pixel_val: {pixel_val}, lsb: {lsb}, pixelPos: {pixelPos}")
        
        sdb.extend(lsb)
    
    print(len(sdb))
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
stegoImg = "img/res/6x6_stg.png"
resPath = "data/extract.txt"
oriImgPath = "img/ori/ext_ori_6x6.png"

#parse secret key
pixel_positions = parse_secret_key(secretKey)
print(f"len {len(pixel_positions)} pixel_positions: {pixel_positions}")
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
