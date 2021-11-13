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
import json
import datetime

st.set_page_config(layout='wide')
# float_cond lambda function to check given text is float or number or not
def float_cond(text):
    try:
        float(text)
        return True
    except ValueError:
        return False

menu_bars=["Easy Ocr","Keras OCR","Vision API","OCR Space","Google Tesseract","Info","About me"]
choice = st.sidebar.selectbox("Select Menu",menu_bars)


#mongodb+srv://achuth:<password>@cluster0.4xbkl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority
@st.cache
def load_model(): 
    reader = ocr.Reader(['en'],model_storage_directory='.',cudnn_benchmark=True)
    return reader 
@st.cache
def draw_boxes(image, result, color='blue', width=2):
            draw = ImageDraw.Draw(image)
            for line in result:
                p0, p1, p2, p3 = line[0]
                draw.line([*p0, *p1, *p2, *p3, *p0], fill=color, width=width)
            return image

@st.cache
def read_text_from_image(input_image):
    a = reader.readtext(np.array(input_image))
    print(*a,sep="\n")
    return a

if choice == "Easy Ocr":
    st.title("Utility Bill Ananlysis")
    st.markdown("### - Using Easyocr")
    st.markdown("### by Dintakurthi Achuth ")

    st.markdown("")
    image = st.file_uploader(label = "Upload your image here",type=['png','jpg','jpeg'])
    
    reader = load_model()

    
    if image is not None:

        input_image = Image.open(image) #read image

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
            store_name = st.multiselect("Select Store Name",result_text+["Enter Manually"])
            if store_name == ["Enter Manually"]:
                store_name = st.text_input("Enter Store Name")
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
            store_address = st.multiselect("Select Store Address",result_text+["Enter Manually"])
            if store_address == ["Enter Manually"]:
                store_address = st.text_input("Enter Store Address")
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
            bill_date = st.multiselect("Select Bill Date",result_text+["Enter Manually"])
            # if bill_date == ["Enter Manually"]:
            #     bill_date = st.text_input("Enter Bill Date")
            # else:
            #     bill_date = " ".join(bill_date)
            #     bill_date = st.text_input("Enter Bill Date",bill_date)
            bill_date = st.date_input("Enter Bill Date",datetime.datetime.now())
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
            no_of_values = int(st.number_input('Number of values',min_value=1))
            st.write('Number of values :',no_of_values)

            # get name for each feature and store in a dictionary {feature_index:feature_name} format
            feature_name = {}
            for i in range(no_of_values):
                feature_name[i] = st.text_input('Feature {} name'.format(i+1) ,'')
            st.write('Feature name :',feature_name)

            # get number of items
            no_of_items = int(st.number_input('Number of items',min_value=1))
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
                        items_[i]=col.text_input("item {} name".format(i+1),items_[i])
                else:
                    #print feature_name
                    col.write(feature_name[col_count-1])
                    for i in range(items_count):
                        # col.write(items_dict[items_[i]][col_count-1] if items_dict[items_[i]] else '')
                        if not(len(items_values_dict[i])>col_count-1):
                            items_values_dict[i].append("")
                        items_values_dict[i][col_count-1]=col.text_input(
                            "item {} {}".format(i+1,feature_name[col_count-1]),
                            items_values_dict[i][col_count-1])
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
        subtotal_value=0
        with st.expander("subtotal"):
            # user select one feature for subtotal
            subtotal_feature = st.multiselect('Select subtotal feature',list(feature_name.values()),default=list(feature_name.values())[-1])
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
        
        tax_list = []
        with st.expander("taxes"):
            no_of_taxes = st.slider('No of taxes',1,10,1)
            taxlist=[{'type':'','rate':0.0,'amount':0.0} for i in range(no_of_taxes)]
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
        total_amount = total_columns[2].number_input('Total',total_amount)
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

if choice == "Info":
    st.title("This is the Info page")
if choice == "About me":
    st.title("this is about page")




