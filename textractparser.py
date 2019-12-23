import boto3
import re
import pandas as pd

# Document
s3BucketName = "receiptscanclientimagepipeline"
documentName = "GroceryStoreReceipt.jpg"

W
# Amazon Textract client
textract = boto3.client('textract')

# Call Amazon Textract
response = textract.detect_document_text(
    Document={
        'S3Object': {
            'Bucket': s3BucketName,
            'Name': documentName
        }
    })

#print(response)


products=[]
for item in response["Blocks"]:
    if item["BlockType"] == "LINE":
        products.append(item["Text"])

items=[]
costs=[]
numberless=[]

# Get possible items and prices
for text in range(len(products)):
    try:
        if "$" in products[text+1]:
            items.append(products[text])
            items.append(products[text+1])
    except IndexError:
        pass
    
unique = []
[unique.append(x) for x in items if x not in unique]

items=[]
prices=[]
# Separate prices and possible items
for text in range(len(unique)):
    if unique[text][0]!="$":
        items.append(unique[text])
    else:
        prices.append(unique[text])
        
finalprod=[]
# Separate items from total, taxes, and credit cards
for product in items:
    try:
        int(product)
    except ValueError:
        if ("TOTAL") in product:
            pass
        elif "PURCHASE" in product:
            pass
        elif "TAX" in product:
            pass
        else:
            valuesearch=re.findall("\d+", product)
            allvalues=[int(valuesearch[i]) for i in range(len(valuesearch))]
            try:
                if max(allvalues) < 10000:
                    finalprod.append(product)
            except ValueError:
                finalprod.append(product)
            
single=[]

# Solve accidental price and item combination from Textract
for prod in finalprod:
    try:
        price=re.findall("\$\d+(?:\.\d+)?", prod)
        dollarvalue=price[0]
        finalvalue=float(dollarvalue.replace("$",""))
        item=prod.replace(dollarvalue, "")
        position=finalprod.index(prod)
        single.append(item)
        prices.insert(position, finalvalue)
    except IndexError:
        single.append(prod)

intcosts=[]
# Turn prices into floats
for entries in prices:
    try:
        errors=entries.replace(" ", "")
        price=re.findall("\$\d+(?:\.\d+)?", entries)
        dollarvalue=price[0]
        finalvalue=float(dollarvalue.replace("$",""))
        intcosts.append(finalvalue)
    except AttributeError:
        intcosts.append(entries)

# Check for if total value is included or multiple total values included
total=max(intcosts)
placement=intcosts.index(total)
intcosts.remove(total)
count=0
while max(intcosts)-1 < total and total < max(intcosts)+1:
    count=1
    currentmax=max(intcosts)
    intcosts.remove(currentmax)

if count==0:
    intcosts.insert(placement, total)

    
print(single)
print(intcosts)

# Next step, convert lists to dataframe and format the JSON
