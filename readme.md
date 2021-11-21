# Utility Bill Analytics
---
Automated Bill/Receipts Recognizer
--- 
1. Digitalize bills automatically (Uses Ml models predictions)
2. Generate reports/Bills
3. Dashboard and Database Features
---
## image upload
![image](https://user-images.githubusercontent.com/62134438/141650730-0aa0e733-f69a-468e-973d-fb8ff2f46d06.png)
## automated bill entites recogintion
![image](https://user-images.githubusercontent.com/62134438/142752206-d9dc9072-21ae-4130-a05a-6ca2fd8fa35f.png)
## database
![image](https://user-images.githubusercontent.com/62134438/142752302-3561c05b-66c1-4221-bac4-7bf88a64404d.png)
![image](https://user-images.githubusercontent.com/62134438/142752326-ec2c99c9-b3ac-474e-869a-d618e65cc120.png)
## dashborad
![image](https://user-images.githubusercontent.com/62134438/142752477-aaaa55a3-3125-472b-86a9-eeb3cf072842.png)
![image](https://user-images.githubusercontent.com/62134438/141650738-2f3efe4c-f49b-4a75-82fc-9a848dbe7cb8.png)
---
## Steps:
1. OCR to extract text from bill [ Output : raw text segments]  ✅
2. Convert Raw text segements into Structred Data  **json** using Machine learning models output   ✅
3. Store the JSON representation of the bill into a database  ✅
4. Analytics dashboard for stored data  ✅
---
##  Tools Used
1. Python
2. Streamlit
3. Pandas
4. Easyocr

---
## Usage:
    '''
    pip install -r requirements.txt
    streamlit run ocr.py
    '''
