from PIL import Image
import random #for creating secret key
import math
import numpy as np

interpolated_pixel = set()

def MNMI(imgPath, resPath): #modified neighbor mean interpolation
    #get size of original image
    ori_img = Image.open(imgPath).convert("L")
    ori_array = np.array(ori_img)
    widthOri, heightOri = ori_img.size

    widthCvr = 2 * widthOri - 1
    heightCvr = 2 * heightOri - 1

    enlarged_array = np.zeros((heightCvr, widthCvr), dtype=np.uint8)


    for i in range(heightOri):
        for j in range(widthOri):
            enlarged_array[2 * i, 2 * j] = ori_array[i, j]

    for i in range(heightCvr):
        for j in range(widthCvr):
            #implement the MNMI algorithm
            if i % 2 == 0 and j % 2 == 0 and j < widthCvr - 1:
                enlarged_array[i, j] = ori_array[i // 2, j // 2]
            elif i % 2 == 0 and j == widthCvr - 1:
                enlarged_array[i, j] = ori_array[i // 2, j // 2]
            elif j % 2 == 0 and i == widthCvr - 1:
                enlarged_array[i, j] = ori_array[i // 2, j // 2]
            
            elif i % 2 == 1 and j == widthCvr - 1:
                top = enlarged_array[i - 1, j] if i - 1 >= 0 else 0
                bottom = enlarged_array[i + 1, j] if i + 1 < heightCvr else 0
                top_left = enlarged_array[i - 1, j - 2] if (i - 1 >= 0 and j - 2 >= 0) else 0
                bottom_left = enlarged_array[i + 1, j - 2] if (i + 1 < heightCvr and j - 2 >= 0) else 0

                enlarged_array[i, j] = (2 * int(top) + 2 * int(bottom) + int(top_left) + int(bottom_left)) // 6
                interpolated_pixel.add((i, j))
            elif j % 2 == 1 and i == widthCvr - 1:
                left = enlarged_array[i, j - 1] if j - 1 >= 0 else 0
                right = enlarged_array[i, j + 1] if j + 1 < widthCvr else 0
                top_left = enlarged_array[i - 2, j - 1] if (i - 2 >= 0 and j - 1 >= 0) else 0
                top_right = enlarged_array[i - 2, j + 1] if (i - 2 >= 0 and j + 1 < widthCvr) else 0

                enlarged_array[i, j] = (2 * int(left) + 2 * int(right) + int(top_left) + int(top_right)) // 6
                interpolated_pixel.add((i, j))
            elif i % 2 == 0 and j % 2 == 1 and i < widthCvr - 1:
                left = enlarged_array[i, j - 1] if j - 1 >= 0 else 0
                right = enlarged_array[i, j + 1] if j + 1 < widthCvr else 0
                bottom_left = enlarged_array[i + 2, j - 1] if (i + 2 < heightCvr and j - 1 >= 0) else 0
                bottom_right = enlarged_array[i + 2, j + 1] if (i + 2 < heightCvr and j + 1 < widthCvr) else 0

                enlarged_array[i, j] = (2 * int(left) + 2 * int(right) + int(bottom_left) + int(bottom_right)) // 6
                interpolated_pixel.add((i, j))

            elif i % 2 == 1 and j % 2 == 0 and j < widthCvr - 1:
                top = enlarged_array[i - 1, j] if i - 1 >= 0 else 0
                bottom = enlarged_array[i + 1, j] if i + 1 < heightCvr else 0
                top_right = enlarged_array[i - 1, j + 2] if (i - 1 >= 0 and j + 2 <= widthCvr - 1) else 0
                bottom_right = enlarged_array[i + 1, j + 2] if (i + 1 < heightCvr and j + 2 < widthCvr) else 0

                enlarged_array[i, j] = (2 * int(top) + 2 * int(bottom) + int(top_right) + int(bottom_right)) // 6
                interpolated_pixel.add((i, j))
            else:
                top_left = enlarged_array[i - 1, j - 1] if (i - 1 >= 0 and j - 1 >= 0 ) else 0
                top_right = enlarged_array[i - 1, j + 1] if (i - 1 >= 0 and j + 1 < widthCvr) else 0
                bottom_left = enlarged_array[i + 1, j - 1] if (i + 1 < heightCvr and j - 1 >= 0) else 0
                bottom_right = enlarged_array[i + 1, j + 1] if (i + 1 < heightCvr and j + 1 < widthCvr) else 0

                enlarged_array[i, j] = (int(top_left) + int(top_right) + int(bottom_left) + int(bottom_right)) // 4
                interpolated_pixel.add((i, j))

    resImg = Image.fromarray(enlarged_array)

    resImg.save(resPath)

def secretKeyGeneration(pixel_positions):
    secret_key = ';'.join([f"{x},{y}" for x, y in pixel_positions]) #convert to string
    with open("./data/secret_key.txt", "w") as f:
        f.write(secret_key)

def secret_data_bits(secretDataPath):
    with open(secretDataPath, 'r') as secretDataFile:
        secretData = secretDataFile.read().strip()

    #remove spaaces
    secretDataBits = list(secretData.replace(" ", "").replace("\n", "").replace("\t", ""))
    return secretDataBits

def embedding(secretDataBits, pixel_positions, imgPath, resPath):

    # Convert pixel positions to list for indexing
    interpolated_pixel_position = list(pixel_positions)
    rand_pixel_positions = random.sample(interpolated_pixel_position, len(secretDataBits))
    choosen_pixel_positions = []
    
    # Open and convert image to numpy array
    img = Image.open(imgPath).convert("L")
    img_array = np.array(img)
    
    # Track current position in secret data
    data_index = 0
    data_len = len(secretDataBits)

    # Process each selected pixel
    with open("logEmbed.txt", "w") as log_file:
        for pos in rand_pixel_positions:
            if data_index >= data_len:
                break
                
            i, j = pos
            pixel_val = img_array[i, j]
            
            # Determine number of LSBs to replace based on pixel value
            if (0 <= pixel_val <= 15) or (192 <= pixel_val <= 255):
                num_bits = 4
            elif 32 <= pixel_val <= 191:
                num_bits = 2
            else:  # 16-31
                num_bits = 3
                
            # Calculate remaining bits and pad with zeros at start if needed
            remaining = data_len - data_index
            if remaining < num_bits:
                bits_to_embed = ['0'] * (num_bits - remaining) + secretDataBits[data_index:]
            else:
                bits_to_embed = secretDataBits[data_index:data_index + num_bits]
                
            # Convert pixel value to binary and keep MSBs
            bin_pixel = format(pixel_val, '08b')
            new_pixel = bin_pixel[:-num_bits] + ''.join(bits_to_embed)
            # print(F"BITS TO EMBED: {bits_to_embed}, pixel position: {pos}")
            
            # Update pixel value
            img_array[i, j] = int(new_pixel, 2)
            data_index += num_bits
            
            lsb_str = ''.join(bits_to_embed)
            log_file.write(f"pixel_val: {img_array[i, j]:<5} lsb: {lsb_str:<8} pixelPos: {pos}\n")
            # Save pixel position
            choosen_pixel_positions.append(pos)
    secretKeyGeneration(choosen_pixel_positions)
    # Save result image
    result_img = Image.fromarray(img_array)
    result_img.save(resPath)

def countMSE(stgImg, oriImg):
    stegoImage = Image.open(stgImg).convert("L")
    originalImage = Image.open(oriImg).convert("L")

    width, height = stegoImage.size
    MSE = 0
    for x in range(width):
        for y in range(height):
            MSE += (stegoImage.getpixel((x, y)) - originalImage.getpixel((x, y))) ** 2

    MSE /= (width * height)
    return MSE

def calculate_psnr(stgImg, oriImg):
    MSE = countMSE(stgImg, oriImg)
    PSNR = 10 * math.log10((255 ** 2) / MSE)
    return PSNR


data_path = "./data/data3kb.txt"
ori_img_path = "./img/ori/axial2.bmp"

#resPath
cvr_res_path = "./img/cvr/axial2_cvr.bmp"
stg_res_path = "./img/res/axial2_stg.bmp"

#interpolation
MNMI(ori_img_path, cvr_res_path)

#embedding
secretDataBits = secret_data_bits(data_path)
embedding(secretDataBits, interpolated_pixel, cvr_res_path, stg_res_path)  

# Calculate PSNR
print("PSNR:", calculate_psnr(cvr_res_path, stg_res_path))