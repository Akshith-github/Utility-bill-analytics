import easyocr as ocr
import streamlit as st  
from PIL import Image , ImageDraw
import numpy as np
import pymongo
from pymongo import MongoClient
# import re
import pandas as pd
# import as go from plotly
import plotly.express as px
import plotly.graph_objects as go
import json , os ,re
from datetime import datetime
from predictor import jsonPredictionFromImage
import random as rd
# functionality for combinations of items
from itertools import combinations
def tax_extract(text):
    a = re.findall(r'[\d\.]+',text)
    if a:
        return float("".join(a))
    else:
        return 0.0


@st.cache
def getjsonprediction(image):
    # st.write("Got",type(image))
    # convert numpy array to binary foramt data_bytes
    #unique name to save image in temp folder 
    # get random number to avoid name conflict
    image_name = 'temp/'+str(datetime.now())+str(rd.randint(1,1000000))+'.jpeg'
    image.save(image_name)
    prediction = jsonPredictionFromImage(imgfilename=image_name)
    # clear temp folder
    os.remove(image_name)
    return prediction

#mongodb+srv://achuth:<password>@cluster0.j1thl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority

st.set_page_config(layout='wide')
# float_cond lambda function to check given text is float or number or not
def float_cond(text):
    try:
        float(text)
        return True
    except ValueError:
        return False

@st.cache
def load_model(): 
    reader = ocr.Reader(['en'],model_storage_directory='.',cudnn_benchmark=True)
    return reader 
@st.cache
def draw_boxes(image, result, color='blue', width=2):
    draw = ImageDraw.Draw(image)
    for line in result:
        # print(line[0])
        # print("\n\n")
        p0, p1, p2, p3 = line[0]
        draw.line([*p0, *p1, *p2, *p3, *p0], fill=color, width=width)
    return image
@st.cache
def draw_boxes_v1(image, json_boundary_result, color='blue', width=2):
    draw = ImageDraw.Draw(image)
    # [{"text": "NICEk MART SUPER MARKET","boundingBox": [43,6,508,7,508,29,43,27],
    #   "words": [{"text": "NICE","boundingBox": [44, 6,117,6,117,28,43,27],"confidence": 0.986},{"text": "MART","boundingBox": [145,6,227,6,226,28,144,28],"confidence": 0.993},...]}]
    for line in json_boundary_result:
        # p0, p1, p2, p3 = line['boundingBox']
        draw.line(line['boundingBox'], fill=color, width=width)
    return image

@st.cache
def read_text_from_image(input_image):
    a = reader.readtext(input_image)
    print(*a,sep="\n")
    return a

@st.cache(allow_output_mutation=True)
def items_from_json(items_json_data):
    """ "Items": {"type": "array","valueArray": [
        *******************input**************************
    ]"""
    #json format is like this
    # [{"type":"object",
    #    "valueObject":
    #           {"Name":
    #               {"type":"string",
    #                 "valueString":".....",
    #                 "text":"....",
    #                  "boundingBox":[...]},
    #              "Price":{},"Quantity":{},
    #               "TotalPrice":{}}},
    #   {"type":"object",
    #       "valueObject":
    #              {"Name":{..},"Price":{..},"Quantity":{..},"TotalPrice":{..}}
    #  }]
    items = [];cols=[]
    for i,item in enumerate(items_json_data):
        item_dict = {}
        for key in item['valueObject']:
            if i == 0:
                cols.append(key)
            if item['valueObject'][key]['type'] == 'string':
                item_dict[key] = item['valueObject'][key]['valueString'] if item['valueObject'][key]['valueString'] else item['valueObject'][key]['text']
            elif item['valueObject'][key]['type'] == 'number':
                item_dict[key] = item['valueObject'][key]['valueNumber'] if item['valueObject'][key]['valueNumber'] else item['valueObject'][key]['text']
            else:
                item_dict[key] = item['valueObject'][key]['text']
        items.append(item_dict)
    return pd.DataFrame(pd.read_json(json.dumps(items))),cols



pages = ["DigitalizeBill","SavedBills","Dashboard"] #"HomePage",
page = st.sidebar.selectbox("Select Page",pages)

if page == "DigitalizeBill":
    menu_bars=["Easy Ocr","Google Tesseract","Info","About me"]
    choice = st.sidebar.selectbox("Select Menu",menu_bars)

    if choice == "Easy Ocr":
        st.title("Utility Bill Ananlysis")
        st.markdown("### - Using Easyocr")
        st.markdown("### by AA Studioz Team ")

        st.markdown("")
        image = st.file_uploader(label = "Upload your image here",type=['png','jpg','jpeg'])
        
        reader = load_model()

        
        if image is not None:

            input_image = Image.open(image) #read image
            copy_image = input_image.copy() #copy image

            with st.expander("Uploaded Image > OCR PART"):
                st.image(input_image) #display image
                with st.spinner("Processing ..."):
                    result = read_text_from_image(np.array(input_image))
                    # ([[289, 117], [373, 117], [373, 131], [289, 131]], 'Restauran', 0.9998766145792461) result item sample
                    result_text = [] 
                    for text in result:
                        result_text.append(text[1])
                    
                    boxed_img = draw_boxes(input_image,result)
                    st.image(boxed_img)
                    st.sidebar.image(boxed_img)
            st.write(result_text) 
            main_json={}
            # get json prediction from image
            with st.expander("Uploaded Image > JSON Prediction"):
                st.image(copy_image) #display image
                with st.spinner("Processing ..."):
                    json_prediction = getjsonprediction(copy_image)
                    st.image(draw_boxes_v1(copy_image,json_prediction['analyzeResult']['readResults'][0]['lines']))
                    st.write(json_prediction['analyzeResult']['documentResults'][0]['fields'])
                    main_json = json_prediction['analyzeResult']['documentResults'][0]['fields']
            # st.dataframe(items_from_json(main_json['Items']['valueArray'])[0])
            preddf,predcols=[],[]
            if "Items" in main_json:
                preddf,predcols = items_from_json(main_json['Items']['valueArray'])
                if "Name" in predcols:
                    predcols.remove("Name")
                st.dataframe(preddf)
                st.write(predcols)

            #Firstly get user to assign store details as of target_format.json file 
            #prompt user with text from result_text as suggestion 
            #{"store_name": "Lucky Restaurant", 
            # "store description": "Family Dinning", 
            # "bill_identifier": "CRN3/1/00000014", 
            # "bill_date": "03/Jul/2019", 
            # "bill_meta_data": {
            #     "store address": "Nagole, Hyderabad, Telangna, 500083", 
            #     "store_gstin": "xXXXXXXXXXXXXXX",
            #     "uid": "admin",
            #     "table_no": 24,
            #     "kot_no": 29.33
            # },   
            
            
            
            """### Store Details"""
            with st.expander("Store Details"):
                # Give options to user from result_text if no option in result_text then prompt user to enter manually
                store_name_choice = st.multiselect("Select Store Name",result_text+["Enter Manually"])
                merchant_name = main_json['MerchantName'] if 'MerchantName' in main_json else ""
                if merchant_name:
                    merchant_name = merchant_name['valueString'] if 'valueString' in merchant_name else merchant_name['text'] if 'text' in merchant_name else merchant_name
                if store_name_choice == ["Enter Manually"]:
                    store_name = st.text_input("Enter Store Name",merchant_name)
                elif not store_name_choice:
                    store_name = st.text_input("Enter Store Name",merchant_name)
                else:
                    #based on the user input create concated string of selected options and prompt in new text input box as user can correct it if any spelling mistake
                    store_name = " ".join(store_name)
                    store_name = st.text_input("Enter Store Name",store_name)

                # similarly for store description we need to first have selectbox followed by text input box
                store_description = st.multiselect("Select Store Description",result_text+["Enter Manually"])
                if store_description == ["Enter Manually"]:
                    store_description = st.text_input("Enter Store Description")
                else:
                    store_description = " ".join(store_description)
                    store_description = st.text_input("Enter Store Description",store_description)
                # similarly for store address we need to first have selectbox followed by text input box
                store_address_choice = st.multiselect("Select Store Address",result_text+["Enter Manually"])
                merchant_address = main_json['MerchantAddress'] if 'MerchantAddress' in main_json else ""
                if merchant_address:
                    merchant_address = merchant_address['valueString'] if 'valueString' in merchant_address else merchant_address['text'] if 'text' in merchant_address else merchant_address
                if store_address_choice == ["Enter Manually"]:
                    store_address = st.text_input("Enter Store Address")
                elif not store_address_choice:
                    store_address = st.text_input("Enter Store Address",merchant_address)
                else:
                    store_address = " ".join(store_address)
                    store_address = st.text_input("Enter Store Address",store_address)
                    
                # similarly for store gstin we need to first have selectbox followed by text input box
                store_gstin = st.multiselect("Select Store GSTIN",result_text+["Enter Manually"])
                if store_gstin == ["Enter Manually"]:
                    store_gstin = st.text_input("Enter Store GSTIN")
                else:
                    store_gstin = " ".join(store_gstin)
                    store_gstin = st.text_input("Enter Store GSTIN",store_gstin)
                # similarly for bill identifier we need to first have selectbox followed by text input box
                bill_identifier = st.multiselect("Select Bill Identifier",result_text+["Enter Manually"])
                if bill_identifier == ["Enter Manually"]:
                    bill_identifier = st.text_input("Enter Bill Identifier")
                else:
                    bill_identifier = " ".join(bill_identifier)
                    bill_identifier = st.text_input("Enter Bill Identifier",bill_identifier)
                # similarly for bill date we need to first have selectbox followed by text input box
                transaction_date = main_json['TransactionDate'] if 'TransactionDate' in main_json else ""
                # bill_date_choice = st.multiselect("Select Bill Date",result_text+["Enter Manually"])
                # if bill_date == ["Enter Manually"]:
                #     bill_date = st.text_input("Enter Bill Date")
                # else:
                #     bill_date = " ".join(bill_date)
                #     bill_date = st.text_input("Enter Bill Date",bill_date)
                identifiedDate=""
                if transaction_date:
                    #check valid date format and convert to date object 
                    # if valueDate is there in transaction_date then it is of foramt "2021-09-22", convert to date object
                    if 'valueDate' in transaction_date:
                        identifiedDate = datetime.strptime(transaction_date['valueDate'], '%Y-%m-%d')
                    # check all formats of date and convert to date object
                    # if date is not valid then prompt user to enter manually
                    else:
                        # FIND symbol in date string
                        # connectors = re.findall(r'[^\w]',transaction_date['text'])
                        #list out possible formats of date
                        formats = [
                            (d,m,y) for d in ["%d","%D"] for m in ["%b","%B","%m","%M"] for y in ["%y","%Y"]
                        ]
                        # make permutation of formats and check if date is valid
                        # formats_permt = [ connector.join(list(comb)) for comb in combinations(formats,3) for connector in ["-",'/',','] ]
                        formats_permt = [ " ".join(comb) for formati in formats for comb in combinations(formati,3) ]
                        # st.write(formats_permt)
                        # remove all symbols from transaction_date['text']
                        checkdate_text = " ".join(re.findall('\w+',transaction_date['text']))
                        # st.write(checkdate_text)
                        #check if date is in any of the formats
                        for format in formats_permt:
                            try:
                                # st.write(format)
                                identifiedDate = datetime.strptime(checkdate_text, format)
                                print("matched pattern {}".format(format))
                                break
                            except:
                                pass
                        if not identifiedDate:
                            transaction_date = transaction_date['valueDate'] if 'valueDate' in transaction_date else transaction_date['text']
                            bill_date_text = st.text_input("Enter Bill Date text correctly",transaction_date)
                            st.warning("Invalid Date Format Identified")               
                else:
                    st.error("Please enter valid date/Failed to find date")
                bill_date = st.date_input("Enter Bill Date",datetime.now() if not identifiedDate else identifiedDate)
                # similarly for uid we need to first have selectbox followed by text input box
                uid = st.multiselect("Select UID",result_text+["Enter Manually"])
                if uid == ["Enter Manually"]:
                    uid = st.text_input("Enter UID")
                else:
                    uid = " ".join(uid)
                    uid = st.text_input("Enter UID",uid)
                # similarly for table_no we need to first have selectbox followed by text input box
                table_no = st.multiselect("Select Table Number",result_text+["Enter Manually"])
                if table_no == ["Enter Manually"]:
                    table_no = st.text_input("Enter Table Number")
                else:
                    table_no = " ".join(table_no)
                    table_no = st.text_input("Enter Table Number",table_no)
                # similarly for kot_no we need to first have selectbox followed by text input box
                kot_no = st.multiselect("Select KAT Number",result_text+["Enter Manually"])
                if kot_no == ["Enter Manually"]:
                    kot_no = st.text_input("Enter KAT Number")
                else:
                    kot_no = " ".join(kot_no)
                    kot_no = st.text_input("Enter KAT Number",kot_no)
                
                bill_store_data = {"store_name": store_name,
                    "store description": store_description,
                    "bill_identifier": bill_identifier,
                    "bill_date": bill_date,
                    "store address": store_address,
                    "store_gstin": store_gstin,
                    "bill_meta_data": {
                        "uid": uid,
                        "table_no": table_no,
                        "kot_no": kot_no
                    }}
            st.write(bill_store_data)

            
            
            
            """### Process Extracted Text > Item Details"""
            # intially let us consider the text item in result text which has the text item and number item following it in the result text list.
            # check if main_json has Items

            
            
            with st.expander("Item Details"):
                assumed_title_input = ""
                while True and not assumed_title_input:
                    if len(result_text) == 0:
                        st.error("No text found in the image")
                        break
                    elif len(result_text) == 1:
                        st.success("Only one text found in the image")
                        break
                    else:
                        st.success("Multiple text found in the image")
                        # for loop will break when we identify the text item and number item in the result text list.
                        for i,item in enumerate(result_text):
                            if ( ( not float_cond(item.replace(',','.').replace(' ','')))
                                    and 
                                (not float_cond(result_text[i+1].replace(',','.').replace(' ','')))
                                    and
                                float_cond(result_text[i+2].replace(',','.').replace(' ',''))
                                ):
                                st.success("Assuming text following [{}] are related to items".format(item))
                                assumed_title_input = item
                                break
                        else:
                            st.error("Text preceding items list in bill is not identified")
                        break
                
                if assumed_title_input:
                    title_inp = st.selectbox('Items preceding text',result_text,index=result_text.index(assumed_title_input))
                else:
                    title_inp = st.text_input("Enter Items preceding text")
                st.write('Items preceding text is', title_inp)
                #check if title_inp is in result_text else make title_inp = title_inp[1:-1] and check
                try:
                    result_text.index(title_inp)
                    st.write('Items preceding text: [{}] is in result_text'.format(title_inp))
                except ValueError:
                    st.write('Items preceding text: [{}] is not in result_text'.format(title_inp) )
                    title_inp = title_inp[1:-1]
                    try:
                        result_text.index(title_inp)
                        st.write('Items preceding text: [{}] is in result_text'.format(title_inp))
                    except ValueError:
                        st.write('Items preceding text: [{}] is not in result_text'.format(title_inp))

                st.write('Items text :',result_text[result_text.index(title_inp)+1:])

                # check box input field in streamlit comma to decimal point
                comma_to_point = st.checkbox('Comma => point in text',True)
                if comma_to_point:
                    items_text = [float(i.replace(',','.').replace(' ','')) if float_cond(i.replace(',','.').replace(' ','')) else i for i in result_text[result_text.index(title_inp)+1:]]
                else:
                    items_text = [
                        float(i.replace(' ','')) if float_cond(i.replace(' ','')) else i 
                            for i in result_text[result_text.index(title_inp)+1:]    ]
                # st.write('Items text :',items_text)
                items_text= st.multiselect('UnSelect Invalid Items',items_text ,default=items_text)
                # get number of values exist for each items
                no_of_values = int(st.number_input('Number of values',value=len(predcols) if predcols else 1,min_value=1))
                st.write('Number of values :',no_of_values)

                # get name for each feature and store in a dictionary {feature_index:feature_name} format
                feature_name = {}
                for i in range(no_of_values):
                    feature_name[i] = st.text_input('Feature {} name'.format(i+1) ,'' if not predcols else predcols[i])
                st.write('Feature name :',feature_name)

                # get number of items
                no_of_items = int(st.number_input('Number of items',min_value=1,value=preddf.shape[0] if predcols else 1))
                st.write('Number of items :',no_of_items)


                # As per no_of_values given we need to map item to values 
                # if result_text=["a",1,1] if no_of_values=2 then result_text=[{"a":[1,1]}]
                # example : ["OMELETTE",850,"2 BOILED EGGS",1700,"2 OMELETTE","T700, 00","DIET COKE",260,"DIET COKE",260,"COKE ZERO", 260,"OMELETTE", 850,"FOOD", 5100,"AERATED BEVERAGE", 780, "CGST 9,0%", 529.2,"SGST 9.0%", 20.6938, "Total Due", 40529 ]

                # map_items_to_values
                def map_items_to_values(items,values,no_of_items_=no_of_items,no_of_values_=no_of_values):
                    items_dict = {}
                    for i in range(0,len(items),no_of_values_+1):
                        items_dict[items[i]] = values[i:i+no_of_values_]
                        no_of_items_ -= 1
                        if no_of_items_ == 0:
                            break
                    return items_dict
                
                # map_items_to_values
                items_dict = map_items_to_values(items_text,items_text[1:])
                st.write('Items text :',items_dict)
                
                
                # use streamlit columns to create an editable table to diplay the items items_dict
                # first column item names are editable
                # remaining column item values are editable
                # items_dict = {'a':[1,2,3],'b':[4,5,6]}
                # st.write(items_dict)
                # st.write(items_dict.keys())  are item names
                # st.write(items_dict.values()) are item values
                # no of cols = no_of_values+1
                # no of rows = items count
                items_ = list(items_dict.keys())
                items_count = len(items_)
                columns =  st.columns(no_of_values+1)
                items_values_dict = { i:items_dict[item].copy() for i,item in enumerate(items_)}

                for col_count,col in enumerate(columns):
                    if col_count == 0:
                        col.write("item name")
                        for i in range(items_count):
                            # col.write(items_[i])
                            items_[i]=col.text_input("item {} name".format(i+1),items_[i] if not predcols else preddf.iloc[i,0])
                    else:
                        #print feature_name
                        col.write(feature_name[col_count-1])
                        for i in range(items_count):
                            # col.write(items_dict[items_[i]][col_count-1] if items_dict[items_[i]] else '')
                            if not(len(items_values_dict[i])>col_count-1):
                                items_values_dict[i].append("")
                            items_values_dict[i][col_count-1]=col.text_input(
                                "item {} {}".format(i+1,feature_name[col_count-1]),
                                items_values_dict[i][col_count-1] if not predcols else preddf.iloc[i,col_count])
            # st.write(items_)
            # st.write(items_values_dict)
            items_df = pd.DataFrame.from_dict(
                [
                    {
                        "item_name":item_name,
                        **{feature_name[j]:float(items_values_dict[i][j]) for j in range(no_of_values)}}
                        for i,item_name in enumerate(items_)
                ])
                        
            # pie chart in streeamlit with item_dict values and keys as labels
            # st.write(list(items_dict.values()))
            st.write('Items text :',items_df)
            #print json format of dataframe items_df
            # required format is
            # {
            # "item 1":{"item_name":item_name,
            #           feature_name[0]":feature_value_0,
            #           feature_name[1]":feature_value_1,
            #           ....},
            # "item 2":{"item_name":item_name
            #           feature_name[0]":feature_value_0,
            #        feature_name[1]":feature_value_1,
            #       ....},
            # ....}
            items_json = {}
            for i in range(items_count):
                items_json["item_{}".format(i+1)] = {
                    "item_name":items_[i],
                    **{feature_name[j]:float(items_values_dict[i][j]) for j in range(no_of_values)}}
            st.write('Items json :',items_json)
            
            
            """### Subtotal """
            subtotal_value=0 if not "Subtotal" in main_json else main_json["Subtotal"]["valueNumber"] if "valueNumber" in main_json["Subtotal"] else tax_extract(main_json["Subtotal"]["text"])
            with st.expander("subtotal"):
                # user select one feature for subtotal
                lastcol = list(feature_name.values())[-1]
                subtotal_feature = st.multiselect('Select subtotal feature',list(feature_name.values()),default=lastcol if not predcols else predcols[-1] if items_df[lastcol].sum()==subtotal_value else [])
                # if user select more than 2 columns then show error
                if len(subtotal_feature)>2:
                    st.error('Please select only one feature for subtotal')
                else:
                    # if user select more than 1 column then multiply the values of column1 with column2 numpy array multiplication
                    if len(subtotal_feature)==2:
                        subtotal_value = np.multiply(items_df[subtotal_feature[0]].values,items_df[subtotal_feature[1]].values)
                        st.write('Subtotal feature :',subtotal_feature,subtotal_value)
                        subtotal_value = subtotal_value.sum()
                    elif len(subtotal_feature)==1:
                        subtotal_value = items_df[subtotal_feature[0]].sum()
                    else:
                        pass
                    st.write('Subtotal :',subtotal_value)
                    #take subtotal value input from user as confirmation, keep calculated value as default
            subtotal_value = st.number_input('Subtotal',subtotal_value)
            st.write('Subtotal :',subtotal_value)
            

            """### Taxes """
            #final Output
            #{   
            #     "type": "CGST",
            #     "rate": "2.5",
            #     "amount": "9.29"
            # },
            # {   
            #     "type": "86ST",
            #     "rate": "2.5",
            #     "amount": "9.29"
            # }
            # prompt user with three inputs tax type, rate and amount
            # In the loop while creating text_inputs check if Tax in main_json if present ,add intial one as i.e taxlist first element type=>total tax amount=>main_json["Tax"]["valueNumber"] else empty list
            tax_list = []
            with st.expander("taxes"):
                no_of_taxes = st.slider('No of taxes',1,10,1)
                taxlist=[{'type':'','rate':0.0,'amount':0.0} for i in range(no_of_taxes)]
                if "Tax" in main_json:
                    taxlist[0]['type'] = "TotalTax"
                    taxlist[0]['amount'] = main_json["Tax"]["valueNumber"] if "valueNumber" in main_json["Tax"] else tax_extract(main_json["Tax"]["text"])
                # with three columsn ask user to enter tax type, rate and amount for each tax
                tax_columns = st.columns(3)
                for i,tax in enumerate(taxlist):
                    tax_columns[0].write('Tax type')
                    tax['type'] = tax_columns[0].text_input('Tax type '+str(i),tax['type'])
                    tax_columns[1].write('Tax rate')
                    tax['rate'] = tax_columns[1].number_input('Tax rate '+str(i),tax['rate'],step=1.,format="%.2f")
                    tax_columns[2].write('Tax amount')
                    tax['amount'] = tax_columns[2].number_input('Tax amount '+str(i),tax['amount'],step=1.,format="%.2f")
                    tax_list.append(tax)
            st.write('Taxes :',tax_list)
            # calculate tax amount
            tax_amount = 0
            for tax in tax_list:
                tax_amount += tax['amount']
            st.write('Tax amount :',tax_amount)

            """### Total """
            # final Output
            # {
            #     "subtotal": "100",
            #     "taxes": [
            #         {
            #             "type": "CGST",
            #             "rate": "2.5",
            #             "amount": "9.29"
            #         },
            #         {
            #             "type": "86ST",
            #             "rate": "2.5",
            #             "amount": "9.29"
            #         }
            #     ],
            #     "total": "109.29"
            # }
            # prompt user with subtotal, tax amount and total amount
            total_columns = st.columns(3)
            total_columns[0].write('Subtotal')
            subtotal_value = total_columns[0].number_input('Sub total',subtotal_value)
            total_columns[1].write('Tax amount')
            tax_amount = total_columns[1].number_input('Tax amount',tax_amount)
            #check box in column 1 along with tax amount to get wether tax is inclusive or not
            tax_inclusive = total_columns[1].checkbox('Tax inclusive',False)
            if not tax_inclusive:
                total_amount = subtotal_value + tax_amount
            else:
                total_amount = subtotal_value
            total_columns[2].write('Total')
            # predicted Total  
            predTotal = 0
            if "Total" in main_json:
                predTotal = main_json["Total"]["valueNumber"] if "valueNumber" in main_json["Total"] else tax_extract(main_json["Total"]["text"])
            total_amount = total_columns[2].number_input('Total',total_amount if not predTotal else predTotal)
            st.write('Total :',total_amount)


                
            # Similar to taxes dict now bill meta dictionary
            # "bill_meta": { 
            #         "key_1": "valuexxx",
            #         "key_2": "valueXYY"
            #     }
            bill_meta = {}
            with st.expander("bill meta"):
                # slider to get number of key value pairs
                no_of_meta = st.slider('No of meta',1,10,1)
                # meta_columns = st.columns(2)
                for i in range(no_of_meta):
                    # meta_columns[0].write('Key')
                    key = "key_"+str(i)
                    # meta_columns[0].write(key)
                    # meta_columns[1].write('Value')
                    value = st.text_input('Value '+str(i),'')
                    bill_meta[key] = value
                st.write('Bill meta :',bill_meta)
            #finally show the output in json format
            #{
            #     "store_name": "Lucky Restaurant", 
            #     "store_description": "Family Dinning", 
            #     "store address": "Nagole, Hyderabad, Telangna, 500083", 
            #     "store_gstin": "xXXXXXXXXXXXXXX",
            #     "bill_identifier": "CRN3/1/00000014", 
            #     "bill_date": "03/Jul/2019", 
            #     "bill_meta_data": {
            #         "uid": "admin",
            #         "table_no": 24,
            #         "kot_no": 29.33
            #     },
            #     "bill_items": [
            #         {
            #             "item_name":"Crispy Chilli co", 
            #             "quantity": 1,
            #             "unit_price": 200.00, 
            #             "total_price": 200.00
            #         },
            #         {
            #             "item_name": "andori Murgh H",
            #             "quantity": 2, 
            #             "unit_price": 190.00,
            #             "total_price": 380.00
            #         }
            #     ],
            #     "sub_total": 580.007,
            #     "taxes": [
            #         {   
            #             "type": "CGST",
            #             "rate": "2.5",
            #             "amount": "9.29"
            #         },
            #         {   
            #             "type": "86ST",
            #             "rate": "2.5",
            #             "amount": "9.29"
            #         }
            #     ],
            #     "total_tax": "18.58",
            #     "total_paid": "390.00", 
            #     "bill_meta": { 
            #         "key_1": "valuexxx",
            #         "key_2": "valueXYY"
            #     }
            # } in this format

            with st.expander("finalize"):
                #create a dictionary to store all the values
                bill_dict = {}
                bill_dict['store_name'] = st.text_input('Store name',store_name)
                bill_dict['store_description'] = st.text_input('Store description',store_description)
                bill_dict['store_address'] = st.text_input('Store address',store_address)
                bill_dict['store_gstin'] = st.text_input('Store gstin',store_gstin)
                bill_dict['bill_identifier'] = st.text_input('Bill identifier',bill_identifier)
                bill_dict['bill_date'] = st.text_input('Bill date',bill_date)
                bill_dict['bill_meta_data'] = {}
                bill_dict['bill_meta_data']['uid'] = st.text_input('uid',uid)
                bill_dict['bill_meta_data']['table_no'] = st.text_input('Table no',table_no)
                bill_dict['bill_meta_data']['kot_no'] = st.text_input('Kot no',kot_no)
                bill_dict['bill_items'] = []
                st.write(items_df) 
                # with use of itemsdf and columns ask user to enter item name, quantity, unit price and total price
                item_columns = st.columns(len(items_df.columns))
                for i,item in enumerate(items_df.values):
                    item_dict = {}
                    # item_dict['item_name'] = item_columns[0].text_input('Item name '+str(i),item[0])
                    # instead of hardcoding the features as it use feature_name and iterate over it
                    for j,feature in enumerate(items_df.columns):
                        if feature == 'item_name':
                            item_dict['item_name'] = item_columns[j].text_input('Item name '+str(i),item[j])
                        else:
                            item_dict[feature] = item_columns[j].number_input(feature+' '+str(i+1),item[j])
                    bill_dict['bill_items'].append(item_dict)
                
                bill_dict['sub_total'] = subtotal_value
                bill_dict['taxes'] = []
                for i,tax in enumerate(tax_list):
                    bill_dict['taxes'].append({})
                    bill_dict['taxes'][i]['type'] = tax['type']
                    bill_dict['taxes'][i]['rate'] = tax['rate']
                    bill_dict['taxes'][i]['amount'] = tax['amount']
                bill_dict['total_tax'] = tax_amount
                bill_dict['total_paid'] = total_amount
                bill_dict['bill_meta'] = {}
                #with columsns of bill meta ask user to enter key and value
                # meta_columns = st.columns(2)
                for i in range(no_of_meta):
                    # key = meta_columns[0].text_input('Key '+str(i),)
                    key = 'key_'+str(i)
                    value = st.text_input('Value for key_'+str(i),bill_meta['key_'+str(i)])#meta_columns[1].text_input('Value '+str(i),'')
                    bill_dict['bill_meta'][key] = value
                # st.write('Bill meta :',bill_dict)

                # bill_dict['bill_meta']['key_1'] = st.text_input('Key 1',key_1)
                # bill_dict['bill_meta']['key_2'] = st.text_input('Key 2',key_2)
            st.write(bill_dict)
            # st.json(bill_dict)
            print(json.dumps(bill_dict))
            #st.write(json.dumps(bill_dict, indent=4))
            #st.write(json.dumps(bill_dict, indent=4, sort_keys=True))
            json_output = json.dumps(bill_dict)

            #client = pymongo.MongoClient("mongodb+srv://kluuser:<password>@cluster0.zjawa.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
            #db = client.test

            if st.button("add to database"):
                with st.spinner("Saving.."):
                    client = pymongo.MongoClient("mongodb+srv://kluuser:1234@cluster0.zjawa.mongodb.net/DB?retryWrites=true&w=majority")
                    database  = client["DB"]
                    collection = database["test"]
                    post1 = bill_dict
                    curr_saved = collection.insert_one(post1)
                    curr_saved_rec = collection.find({"_id":curr_saved.inserted_id})
                    records = [i for i in curr_saved_rec]
                    with st.expander("saved as"):
                        st.write(records)
                    st.success("Saved Successfully")

            #cluster = MongoClient("mongodb+srv://achuth:1234@cluster0.j1thl.mongodb.net/easyocr?ssl=true&ssl_cert_reqs=CERT_NONE")
            

            """### Plots"""
            # expander for plots 
            with st.expander("Plots"):
                # st.pyplot(items_df.plot(kind='bar',x='item_name',y=list(feature_name.values())).get_figure())
                # group bar chart  with plotly package
                fig=go.Figure(
                    data=[
                        go.Bar(x=items_,   y=items_df[feature_name[i]],    name=feature_name[i]) 
                                for i in range(no_of_values)
                                ]
                                )
                #bar graphs attached horizontally side by side edges
                fig.update_layout(barmode='group')
                st.plotly_chart(fig)

                for feature in feature_name.values():
                    # plot pie chart for th feature with plotly package
                    st.header(feature)
                    fig = go.Figure(data=[go.Pie(labels=items_, values=items_df[feature])])
                    st.plotly_chart(fig)

            # following the items information, there will be tax amounts and total amount which need to be extracted into taxes_dict and total_amount_var respectively.
            # example : ["CGST 9,0%", 529.2,"SGST 9.0%", 20.6938, "Total Due", 40529 ]
            # tax_amounts = [529.2,20.6938]
            # total_amount_var = 40529
            # tax_dict = {"CGST":529.2,"SGST":20.6938}
            # st.write('Taxes :',tax_dict)
            # st.write('Total amount :',total_amount_var)

            # get tax_amounts and total_amount_var
            tax_amounts = []
            total_amount_var = 0
            tax_dict = {}
            #this extraction is made with text that is after the items list in result_text
            # print last item in items_dict
            st.write('Last item in items_dict :',list(items_dict.keys())[-1])
            # print last item in items_dict to terminal console also
            print('Last item in items_dict :' ,list(items_dict.keys())[-1])
            # target test list is the list of elements in items_dict that are followed after the last item in items_dict
            target_test_list = items_text[items_text.index(list(items_dict.keys())[-1])+no_of_values+1:]
            # print target_test_list
            print('target_test_list :',target_test_list)
            # now in target_test_list we need to extract tax_amounts and total_amount_var from the list


            # get total amount
            # total_amount = items_dict.pop('TOTAL')
            # st.write('Total amount :',total_amount)




        # st.header('Pie chart')
        # for feature in range(no_of_values):
        #     st.subheader('Pie Chart for feature {} => {}'.format(feature+1, feature_name[feature]))
        #     fig = go.Figure(data=[go.Pie(labels=list(items_dict.keys()), 
        #         values=[i[feature] for i in list(items_dict.values())]
        #     )])
        #     st.plotly_chart(fig)

        else:
            st.write("Upload an Image")

    if choice == "Keras OCR":
        st.title("Utility Bill Analysis")
        st.markdown("### - Using Keras OCR")
        st.markdown("")
        image = st.file_uploader(label= "Upload your image here",type=['png','jpg','jpeg'])

    if choice == "Vision API":
        st.title("Utility Bill Analysis")
        st.markdown("### - Using Vision API")
        st.markdown("")
        image = st.file_uploader(label= "Upload your image here",type=['png','jpg','jpeg'])

    if choice == "OCR Space":
        st.title("Utility Bill Analysis")
        st.markdown("### - Using OCR Space")
        st.markdown("")
        image = st.file_uploader(label= "Upload your image here",type=['png','jpg','jpeg'])

    if choice == "Google Tesseract":
        st.title("Utility Bill Ananlysis")
        st.markdown("### - Using Google Tesseract")

        st.markdown("")
        image = st.file_uploader(label = "Upload your image here",type=['png','jpg','jpeg'])

if page == "SavedBills":
    st.title("=== Saved Bills ===")
    records=[]
    with st.spinner("Fetching data.."):
        client = pymongo.MongoClient("mongodb+srv://kluuser:1234@cluster0.zjawa.mongodb.net/DB?retryWrites=true&w=majority")
        database  = client["DB"]
        collection = database["test"]
        curr_saved_rec = collection.find()
        records = [i for i in curr_saved_rec]
        st.success("Fetched Successfully")
    # 5 text input boxes 1 button in 6 colmns to get input from user and filter the data
    filterform = st.form("Filters")
    filtercols = filterform.columns([2,2,2,2,2,2,1,1])
    ff_store_name = filtercols[0].text_input("Store Name")
    ff_bill_no = filtercols[1].text_input("Bill No")
    ff_bill_date = filtercols[2].date_input("Bill Date")
    ff_bill_amount = filtercols[3].number_input("Bill Amount")
    ff_no_of_items = filtercols[4].number_input("No of Items")
    filterby = filtercols[5].multiselect("Filter By",["Store Name","Bill No","Bill Date","Bill Amount","No of Items"])
    fflogic = filtercols[6].checkbox("uses OR instead of AND")
    filtercols[7].write("Apply")
    filterform_submit = filtercols[7].form_submit_button("Filter")
    if filterform_submit:
        # filter the data depending on the filterby
        if not fflogic:
            if "Store Name"  in filterby:
                records = [i for i in records if i['store_name'] == ff_store_name]
            if "Bill No"  in filterby:
                records = [i for i in records if i['bill_no'] == ff_bill_no]
            if "Bill Date"  in filterby:
                records = [i for i in records if i['bill_date'] == str(ff_bill_date)]
            if "Bill Amount"  in filterby:
                records = [i for i in records if i['bill_amount'] == bill_amount]
            if "No of Items"  in filterby:
                records = [i for i in records if len(i['bill_items']) == ff_no_of_items]
            if not filterby:
                records = records
        else:
            filtered_records = []
            if "Store Name"  in filterby:
                filtered_records.extend([i for i in records if i['store_name'] == ff_store_name])
            if "Bill No"  in filterby:
                filtered_records.extend([i for i in records if i['bill_no'] == ff_bill_no])
            if "Bill Date"  in filterby:
                filtered_records.extend([i for i in records if i['bill_date'] == str(ff_bill_date)])
            if "Bill Amount"  in filterby:
                filtered_records.extend([i for i in records if i['bill_amount'] == bill_amount])
            if "No of Items"  in filterby:
                filtered_records.extend([i for i in records if len(i['bill_items']) == ff_no_of_items])
            if not filterby:
                filtered_records = records
            # st.write(records)
            records = list(set(filtered_records))

                # i['bill_no'] == bill_no or i['bill_date'] == bill_date or i['bill_amount'] == bill_amount or i['bill_type'] == bill_type]
        # st.dataframe(pd.DataFrame(filtered_records))
    # st.form
    # column headings store_name,bill_no,bill_date,bill_amount,len(bill_items),total paid on expander
    headcols = st.columns([2,2,2,2,2,4])
    headcols[0].write("### Store Name")
    headcols[1].write("### Bill No")
    headcols[2].write("### Bill Date")
    headcols[3].write("### Bill Amount")
    headcols[4].write("### Items Count")
    headcols[5].write("### More information")
    rec_checkboxes=[]
    for no,i in enumerate(records):
        # display basic information :store name, bill no, bill date, bill amount,len(bill_items) on expander
        # i = 
        # {
        # "_id": "ObjectId('6190cbee3f5c7c56ba323b9f')",
        # "store_name": "",
        # "store_description": "",
        # "store_address": "",
        # "store_gstin": "",
        # "bill_identifier": "",
        # "bill_date": "2021-11-14",
        # "bill_meta_data": {
        #     "uid": "",
        #     "table_no": "",
        #     "kot_no": ""
        # },
        # "bill_items": [
        #     {
        #     "item_name": "1xT-Shirt",
        #     "": 525.5
        #     }
        # ],
        # "sub_total": 525.5,
        # "taxes": [
        #     {
        #     "type": "",
        #     "rate": 0,
        #     "amount": 0
        #     }
        # ],
        # "total_tax": 0,
        # "total_paid": 525.5,
        # "bill_meta": {
        #     "key_0": ""
        # }
        # }
        # use 6 columns and in each column display the following information
        # store_name,bill_no,bill_date,bill_amount,len(bill_items),total paid on expander
        # 6th column checkbox to display more information
        cols = st.columns([2,2,2,2,2,4])
        cols[0].write(i['store_name'])
        cols[1].write(i['bill_identifier'])
        cols[2].write(i['bill_date'])
        cols[3].write(i['total_paid'])
        cols[4].write(len(i['bill_items']))
        # rec_checkboxes.append(cols[5].checkbox("More Information "+str(no+1)))
        # if rec_checkboxes[no]:
        with cols[5].expander("More about Bill Item "+str(no+1)):
            st.write(i)

# cachefunction for  connection of pymongo/mongo db 
@st.cache
def get_mongo_db_collection(time=0):
    # mongodb connection
    client = pymongo.MongoClient("mongodb+srv://kluuser:1234@cluster0.zjawa.mongodb.net/DB?retryWrites=true&w=majority")
    database  = client["DB"]
    collection = database["test"]
    records = [i for i in collection.find()]
    for i in records:
        i['_id'] = str(i['_id'])
    #close client
    client.close()
    return records
time = 0
if page == "Dashboard":
    headercols = st.columns([6,2])
    headercols[0].write("### Welcome to the Dashboard")
    if headercols[1].button("Refresh for Newbills"):
        time +=1
    records = get_mongo_db_collection(time)
    
    st.markdown("--- \n ### Total No of records: {}".format(len(records)))
    # convert bills json format recoreds to pandas dataframe
    df = pd.DataFrame(records)
    # print datatypes of each column
    # st.write(str(df.dtypes))
    # st.write(df[df["_id"]=="61910cd4f7194e9b00a057b2"]["bill_items"].values[0])
    st.dataframe(df)
    # bill_date vs total paid plot
    # st.write(df.groupby(["bill_date"]).sum()["total_paid"].plot(kind="bar"))
    # st.pyplot()
    st.markdown("--- \n ### Timeline based analysis")
    headplotcols = st.columns(2)
    fig = go.Figure(data = [go.Scatter(x=df.groupby(["bill_date"]).count().index ,y=df.groupby(["bill_date"]).sum()["total_paid"])],layout=go.Layout(title="Bill Date vs Total Paid"))
    headplotcols[0].plotly_chart(fig)
    # bill_date vs bill_records_count plot x = bill_date, y = bill_records_count
    fig = go.Figure(data = [go.Scatter(x=df.groupby(["bill_date"]).count().index ,y=df.groupby(["bill_date"]).count()["_id"])],layout=go.Layout(title="Bill Date vs Bill Records Count"))
    headplotcols[1].plotly_chart(fig)



    latest_date = df['bill_date'].sort_values(ascending=True).tail(1)
    st.write("--- \n ### Latest Bill Date: {}".format(latest_date.values[0]))
    with st.expander("latest bill analysis"):
        st.table(df[df['bill_date']==latest_date.values[0]].tail(1))
        target_df = df[df['bill_date']==latest_date.values[0]].tail(1)
        # using json string stored in bill_items of target_df to convert to pandas dataframe
        # target_df['bill_items'] = target_df['bill_items'].apply(lambda x: pd.read_json(x))
        # st.write(target_df['bill_items'].values[0])
        #list of items in format [
        # 0:{
        # "item_name":"1xT-Shirt"
        # "":525.5
        # }
        # ]
        # to dataframe 
        target_df['bill_items'] = target_df['bill_items'].apply(lambda x: pd.DataFrame(x))
        # display with height=1000
        st.dataframe(target_df['bill_items'].values[0],height=1000)
        # st.write(pd.read_json(target_df['bill_items'].values[0]))
        st.write(df.shape)
        latest_items_df = target_df['bill_items'].values[0]
        # iter rows of dataframe and print dataframe of item_bills in each row
        # for i in df.itertuples():
            # st.dataframe(i.bill_items)

        # fig = go.Figure(data=[go.Pie(labels= latest_date, values=df[df['bill_date']==latest_date].values[])])
        # Using the latest_items_df to plot pie chart of items features
        plotcols = st.columns(2)
        for col in latest_items_df.columns:
            if col != "item_name":
                fig = go.Figure(data=[go.Pie(labels= latest_items_df[col].values, values=latest_items_df[col].values)])
                plotcols[0].plotly_chart(fig)
        # all cols group bar chart x = item_name y = all other columns except item_name
        fig = go.Figure(data=[go.Bar(x=latest_items_df['item_name'].values,y=latest_items_df.drop(columns=['item_name']).sum().values)])
        plotcols[1].plotly_chart(fig)
    st.write("--- \n ### Filter the bills and get plots")
    with st.expander("Filter the bills and get plots"):
        # As in savedbills page we have to give filter options to filter the records
        # use slider to filter the records with amount greater than x
        st.write(max(df['total_paid'].values),type(max(df['total_paid'].values)))
        amtfiltercols = st.columns(2)
        amount_slider = amtfiltercols[0].slider("Filter by Amount",0,int(max(df['total_paid'].values))+1,(0,int(max(df['total_paid'].values))+1))
        amtfiltercols[1].write(" apply ")
        amtfilter=amtfiltercols[1].checkbox("Filter by Amount")
        # cols3= st.columns(3)
        # cols3[0].dataframe(df['total_paid']>=amount_slider[0])
        # cols3[1].dataframe(df['total_paid']<=amount_slider[1])
        # cols3[2].dataframe(df['total_paid'])
        # st.write(df[df['total_paid']>=amount_slider[0]][df['total_paid']<=amount_slider[1]])
        result_df = df[(df['total_paid']>=amount_slider[0]) & (df['total_paid']<=amount_slider[1])] if amtfilter else df

        # similarly we can filter the records with bill_date greater than x get start data and end date
        st.write(df['bill_date'].min(),type(df['bill_date'].min()))
        datefiltercols = st.columns(3)
        start_date = datefiltercols[0].date_input("Start Date",datetime.strptime(df['bill_date'].min(),'%Y-%m-%d'))
        end_date = datefiltercols[1].date_input("End Date",datetime.strptime(df['bill_date'].max(),'%Y-%m-%d'))
        datefiltercols[2].write(" apply ")
        datefilter = datefiltercols[2].checkbox("Filter by Date")
        st.write(start_date,end_date)
        result_df = result_df[(result_df['bill_date']>=start_date) & (result_df['bill_date']<=end_date)] if datefilter else result_df

        # filter the total_tax greater than x and less than y
        taxfiltercols = st.columns(3)
        tax_slider = taxfiltercols[0].slider("Filter by Tax",0,int(max(result_df['total_tax'].values))+1,(0,int(max(result_df['total_tax'].values))+1))
        taxfiltercols[2].write(" apply ")
        taxfilter = taxfiltercols[2].checkbox("Filter by Tax")
        result_df = result_df[(result_df['total_tax']>=tax_slider[0]) & (result_df['total_tax']<=tax_slider[1])] if taxfilter else result_df

        # filter with regular expression string from user input on column name  is also from dropdown annd also have check box for exact case match
        regexfiltercols = st.columns(4)
        regex_string = regexfiltercols[0].text_input("Filter by Regex")
        case_flag = regexfiltercols[1].checkbox("Case Sensitive")
        regex_col = regexfiltercols[2].selectbox("Filter by Regex Column",df.columns)
        regexfiltercols[3].write(" apply ")
        regexfilter = regexfiltercols[3].checkbox("Filter by Regex")
        result_df = result_df[result_df[regex_col].str.contains(regex_string,case=case_flag)] if regexfilter else result_df
        # result_df = result_df[result_df[regex_col].str.contains(regex_string)] if regexfilter else result_df
        # with st.expander("Show Filtered Data"):
        st.table(result_df)

        # now on the the extracted result_df a custom plot ui with plolt user can select which type of plot to plot and also can filter the dataframe with the selected columns and decide the values to x column and y column or other based on the plot type
        #get plot type from user
        customplotcols = st.columns([1,2])
        plot_type = customplotcols[0].selectbox("Select Plot Type",["Scatter","Bar","Pie"])
        # get the columns from user
        # filter columns that are not suitable for plot based on dtype of column also include string columns
        eligible_cols = result_df.columns[result_df.dtypes.isin(['int64','float64','object'])]
        plot_cols = customplotcols[0].multiselect("Select Columns",result_df.columns)
        # get the x and y columns from user
        x_col = customplotcols[0].selectbox("Select X Column",plot_cols)
        y_col = customplotcols[0].selectbox("Select Y Column",plot_cols)
        # get the plot title from user
        plot_title = customplotcols[0].text_input("Plot Title","" if (x_col and y_col) else x_col+" vs "+y_col if (x_col!=y_col) else x_col)
        # get the plot description from user
        plot_desc = customplotcols[0].text_input("Plot Description")
        # Now we have to plot the dataframe based on the plot type
        customplotcols[1].write("--- \n plot is displayed here")
        if x_col and y_col:
            if plot_type == "Scatter":
                fig = go.Figure(data=[go.Scatter(x=result_df[x_col].values,y=result_df[y_col].values)])
                fig.update_layout(title=plot_title,xaxis_title=x_col,yaxis_title=y_col)
                customplotcols[1].plotly_chart(fig)
            elif plot_type == "Bar":
                fig = go.Figure(data=[go.Bar(x=result_df[x_col].values,y=result_df[y_col].values)])
                fig.update_layout(title=plot_title,xaxis_title=x_col,yaxis_title=y_col)
                customplotcols[1].plotly_chart(fig)
            elif plot_type == "Pie":
                fig = go.Figure(data=[go.Pie(labels=result_df[x_col].values,values=result_df[y_col].values)])
                fig.update_layout(title=plot_title,xaxis_title=x_col,yaxis_title=y_col)
                customplotcols[1].plotly_chart(fig)
            else:
                customplotcols[1].write("Invalid Plot Type")
        customplotcols[1].write("---")
    st.write("--- \n ### items data based plots")
    # generate items dataframe from the result_df and show the items in a dataframe extract it out of json format and show it in a dataframe
    with st.expander("Configure data frame column names for Better Analytics"):
        item_dfs=[]
        for i in range(len(result_df)):
            # print bill_items column
            item_bills = result_df.iloc[i]['bill_items']
            # [{"":null,"Amount":136,"Mrp":70,"Price":null,"Qty":2,"Rate":68,"item_name":"ID WHEAT CHAPATI"},{"":null,"Amount":103.5,"Mrp":105,"Price":null,"Qty":1,"Rate":103.51,"item_name":"PARACHUTE"},{"":null,"Amount":130,"Mrp":135,"Price":null,"Qty":1,"Rate":130,"item_name":"Tea"}]
            # or
            #[{"":null,"Amount":120,"Mrp":null,"Price":null,"Qty":null,"Rate":null,"item_name":"Chicken Burger"},{"":null,"Amount":280,"Mrp":null,"Price":null,"Qty":null,"Rate":null,"item_name":"Beer"}]
            # analyze json list and extract the items
            # for i in item_bills:
            #     st.write(i)
                # {
                # "item_name":"1xT-Shirt"
                # "":525.5
                # } to dataframe
            item_df = pd.DataFrame(item_bills)
            # append store details to each item row in the item_df
            # store_name, store_description, store_address, store_gstin, bill_identifier ,bill_date ,sub_total , total_tax,total_paid, bill_meta_data @ {
            #     "uid": "ADMIN",
            #     "table_no": "24",
            #     "kot_no": "28,33"
            # },
            column_names = item_df.columns
            # st.write(item_df.columns)
            cols = st.columns(len(column_names))
            column_names = [cols[col].text_input(column_names[col]+"label for"+str(i),column_names[col]) for col in range(len(column_names))]
            item_df.columns = column_names
            item_df['store_name'] = result_df.iloc[i]['store_name']
            item_df['store_description'] = result_df.iloc[i]['store_description']
            item_df['store_address'] = result_df.iloc[i]['store_address']
            item_df['store_gstin'] = result_df.iloc[i]['store_gstin']
            item_df['bill_identifier'] = result_df.iloc[i]['bill_identifier']
            item_df['bill_date'] = result_df.iloc[i]['bill_date']
            item_df['sub_total'] = result_df.iloc[i]['sub_total']
            item_df['total_tax'] = result_df.iloc[i]['total_tax']
            item_df['total_paid'] = result_df.iloc[i]['total_paid']
            item_df['bill_meta_data_uid'] = result_df.iloc[i]['bill_meta_data']['uid']
            item_df['bill_meta_data_table_no'] = result_df.iloc[i]['bill_meta_data']['table_no']
            item_df['bill_meta_data_kot_no'] = result_df.iloc[i]['bill_meta_data']['kot_no']
            # now show the item_df
            # st.table(item_df)
            # give column names in text input so user can rename them
            # each column name in one text input
            # show the item_df in a dataframe
            st.dataframe(item_df)
            # append the item_df to the list
            item_dfs.append(item_df)
    # if column names finalized(@ use checkbox) then the following code will run
    if st.checkbox("Finalize Column Names"):
        # concat item_dfs into one dataframe
        item_df = pd.concat(item_dfs)
        # show the item_df
        with st.expander("Show the Items dataframe"):
            st.dataframe(item_df)
        # st.table(item_df)
        st.write("--- \n ### items data based plots")
        # Now we have to plot the dataframe based on the plot type
        # inputs column to group by column to use for x axis and y axis
        groupby_col = st.selectbox("Select the column to group by",item_df.columns)
        # show the dataframe in after grouping
        with st.expander("Show the Items dataframe after grouping"):
            st.dataframe(item_df.groupby(groupby_col).agg(['sum','mean','max','min']))
        # inputs column to plot on x axis and y axis
        item_customplotcols = st.columns([2,3])
        item_customplotcols[0].write("---")
        x_col = item_customplotcols[0].selectbox("Select the column to plot on x axis",item_df.columns)
        y_col = item_customplotcols[0].selectbox("Select the column to plot on y axis",item_df.columns)
        # inputs plot type
        plot_type = item_customplotcols[0].selectbox("Select the plot type",["Bar","Line","Pie"])
        # inputs plot title
        plot_title = item_customplotcols[0].text_input("Enter the plot title")
        # now plot the dataframe
        item_customplotcols[1].write("Plot the Items dataframe")
        if plot_type == "Bar":
            fig = go.Figure(data=[go.Bar(x=item_df[x_col].values,y=item_df[y_col].values)])
            fig.update_layout(title=plot_title,xaxis_title=x_col,yaxis_title=y_col)
            item_customplotcols[1].plotly_chart(fig)
        elif plot_type == "Line":
            fig = go.Figure(data=[go.Scatter(x=item_df[x_col].values,y=item_df[y_col].values)])
            fig.update_layout(title=plot_title,xaxis_title=x_col,yaxis_title=y_col)
            item_customplotcols[1].plotly_chart(fig)
        elif plot_type == "Pie":
            fig = go.Figure(data=[go.Pie(labels=item_df[x_col].values,values=item_df[y_col].values)])
            fig.update_layout(title=plot_title,xaxis_title=x_col,yaxis_title=y_col)
            item_customplotcols[1].plotly_chart(fig)
        else:
            item_customplotcols[1].write("Invalid Plot Type")


    
    
    # word cloud of all items with item_name as text and total_paid as weight
    # use plotly package functions to create word cloud
    


    # with st.expander("## date vs bills"):
        
        




