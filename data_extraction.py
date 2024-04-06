import fitz
from PIL import Image, ImageEnhance, ImageFilter
import os
import pytesseract
import re
import json
import cv2
import numpy as np



def extract_information(text_all, text_corner, header_text,first_page,ps_text):
    info = { "unique_number": None,"Name":None, "Age": None, "Gender": None,"House_Number": None,
    "No_and_Name_of_Polling_Station":None,"Address_of_Polling_Station": None,
    "town_or_village": None,"Section_No_and_Name":None,"post_office": None,"pin_code":None, "mandal":None,"police_station":None,"revenue_division": None,"district":None,
    "Assembly_Constituency_No_and_Name":None,"PartNo": None,
    "Country":"India", "State":"Andhra Pradesh" 
    }
    head_patterns = {
    "Assembly_Constituency_No_and_Name": r'Assembly\s*Constituency\s*No\s*and\s*Name\s*:\s*(.*?)(?=\b(?:Part\s*No\.|Section\s*No\s*and\s*Name)|$)',
    "PartNo": r'Part\s*No\.(?:\s*:\s*|\s+)(.*?)(?=\b(?:Section\s*No\s*and\s*Name|$))',
    "Section_No_and_Name": r'Section\s*No\s*and\s*Name\s*(?:\s*:\s*|\s+)(.*?)(?=\b(?:Assembly\s*Constituency\s*No\s*and\s*Name|$))'
     }

    # Extract unique number from text_corner and clean it
    unique_number_match = re.search(r'(\b\w{6,12}\b)', text_corner)
    info["unique_number"] = re.sub(r'[^\w]', '', unique_number_match.group(1)) if unique_number_match else None

    patterns = {
    "town_or_village": r'Main\s*Town\s*or\s*Village\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s3]*([-\w\s,;:.!@#$%^&*()+={}[\]<>?/\\|`~]+?)(?=\b(?:Post\s*Office|Police\s*Station|Tehsil/Mandal|Revenue\s*Division|Mandal|District|Pin\s*code)|$)',
    "post_office": r'Post\s*Office\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s3]*([-\w\s,;:.!@#$%^&*()+={}[\]<>?/\\|`~]+?)(?=\b(?:Post\s*Office|Police\s*Station|Tehsil/Mandal|Revenue\s*Division|Mandal|District|Pin\s*code)|$)',
    "police_station": r'Police\s*Station\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s3]*([-\w\s,;:.!@#$%^&*()+={}[\]<>?/\\|`~]+?)(?=\b(?:Post\s*Office|Police\s*Station|Tehsil/Mandal|Revenue\s*Division|Mandal|District|Pin\s*code)|$)',
    "mandal": r'Mandal\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s3]*([-\w\s,;:.!@#$%^&*()+={}[\]<>?/\\|`~]+?)(?=\b(?:Post\s*Office|Police\s*Station|Tehsil/Mandal|Revenue\s*Division|Mandal|District|Pin\s*code)|$)',
    "revenue_division": r'Revenue\s*Division\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s3]*([-\w\s,;:.!@#$%^&*()+={}[\]<>?/\\|`~]+?)(?=\b(?:Post\s*Office|Police\s*Station|Tehsil/Mandal|Revenue\s*Division|Mandal|District|Pin\s*code)|$)',
    "district": r'District\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s3]*([-\w\s,;:.!@#$%^&*()+={}[\]<>?/\\|`~]+?)(?=\b(?:Post\s*Office|Police\s*Station|Tehsil/Mandal|Revenue\s*Division|Mandal|District|Pin\s*code)|$)'
    }


    # Define possible keys and corresponding regex patterns
    keys_and_patterns = {
    "Name": r'Name\s*[:~`!^&*(_\-+=\\|}\]{[;?/.>,<"#\$%\s]*([-\w\s,:;.!@#$%^&*()+={}[\]<>?/\\|`~]+?)(?=\b(?:Father Name|Fathers Name|Husband Name|Husbands Name|Mothers Name|Mother Name|Others|Other)\b|$)',
    "Father_Name": r'Father Name\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s]*([-\w\s,;:.!@#$%^&*()+={}[\]<>?/\\|`~]+?)(?=\b(?:House Number)\b|$)',
    "Fathers_Name": r'Fathers Name\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s]*([-\w\s,:;.!@#$%^&*()+={}[\]<>?/\\|`~]+?)(?=\b(?:House Number)\b|$)',
    "Husband_Name": r'Husband Name\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s]*([-\w\s,;:.!@#$%^&*()+={}[\]<>?/\\|`~]+?)(?=\b(?:House Number)\b|$)',
    "Husbands_Name": r'Husbands Name\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s]*([-\w\s,;:.!@#$%^&*()+={}[\]<>?/\\|`~]+?)(?=\b(?:House Number)\b|$)',
    "Mother_Name": r'Mother Name\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s]*([-\w\s,:;.!@#$%^&*()+={}[\]<>?/\\|`~]+?)(?=\b(?:House Number)\b|$)',
    "Mothers_Name": r'Mothers Name\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s]*([-\w\s,;:.!@#$%^&*()+={}[\]<>?/\\|`~]+?)(?=\b(?:House Number)\b|$)',
    "Others": r'Other(?:s\s)?[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s]*([-\w\s,;:.!@#$%^&*()+={}[\]<>?/\\|`~]+?)(?=\b(?:House Number)\b|$)',
    "House_Number": r'House Number\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s]*([\w\s\-\./]+?)(?=\b(?:Age|Gender|Aga|Ago)\b|$)',
    "Age": r'Age\s*[:~`!^&*(_\-+=\\|}\]{[;?/.>,<"#\$%§\s]*([\d]+|Gender)',
    "Gender": r'Gender\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s]*([\w\s\-\./]+)'
     }

    ps_patterns = {
    "No_and_Name_of_Polling_Station": r'No[.\s,]*and\s*Name\s*of\s*Polling\s*Station\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%§\s]*(.*?)(?=\b(?:Address\s*of\s*Polling\s*Station)|$)',
    "Address_of_Polling_Station": r'Address\s*of\s*Polling\s*Station\s*[:~`!^&*(_\-\=+\\|}\]{[;?/.>,<"#\$%\s]*(.*?)(?=\b(?:4,\s*NUMBER\s*OF\s*ELECTORS)|$)'
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, first_page)
        if match:
            value = match.group(1).strip()
            

            # Remove unnecessary signs
            value = re.sub(r'[^\w\s]', '', value).strip()

            info[key] = value.replace("\n"," ").replace("!","I")

    # Apply condition to pin_code separately
    pin_match = re.search(r"Pin\s*code\s*[=?+:]*\s*(\S+)", first_page)
    if pin_match:
        pin_digits = ''.join(filter(str.isdigit, pin_match.group(1)))[-3:]
        info["pin_code"] = "521" + pin_digits

    # Extract information using regex head_patterns

    for key, pattern in head_patterns.items():
        match = re.search(pattern, header_text, re.IGNORECASE | re.DOTALL)
        if match:
            info[key] = match.group(1).strip()
        else:
            info[key] = None

    for key, pattern in keys_and_patterns.items():
        match = re.search(pattern, text_all)
        if match:
            value = match.group(1).strip().replace('\n', ' ').replace("!","I").replace("|","I")
            info[key] = value if value else None
     
    for key, pattern in ps_patterns.items():
        match = re.search(pattern, ps_text, re.IGNORECASE | re.DOTALL)
        if match:
            info[key] = match.group(1).replace('\n', ' ').strip()
        else:
            info[key] = None

    return info

def crop_boxes_and_apply_ocr(pdf_folder, json_output_folder,text_output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(json_output_folder):
        os.makedirs(json_output_folder)
        os.makedirs(text_output_folder)

    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            # Construct paths
            pdf_path = os.path.join(pdf_folder, filename)
            
            # Load PDF using fitz
            doc = fitz.open(pdf_path)
            num_pages = len(doc)

            num_pages = doc.page_count
            num_rows, num_cols = 10, 3
            header_height = 1.0
            total_width, total_height = 20.99, 29.7
            top_margin, bottom_margin, left_margin, right_margin = 1, 1, 0.508, 0.508
            gap_size = 0.154
            first_top_margin, first_bottom_margin, first_left_margin, first_right_margin = 11, 11, 8.7, 0.1
            first_box_width, first_box_height = 11.5, 5.5
            ps_top_margin, ps_bottom_margin, ps_left_margin, ps_right_margin = 16.5, 6, 0.4, 8.1
            ps_box_width, ps_box_height = 8.4, 5.5

            # Convert dimensions to points (1 cm = 28.3465 points)
            total_width *= 28.3465
            total_height *= 28.3465
            top_margin *= 28.3465
            bottom_margin *= 28.3465
            left_margin *= 28.3465
            right_margin *= 28.3465
            gap_size *= 28.3465
            first_top_margin *= 28.3465
            first_bottom_margin *= 28.3465
            first_left_margin *= 28.3465
            first_right_margin *= 28.3465
            first_box_width    *= 28.3465
            first_box_height   *= 28.3465
            ps_top_margin *= 28.3465
            ps_bottom_margin *= 28.3465
            ps_left_margin *= 28.3465
            ps_right_margin *= 28.3465
            ps_box_width    *= 28.3465
            ps_box_height   *= 28.3465

            # first_page details box clip
            first_x1 = first_left_margin
            first_y1 = first_top_margin
            first_x2 = first_x1 + first_box_width
            first_y2 = first_y1 + first_box_height
            # polling sattion details box clip
            ps_x1 = ps_left_margin
            ps_y1 = ps_top_margin
            ps_x2 = ps_x1 + ps_box_width
            ps_y2 = ps_y1 + ps_box_height

            effective_width = total_width - left_margin - right_margin
            effective_height = total_height - top_margin - bottom_margin

            box_width = (effective_width - (num_cols - 1) * gap_size) / num_cols
            box_height = (effective_height - (num_rows - 1) * gap_size) / num_rows
            
            all_info = []
            all_text = ""
            
            page_num = 0
            pix = doc[page_num].get_pixmap(matrix=fitz.Matrix(2, 2), clip=(first_x1, first_y1, first_x2, first_y2))
            first_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Preprocess the top right corner image
            first_img_preprocessed = first_img.convert("L")  # Convert to grayscale
            first_img_preprocessed = first_img_preprocessed.filter(ImageFilter.UnsharpMask(radius=2, percent=175))  # Apply unsharp mask
            first_img_preprocessed = ImageEnhance.Contrast(first_img_preprocessed).enhance(2.2) 
            # Denoising
            first_img_preprocessed = cv2.fastNlMeansDenoising(np.array(first_img_preprocessed), None, h=10, templateWindowSize=7, searchWindowSize=21)

            # Apply OCR to the header
            first_page = pytesseract.image_to_string(first_img_preprocessed, config='--psm 6 --oem 3 -l eng')

            pix = doc[page_num].get_pixmap(matrix=fitz.Matrix(2, 2), clip=(ps_x1, ps_y1, ps_x2, ps_y2))
            ps_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            ps_img_preprocessed = ps_img.convert("L")  # Convert to grayscale
            ps_img_preprocessed = ps_img_preprocessed.filter(ImageFilter.UnsharpMask(radius=2, percent=175))  # Apply unsharp mask
            ps_img_preprocessed = ImageEnhance.Contrast(ps_img_preprocessed).enhance(2.2) 
            # Denoising
            ps_img_preprocessed = cv2.fastNlMeansDenoising(np.array(ps_img_preprocessed), None, h=10, templateWindowSize=7, searchWindowSize=21)

            # Apply OCR to the header
            ps_text = pytesseract.image_to_string(ps_img_preprocessed, config='--psm 6 --oem 3 -l eng')
            
            for page_num in range(2, num_pages - 1):
                
                # Crop header from the top of the page
                x1, y1, x2, y2 = 0, 0, doc[page_num].rect.width, header_height * 28.3465
                pix = doc[page_num].get_pixmap(matrix=fitz.Matrix(3, 3), clip=(x1, y1, x2, y2))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Preprocess the header image
                img_header_preprocessed = img.convert("L")  # Convert to grayscale
                img_header_preprocessed = img_header_preprocessed.filter(ImageFilter.UnsharpMask(radius=2, percent=175))  # Apply unsharp mask
                img_header_preprocessed = ImageEnhance.Contrast(img_header_preprocessed).enhance(2.2)  # Increase contrast
                # Denoising
                img_header_preprocessed = cv2.fastNlMeansDenoising(np.array(img_header_preprocessed), None, h=10, templateWindowSize=7, searchWindowSize=21)

                # Apply OCR to the header
                header_text = pytesseract.image_to_string(img_header_preprocessed, config='--psm 6 --oem 3 -l eng')
                
                for row in range(num_rows):
                    for col in range(num_cols):
                        x1 = left_margin + col * (box_width + gap_size)
                        y1 = top_margin + row * (box_height + gap_size)
                        x2 = x1 + box_width
                        y2 = y1 + box_height

                        pix = doc[page_num].get_pixmap(matrix=fitz.Matrix(3, 3), clip=(x1, y1, x2, y2))
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                        # Preprocess the top right corner image
                        img_preprocessed = img.convert("L")  # Convert to grayscale
                        img_preprocessed = img_preprocessed.filter(ImageFilter.UnsharpMask(radius=2, percent=175))  # Apply unsharp mask
                        img_preprocessed = ImageEnhance.Contrast(img_preprocessed).enhance(2.2)  # Increase contrast
                        # Denoising
                        img_preprocessed = cv2.fastNlMeansDenoising(np.array(img_preprocessed), None, h=10, templateWindowSize=7, searchWindowSize=21)
                        
                        text_all = pytesseract.image_to_string(img, config='--psm 6 --oem 3 -l eng')

                        x1_corner = x2 - box_width / 3
                        y1_corner = y1
                        x2_corner = x2
                        y2_corner = y1 + box_height / 4.2
                        pix_corner = doc[page_num].get_pixmap(matrix=fitz.Matrix(3, 3), clip=(x1_corner, y1_corner, x2_corner, y2_corner))
                        img_corner = Image.frombytes("RGB", [pix_corner.width, pix_corner.height], pix_corner.samples)

                        img_corner_preprocessed = img_corner.convert("L")
                        img_corner_preprocessed = img_corner_preprocessed.filter(ImageFilter.UnsharpMask(radius=2, percent=175))
                        img_corner_preprocessed = ImageEnhance.Contrast(img_corner_preprocessed).enhance(2.2)
                        # Denoising
                        img_corner_preprocessed = cv2.fastNlMeansDenoising(np.array(img_corner_preprocessed), None, h=10, templateWindowSize=7, searchWindowSize=21)
                        # Apply OCR to the top right corner
                        text_corner = pytesseract.image_to_string(img_corner_preprocessed, config='--psm 6 --oem 3 -l eng')
                        
                        text_all = text_all.replace("Photo", "").replace("Available", "")
                        text_corner = re.sub(r'[^a-zA-Z0-9\s]', '', text_corner)

                        info = extract_information(text_all , text_corner, header_text,first_page,ps_text)
                        all_info.append(info)
                        all_text += (text_all +"\n" + text_corner +"\n"+ header_text +"\n"+ first_page +"\n" + ps_text + "\n")

                    # Save the information in a JSON file
                    json_file_path = os.path.join(json_output_folder, f"{os.path.splitext(filename)[0]}.json")
                    with open(json_file_path, "w") as json_file:
                        json.dump(all_info, json_file, indent=4)

                    text_output_path = os.path.join(text_output_folder,  f"{os.path.splitext(filename)[0]}.txt")
                    with open(text_output_path, "w", encoding="utf-8") as text_file:  
                        text_file.write(all_text)

    print("All PDF files processed. Exiting.")
    return
 
if __name__ == "__main__":
    pdf_folder = r"C:\Users\lokes\Desktop\New 1-10 pdfs"
    json_output_folder = r"C:\Users\lokes\Desktop\all_voters_json_files"
    text_output_folder = r"C:\Users\lokes\Desktop\all_voters_text_files"
    crop_boxes_and_apply_ocr(pdf_folder, json_output_folder,text_output_folder)
      